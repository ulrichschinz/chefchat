#!/usr/bin/env python3
"""
Automated recipe tagging using AI to detect dietary properties
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database_sqlite import sqlite_db
from app.services.ai_service import ai_service
import json
import time

def analyze_recipe_dietary_properties(recipe):
    """Use AI to analyze a recipe and determine its dietary properties"""
    
    if not ai_service.enabled:
        print("❌ AI service not available for recipe analysis")
        return []
    
    # Format ingredients for analysis
    ingredients_text = "\n".join([
        f"- {ingredient.get('amount', '')} {ingredient.get('unit', '')} {ingredient.get('name', '')}"
        for ingredient in recipe.get('ingredients', [])
    ])
    
    prompt = f"""Analyze this recipe and determine its dietary properties. Look carefully at ALL ingredients and preparation methods.

Recipe: {recipe['name']}

Ingredients:
{ingredients_text}

Instructions:
{recipe.get('instructions', '')}

Please return a JSON object with the following structure:
{{
  "dietary_tags": ["vegetarian", "vegan", "gluten-free", "dairy-free", "quick", "easy"],
  "reasoning": "Brief explanation of why these tags apply",
  "certainty": "high|medium|low"
}}

Dietary definitions:
- vegetarian: No meat, poultry, or fish (but may contain dairy, eggs)
- vegan: No animal products at all (no meat, dairy, eggs, honey, etc.)
- gluten-free: No wheat, barley, rye, or gluten-containing ingredients
- dairy-free: No milk, cheese, butter, cream, yogurt, etc.
- quick: Cooking time under 30 minutes or very simple preparation
- easy: Simple preparation, few steps, basic cooking techniques

Be very careful with German ingredients:
- Hackfleisch = ground meat (NOT vegetarian)
- Schinken = ham (NOT vegetarian)
- Speck = bacon (NOT vegetarian)
- Hähnchen/Huhn = chicken (NOT vegetarian)
- Pute = turkey (NOT vegetarian)
- Schwein = pork (NOT vegetarian)
- Rind = beef (NOT vegetarian)
- Käse = cheese (vegetarian but NOT vegan)
- Milch = milk (vegetarian but NOT vegan)
- Butter = butter (vegetarian but NOT vegan)
- Sahne = cream (vegetarian but NOT vegan)
- Ei/Eier = eggs (vegetarian but NOT vegan)

Only include tags you are confident about. If uncertain, exclude the tag."""

    try:
        message = ai_service.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=800,
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        response_text = message.content[0].text
        
        # Try to extract JSON from the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            result = json.loads(json_str)
            return result.get('dietary_tags', []), result.get('reasoning', ''), result.get('certainty', 'medium')
            
        except (ValueError, json.JSONDecodeError) as e:
            print(f"   ❌ JSON parsing error for {recipe['name']}: {e}")
            print(f"   Raw response: {response_text[:200]}...")
            return [], "", "low"
            
    except Exception as e:
        print(f"   ❌ AI analysis error for {recipe['name']}: {e}")
        return [], "", "low"

def auto_tag_all_recipes():
    """Automatically tag all recipes with dietary properties"""
    print("🔄 Starting automated recipe tagging...")
    
    if not ai_service.enabled:
        print("❌ AI service not available. Please check your ANTHROPIC_API_KEY.")
        return False
    
    # Get all recipes
    recipes = sqlite_db.get_all_recipes()
    print(f"📋 Found {len(recipes)} recipes to analyze")
    
    updated_count = 0
    
    for i, recipe in enumerate(recipes, 1):
        print(f"\n📊 Analyzing recipe {i}/{len(recipes)}: {recipe['name']}")
        
        # Skip if recipe already has comprehensive tags
        existing_tags = recipe.get('tags', [])
        dietary_tags = [tag for tag in existing_tags if tag in ['vegetarian', 'vegan', 'gluten-free', 'dairy-free']]
        
        if len(dietary_tags) >= 1:
            print(f"   ⏭️  Already has dietary tags: {dietary_tags}")
            continue
        
        # Analyze with AI
        new_tags, reasoning, certainty = analyze_recipe_dietary_properties(recipe)
        
        if new_tags:
            # Merge with existing tags, avoiding duplicates
            all_tags = list(set(existing_tags + new_tags))
            
            # Update recipe in database
            try:
                updated_recipe = sqlite_db.update_recipe(recipe['id'], {'tags': all_tags})
                if updated_recipe:
                    print(f"   ✅ Added tags: {new_tags} (certainty: {certainty})")
                    print(f"   💭 Reasoning: {reasoning}")
                    updated_count += 1
                else:
                    print(f"   ❌ Failed to update recipe in database")
            except Exception as e:
                print(f"   ❌ Database update error: {e}")
        else:
            print(f"   ⚠️  No dietary tags detected")
        
        # Small delay to avoid overwhelming the API
        if i < len(recipes):
            time.sleep(1)
    
    print(f"\n✅ Recipe tagging completed!")
    print(f"📊 Updated {updated_count} out of {len(recipes)} recipes")
    
    # Show summary of tags
    print(f"\n📈 Summary of dietary tags:")
    updated_recipes = sqlite_db.get_all_recipes()
    
    tag_counts = {}
    for recipe in updated_recipes:
        for tag in recipe.get('tags', []):
            if tag in ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'quick', 'easy']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    for tag, count in sorted(tag_counts.items()):
        print(f"   - {tag}: {count} recipes")
    
    return True

def manual_tag_recipe(recipe_id: int, tags: list):
    """Manually add tags to a specific recipe"""
    recipe = sqlite_db.get_recipe(recipe_id)
    if not recipe:
        print(f"❌ Recipe with ID {recipe_id} not found")
        return False
    
    existing_tags = recipe.get('tags', [])
    all_tags = list(set(existing_tags + tags))
    
    updated_recipe = sqlite_db.update_recipe(recipe_id, {'tags': all_tags})
    if updated_recipe:
        print(f"✅ Added tags {tags} to recipe: {recipe['name']}")
        return True
    else:
        print(f"❌ Failed to update recipe")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatically tag recipes with dietary properties")
    parser.add_argument("--manual", "-m", type=int, metavar="RECIPE_ID", 
                       help="Manually tag a specific recipe by ID")
    parser.add_argument("--tags", "-t", nargs="+", 
                       help="Tags to add (for manual mode)")
    
    args = parser.parse_args()
    
    if args.manual:
        if not args.tags:
            print("❌ Please specify tags with --tags when using manual mode")
            sys.exit(1)
        success = manual_tag_recipe(args.manual, args.tags)
        sys.exit(0 if success else 1)
    else:
        success = auto_tag_all_recipes()
        sys.exit(0 if success else 1)