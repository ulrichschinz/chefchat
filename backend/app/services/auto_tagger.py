"""
Automatic recipe tagging service using AI analysis
"""

import json
from typing import List, Tuple
from app.services.ai_service import ai_service

class AutoTagger:
    def __init__(self):
        self.enabled = ai_service.enabled
    
    def analyze_recipe_dietary_properties(self, recipe: dict) -> Tuple[List[str], str, str]:
        """
        Use AI to analyze a recipe and determine its dietary properties
        
        Returns:
            tuple: (tags, reasoning, certainty)
        """
        
        if not self.enabled:
            return [], "AI service not available", "low"
        
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
- Fisch = fish (NOT vegetarian, but some consider pescatarian)
- Lachs = salmon (NOT vegetarian)
- Thunfisch = tuna (NOT vegetarian)

Only include tags you are confident about. If uncertain, exclude the tag.
Focus on the most important dietary restrictions first (vegetarian, vegan).
"""

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
                return (
                    result.get('dietary_tags', []), 
                    result.get('reasoning', ''), 
                    result.get('certainty', 'medium')
                )
                
            except (ValueError, json.JSONDecodeError) as e:
                print(f"JSON parsing error for {recipe['name']}: {e}")
                return [], "JSON parsing failed", "low"
                
        except Exception as e:
            print(f"AI analysis error for {recipe['name']}: {e}")
            return [], f"AI error: {str(e)}", "low"
    
    def auto_tag_recipe(self, recipe: dict) -> dict:
        """
        Automatically add AI-generated tags to a recipe
        
        Args:
            recipe: Recipe dictionary
            
        Returns:
            dict: Recipe with updated tags
        """
        if not self.enabled:
            # If AI is not available, return recipe unchanged
            return recipe
        
        # Get existing tags
        existing_tags = recipe.get('tags', [])
        
        # Check if we already have dietary tags
        dietary_tags = [tag for tag in existing_tags if tag in ['vegetarian', 'vegan', 'gluten-free', 'dairy-free']]
        
        # Only analyze if we don't have comprehensive dietary tags
        if len(dietary_tags) == 0:
            new_tags, reasoning, certainty = self.analyze_recipe_dietary_properties(recipe)
            
            if new_tags and certainty in ['high', 'medium']:
                # Merge with existing tags, avoiding duplicates
                all_tags = list(set(existing_tags + new_tags))
                recipe['tags'] = all_tags
                
                print(f"✅ Auto-tagged '{recipe['name']}' with: {new_tags} (certainty: {certainty})")
                if reasoning:
                    print(f"   💭 Reasoning: {reasoning}")
        
        return recipe
    
    def get_fallback_tags(self, recipe: dict) -> List[str]:
        """
        Generate basic tags using keyword analysis when AI is not available
        
        Args:
            recipe: Recipe dictionary
            
        Returns:
            list: List of detected tags
        """
        tags = []
        
        # Convert recipe content to lowercase for analysis
        recipe_text = (
            recipe.get('name', '') + ' ' + 
            recipe.get('instructions', '') + ' ' +
            ' '.join([str(ing) for ing in recipe.get('ingredients', [])])
        ).lower()
        
        # Meat detection
        meat_keywords = ['fleisch', 'hack', 'schwein', 'rind', 'huhn', 'hähnchen', 'pute', 'schinken', 'speck', 'wurst', 'beef', 'pork', 'chicken', 'meat', 'lachs', 'fisch', 'thunfisch']
        has_meat = any(keyword in recipe_text for keyword in meat_keywords)
        
        if not has_meat:
            tags.append('vegetarian')
            
            # Vegan detection (no animal products)
            animal_products = ['käse', 'milch', 'butter', 'sahne', 'joghurt', 'ei', 'cheese', 'milk', 'cream', 'egg', 'honey', 'honig']
            has_animal_products = any(keyword in recipe_text for keyword in animal_products)
            
            if not has_animal_products:
                tags.append('vegan')
        
        # Quick detection
        cooking_time = recipe.get('cooking_time', 60)
        if cooking_time and cooking_time <= 30:
            tags.append('quick')
        
        if cooking_time and cooking_time <= 15:
            tags.append('easy')
        
        return tags

# Global instance
auto_tagger = AutoTagger()