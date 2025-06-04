import anthropic
import os
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        print(f"Debug: API key found: {'Yes' if api_key else 'No'}")
        if api_key:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.enabled = True
                print("✅ Claude AI service initialized successfully!")
            except Exception as e:
                print(f"❌ Warning: Could not initialize Anthropic client: {e}")
                self.client = None
                self.enabled = False
        else:
            print("❌ Warning: No ANTHROPIC_API_KEY found. AI features will be disabled.")
            self.client = None
            self.enabled = False
    
    def generate_meal_plan(self, request: str, available_recipes: List[Dict]) -> Dict:
        """Generate a meal plan based on user request and available recipes"""
        
        if not self.enabled:
            return self._generate_fallback_meal_plan(request, available_recipes)
        
        recipes_text = "\n".join([
            f"- {recipe['name']} (ID: {recipe['id']}, Tags: {', '.join(recipe.get('tags', []))}, "
            f"Cooking time: {recipe.get('cooking_time', 'N/A')} min, Servings: {recipe.get('servings', 4)})"
            for recipe in available_recipes
        ])
        
        prompt = f"""You are a meal planning assistant. Based on the user's request and the available recipes, create a weekly lunch meal plan.

User request: "{request}"

Available recipes:
{recipes_text}

Please create a meal plan for one week (Monday to Sunday) with ONLY lunch for each day. 
Return your response as a JSON object with this structure:
{{
  "meal_plan": {{
    "monday": {{"lunch": recipe_id}},
    "tuesday": {{"lunch": recipe_id}},
    ... (for all 7 days)
  }},
  "explanation": "Brief explanation of the lunch meal plan choices"
}}

CRITICAL DIETARY RULES:
- If the user requests "vegetarian" or "vegetarisch", use ONLY vegetarian recipes (no meat, poultry, or fish)
- If the user requests "vegan", use ONLY vegan recipes (no animal products at all)
- If the user requests specific dietary restrictions, STRICTLY follow them
- The available recipes have already been pre-filtered to match the user's dietary requirements

IMPORTANT RULES:
1. Use only the recipe IDs from the available recipes
2. Try to avoid repeating the same recipe during the week - each day should have a different recipe if possible
3. Only repeat recipes if there are fewer than 7 available recipes
4. STRICTLY follow dietary restrictions mentioned in the user's request
5. Consider cooking time preferences (schnell = quick, unter 30 = under 30 minutes)
6. Focus on lunch-appropriate meals
7. Ensure variety in cooking methods, ingredients, and flavors throughout the week"""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                json_str = response_text[start_idx:end_idx]
                
                result = json.loads(json_str)
                
                # Validate and fix duplicates if needed
                result = self._ensure_variety_in_meal_plan(result, available_recipes)
                return result
                
            except (ValueError, json.JSONDecodeError):
                # If JSON parsing fails, return a basic structure
                return {
                    "meal_plan": {},
                    "explanation": "Error parsing AI response. Please try again.",
                    "raw_response": response_text
                }
                
        except Exception as e:
            return {
                "meal_plan": {},
                "explanation": f"Error generating meal plan: {str(e)}",
                "error": True
            }
    
    def _generate_fallback_meal_plan(self, request: str, available_recipes: List[Dict]) -> Dict:
        """Generate a simple meal plan without AI when Claude is not available"""
        import random
        
        if len(available_recipes) < 2:
            return {
                "meal_plan": {},
                "explanation": "Not enough recipes available for meal planning. Please add more recipes first."
            }
        
        # Create a copy and shuffle for variety
        recipe_pool = available_recipes.copy()
        random.shuffle(recipe_pool)
        
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        meal_plan = {}
        used_recipes = set()
        
        # First, try to assign unique recipes to each day
        available_unique = [r for r in recipe_pool if r["id"] not in used_recipes]
        
        for i, day in enumerate(days):
            if i < len(available_unique):
                # Use unique recipe for this day
                lunch_recipe = available_unique[i]
                used_recipes.add(lunch_recipe["id"])
            else:
                # If we run out of unique recipes, start repeating
                # But try to space them out (use oldest first)
                lunch_recipe = recipe_pool[i % len(recipe_pool)]
            
            meal_plan[day] = {
                "lunch": lunch_recipe["id"]
            }
        
        unique_count = len(used_recipes)
        total_days = len(days)
        
        explanation = f"Simple meal plan generated (AI not available). "
        if unique_count == total_days:
            explanation += "Each day has a different recipe for maximum variety."
        else:
            explanation += f"Used {unique_count} different recipes across {total_days} days, with minimal repetition."
        
        return {
            "meal_plan": meal_plan,
            "explanation": explanation
        }
    
    def _ensure_variety_in_meal_plan(self, meal_plan_result: Dict, available_recipes: List[Dict]) -> Dict:
        """Ensure no duplicates in meal plan, fix if needed"""
        meal_plan = meal_plan_result.get("meal_plan", {})
        explanation = meal_plan_result.get("explanation", "")
        
        if not meal_plan:
            return meal_plan_result
        
        # Extract all recipe IDs used
        used_recipes = []
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        for day in days:
            if day in meal_plan and "lunch" in meal_plan[day]:
                used_recipes.append(meal_plan[day]["lunch"])
        
        # Check for duplicates
        unique_recipes = list(set(used_recipes))
        has_duplicates = len(used_recipes) != len(unique_recipes)
        
        if has_duplicates and len(available_recipes) >= 7:
            # We have enough recipes but AI created duplicates - fix it
            available_ids = [r["id"] for r in available_recipes]
            unused_recipes = [rid for rid in available_ids if rid not in used_recipes]
            
            # Replace duplicates with unused recipes
            seen = set()
            for day in days:
                if day in meal_plan and "lunch" in meal_plan[day]:
                    recipe_id = meal_plan[day]["lunch"]
                    if recipe_id in seen and unused_recipes:
                        # Replace duplicate with unused recipe
                        new_recipe_id = unused_recipes.pop(0)
                        meal_plan[day]["lunch"] = new_recipe_id
                        explanation += f" (Replaced duplicate with recipe {new_recipe_id} for {day})"
                    else:
                        seen.add(recipe_id)
        
        return {
            "meal_plan": meal_plan,
            "explanation": explanation
        }
    
    def suggest_recipes_for_request(self, request: str, search_results: List[Dict]) -> List[int]:
        """Use AI to select the most relevant recipes for a meal planning request"""
        
        if not self.enabled:
            # Simple fallback: return top search results
            return [recipe['recipe_id'] for recipe in search_results[:10]]
        
        recipes_text = "\n".join([
            f"- {recipe['name']} (ID: {recipe['recipe_id']}, Tags: {', '.join(recipe.get('tags', []))}, Score: {recipe['score']:.2f})"
            for recipe in search_results
        ])
        
        prompt = f"""Based on the user's meal planning request, select the most relevant recipes from the search results.

User request: "{request}"

Search results:
{recipes_text}

Return a JSON array of recipe IDs that best match the user's request. Consider dietary preferences, cooking time, and variety.
Example: [1, 3, 5, 7, 12]

Limit to maximum 10 recipes."""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            # Try to extract JSON array from the response
            try:
                # Find JSON array in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                json_str = response_text[start_idx:end_idx]
                
                return json.loads(json_str)
            except (ValueError, json.JSONDecodeError):
                # If JSON parsing fails, return all recipe IDs
                return [recipe['recipe_id'] for recipe in search_results[:10]]
                
        except Exception as e:
            # If AI fails, return all recipe IDs
            return [recipe['recipe_id'] for recipe in search_results[:10]]
    
    def analyze_meal_request_and_generate_searches(self, request: str) -> List[str]:
        """Analyze a meal planning request and generate search queries for ChromaDB"""
        
        if not self.enabled:
            # Simple fallback: use the original request
            return [request]
        
        prompt = f"""Analyze this meal planning request and generate 2-3 semantic search queries that would help find the most relevant recipes.

User request: "{request}"

Your task:
1. Understand what the user wants (dietary preferences, cooking time, meal types, etc.)
2. Generate 2-3 different search queries that would capture relevant recipes
3. Make the search queries semantic and descriptive (not just keywords)

Examples:
- For "2 x vegetarische und der rest mit fleisch" → ["vegetarian lunch dishes", "meat-based main courses", "hearty lunch recipes"]
- For "quick pasta for busy weeknight" → ["quick pasta recipes", "easy weeknight dinners", "fast Italian dishes"]
- For "healthy breakfast options" → ["nutritious breakfast recipes", "healthy morning meals", "light breakfast dishes"]

Return a JSON array of search query strings (2-3 queries maximum).
Example: ["vegetarian lunch dishes", "meat-based main courses"]"""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            # Try to extract JSON array from the response
            try:
                # Find JSON array in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                json_str = response_text[start_idx:end_idx]
                
                search_queries = json.loads(json_str)
                
                # Validate that we have 1-3 string queries
                if isinstance(search_queries, list) and 1 <= len(search_queries) <= 3:
                    return [str(q) for q in search_queries if q]
                else:
                    return [request]  # Fallback to original request
                    
            except (ValueError, json.JSONDecodeError):
                # If JSON parsing fails, return original request
                return [request]
                
        except Exception as e:
            # If AI fails, return original request
            return [request]
    
    def interpret_meal_plan_edit_request(self, edit_request: str, current_meal_plan: Dict) -> Dict:
        """Interpret a natural language request to edit a meal plan"""
        
        if not self.enabled:
            return {
                "days_to_change": [],
                "requirements": edit_request,
                "error": "AI not available for edit interpretation"
            }
        
        # Convert meal plan to readable format for AI
        meal_plan_text = ""
        for day, meals in current_meal_plan.items():
            if "lunch" in meals:
                meal_plan_text += f"- {day.capitalize()}: Recipe ID {meals['lunch']}\n"
        
        prompt = f"""Analyze this meal plan edit request and extract the specific changes needed.

Current meal plan:
{meal_plan_text}

User edit request: "{edit_request}"

Your task:
1. Identify which days need to be changed
2. Extract any specific requirements for the new meals (dietary, cooking time, etc.)
3. Preserve all other days unchanged

Return a JSON object with this structure:
{{
  "days_to_change": ["tuesday", "friday"],
  "requirements": "quick recipes under 30 minutes",
  "preserve_other_days": true
}}

Examples:
- "bitte am dienstag und freitag etwas anderes. es sollten möglichst schnelle gerichte sein" → {{"days_to_change": ["tuesday", "friday"], "requirements": "quick recipes fast cooking time"}}
- "montag sollte vegetarisch sein" → {{"days_to_change": ["monday"], "requirements": "vegetarian recipe"}}
- "donnerstag und sonntag brauche ich etwas ohne fleisch" → {{"days_to_change": ["thursday", "sunday"], "requirements": "vegetarian or vegan recipes no meat"}}

Day names in German should be converted to English: montag→monday, dienstag→tuesday, mittwoch→wednesday, donnerstag→thursday, freitag→friday, samstag→saturday, sonntag→sunday"""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=500,
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
                
                # Validate the structure
                if isinstance(result, dict) and "days_to_change" in result:
                    # Ensure days_to_change is a list
                    if not isinstance(result["days_to_change"], list):
                        result["days_to_change"] = []
                    
                    # Set default requirements if missing
                    if "requirements" not in result:
                        result["requirements"] = edit_request
                    
                    result["preserve_other_days"] = True
                    return result
                else:
                    return {
                        "days_to_change": [],
                        "requirements": edit_request,
                        "preserve_other_days": True,
                        "error": "Could not parse edit request"
                    }
                    
            except (ValueError, json.JSONDecodeError):
                return {
                    "days_to_change": [],
                    "requirements": edit_request,
                    "preserve_other_days": True,
                    "error": "JSON parsing failed"
                }
                
        except Exception as e:
            return {
                "days_to_change": [],
                "requirements": edit_request,
                "preserve_other_days": True,
                "error": f"AI request failed: {str(e)}"
            }

# Global instance
ai_service = AIService()