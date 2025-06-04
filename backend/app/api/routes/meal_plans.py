from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import date

from app.database_sqlite import sqlite_db as db
from app.services.ai_service import ai_service
from app.services.basic_search import basic_search
from app.services.chroma_search import chroma_search

router = APIRouter()

def _filter_recipes_by_dietary_requirements(request: str, recipes: List[Dict], strict: bool = True) -> List[Dict]:
    """Filter recipes based on dietary requirements in the request"""
    request_lower = request.lower()
    
    filtered_recipes = recipes.copy()
    
    # Check if this is a mixed request (contains both vegetarian and meat)
    is_mixed_request = (
        ('vegetarian' in request_lower or 'vegetarisch' in request_lower) and 
        ('fleisch' in request_lower or 'meat' in request_lower or 'rest' in request_lower)
    )
    
    # For mixed requests, don't filter - let AI handle the selection
    if is_mixed_request:
        return filtered_recipes
    
    # Only apply strict dietary filtering for pure dietary requests
    if ('vegetarian' in request_lower or 'vegetarisch' in request_lower) and not is_mixed_request:
        # Try tag-based filtering first
        tag_filtered = [r for r in filtered_recipes if 'vegetarian' in r.get('tags', [])]
        if tag_filtered:
            filtered_recipes = tag_filtered
        else:
            # Fallback to keyword-based filtering
            excluded_keywords = ['fleisch', 'hack', 'schwein', 'rind', 'huhn', 'hähnchen', 'pute', 'schinken', 'speck', 'wurst', 'beef', 'pork', 'chicken', 'meat']
            if strict:
                filtered_recipes = [
                    recipe for recipe in filtered_recipes
                    if not any(
                        keyword in recipe['name'].lower() or
                        keyword in recipe['instructions'].lower() or
                        any(keyword in str(ingredient).lower() for ingredient in recipe.get('ingredients', []))
                        for keyword in excluded_keywords
                    )
                ]
            else:
                obvious_meat_keywords = ['fleisch', 'hack', 'schwein', 'rind', 'huhn', 'hähnchen', 'pute', 'beef', 'pork', 'chicken']
                filtered_recipes = [
                    recipe for recipe in filtered_recipes
                    if not any(keyword in recipe['name'].lower() for keyword in obvious_meat_keywords)
                ]
    
    if 'vegan' in request_lower:
        # Try tag-based filtering first
        tag_filtered = [r for r in filtered_recipes if 'vegan' in r.get('tags', [])]
        if tag_filtered:
            filtered_recipes = tag_filtered
        else:
            # Fallback to keyword-based filtering
            excluded_keywords = ['fleisch', 'hack', 'schwein', 'rind', 'huhn', 'hähnchen', 'pute', 'schinken', 'speck', 'wurst', 'käse', 'milch', 'butter', 'sahne', 'joghurt', 'ei', 'beef', 'pork', 'chicken', 'meat', 'cheese', 'milk', 'cream', 'egg']
            filtered_recipes = [
                recipe for recipe in filtered_recipes
                if not any(
                    keyword in recipe['name'].lower() or
                    keyword in recipe['instructions'].lower() or
                    any(keyword in str(ingredient).lower() for ingredient in recipe.get('ingredients', []))
                    for keyword in excluded_keywords
                )
            ]
    
    # Quick filters using tags first, then cooking time
    if 'schnell' in request_lower or 'quick' in request_lower:
        tag_filtered = [r for r in filtered_recipes if 'quick' in r.get('tags', [])]
        if tag_filtered:
            filtered_recipes = tag_filtered
        else:
            filtered_recipes = [r for r in filtered_recipes if r.get('cooking_time', 60) <= 30]
    
    if 'einfach' in request_lower or 'easy' in request_lower:
        tag_filtered = [r for r in filtered_recipes if 'easy' in r.get('tags', [])]
        if tag_filtered:
            filtered_recipes = tag_filtered
        else:
            filtered_recipes = [r for r in filtered_recipes if r.get('cooking_time', 60) <= 20]
    
    if 'unter 15' in request_lower or 'under 15' in request_lower:
        filtered_recipes = [r for r in filtered_recipes if r.get('cooking_time', 60) <= 15]
    
    if 'unter 30' in request_lower or 'under 30' in request_lower:
        filtered_recipes = [r for r in filtered_recipes if r.get('cooking_time', 60) <= 30]
    
    return filtered_recipes

# Pydantic models
class MealPlanBase(BaseModel):
    week_starting: str  # Using string for simplicity
    meals: Dict[str, Dict[str, int]]  # {"monday": {"lunch": recipe_id, "dinner": recipe_id}}

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    id: int
    created_at: str

class MealPlanRequest(BaseModel):
    request: str  # Natural language request like "3x vegetarisch diese Woche"

class MealPlanEditRequest(BaseModel):
    meal_plan_id: int
    edit_request: str  # Natural language edit like "bitte am dienstag und freitag etwas anderes"

class SwitchMealRequest(BaseModel):
    meal_plan_id: int
    day: str  # "monday", "tuesday", etc.
    requirements: str = ""  # Optional requirements like "vegetarian" or "quick"

@router.post("/", response_model=MealPlan)
def create_meal_plan(meal_plan: MealPlanCreate):
    meal_plan_data = meal_plan.dict()
    db_meal_plan = db.create_meal_plan(meal_plan_data)
    return db_meal_plan

@router.get("/", response_model=List[MealPlan])
def read_meal_plans(skip: int = 0, limit: int = 100):
    meal_plans = db.get_all_meal_plans(skip, limit)
    return meal_plans

@router.get("/{meal_plan_id}", response_model=MealPlan)
def read_meal_plan(meal_plan_id: int):
    meal_plan = db.get_meal_plan(meal_plan_id)
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plan

@router.delete("/{meal_plan_id}")
def delete_meal_plan(meal_plan_id: int):
    meal_plan = db.get_meal_plan(meal_plan_id)
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    db.delete_meal_plan(meal_plan_id)
    return {"message": "Meal plan deleted successfully"}

@router.post("/generate")
def generate_meal_plan(request: MealPlanRequest):
    """Generate a meal plan using AI based on natural language request"""
    try:
        # Get all available recipes
        all_recipes = db.get_all_recipes()
        
        if not all_recipes:
            raise HTTPException(status_code=400, detail="No recipes available for meal planning")
        
        # Use AI to analyze the request and generate dynamic search queries
        search_queries = ai_service.analyze_meal_request_and_generate_searches(request.request)
        
        search_results = []
        search_method = "none"
        all_search_results = []
        
        # Perform multiple searches based on AI-generated queries
        if chroma_search.enabled:
            search_method = f"semantic (ChromaDB) - {len(search_queries)} AI-generated queries"
            for query in search_queries:
                query_results = chroma_search.search_recipes(query, n_results=10)
                all_search_results.extend(query_results)
        
        if not all_search_results:
            # Fallback to basic search with AI-generated queries
            search_method = f"text-based (fallback) - {len(search_queries)} AI-generated queries"
            for query in search_queries:
                query_results = basic_search.search_recipes(query, n_results=10)
                all_search_results.extend(query_results)
        
        # Remove duplicates while preserving order and best scores
        seen_ids = set()
        search_results = []
        for result in all_search_results:
            recipe_id = result['recipe_id']
            if recipe_id not in seen_ids:
                search_results.append(result)
                seen_ids.add(recipe_id)
        
        # Limit total results to reasonable number for AI context
        search_results = search_results[:20]
        
        # Get full recipe data for search results
        if search_results:
            recipe_ids = [result['recipe_id'] for result in search_results]
            recipe_data = [recipe for recipe in all_recipes if recipe['id'] in recipe_ids]
        else:
            # Fallback to all recipes if no search results - let AI choose the best ones
            recipe_data = all_recipes  # Use all available recipes
            search_method += " + all recipes (no search matches)"
        
        # No hard-coded dietary filtering - let AI handle all selection logic
        # AI has already generated appropriate search queries and will select suitable recipes
        
        # Generate meal plan using AI
        meal_plan_result = ai_service.generate_meal_plan(request.request, recipe_data)
        
        return {
            "meal_plan": meal_plan_result.get("meal_plan", {}),
            "explanation": meal_plan_result.get("explanation", ""),
            "available_recipes": len(recipe_data),
            "search_results": len(search_results) if search_results else 0,
            "search_method": search_method,
            "ai_search_queries": search_queries
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating meal plan: {str(e)}")

@router.post("/save-generated", response_model=MealPlan)
def save_generated_meal_plan(meal_plan_data: Dict):
    """Save a generated meal plan to the database"""
    try:
        # Extract meal plan data
        week_starting = meal_plan_data.get("week_starting")
        meals = meal_plan_data.get("meals", {})
        
        if not week_starting or not meals:
            raise HTTPException(status_code=400, detail="Missing week_starting or meals data")
        
        # Create meal plan
        meal_plan = {
            "week_starting": week_starting,
            "meals": meals
        }
        
        db_meal_plan = db.create_meal_plan(meal_plan)
        return db_meal_plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving meal plan: {str(e)}")

@router.post("/edit")
def edit_meal_plan(request: MealPlanEditRequest):
    """Edit specific days in a meal plan using natural language"""
    try:
        # Get the existing meal plan
        meal_plan = db.get_meal_plan(request.meal_plan_id)
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        
        # Use AI to interpret the edit request
        edit_interpretation = ai_service.interpret_meal_plan_edit_request(
            request.edit_request, 
            meal_plan["meals"]
        )
        
        days_to_change = edit_interpretation.get("days_to_change", [])
        requirements = edit_interpretation.get("requirements", "")
        
        if not days_to_change:
            return {
                "error": "Could not identify which days to change",
                "interpretation": edit_interpretation,
                "original_meal_plan": meal_plan
            }
        
        # Get all recipes for the replacement search
        all_recipes = db.get_all_recipes()
        
        # Generate search queries for the requirements
        search_queries = ai_service.analyze_meal_request_and_generate_searches(requirements)
        
        # Search for suitable replacement recipes
        search_results = []
        if chroma_search.enabled:
            for query in search_queries:
                query_results = chroma_search.search_recipes(query, n_results=10)
                search_results.extend(query_results)
        
        if not search_results:
            for query in search_queries:
                query_results = basic_search.search_recipes(query, n_results=10)
                search_results.extend(query_results)
        
        # Remove duplicates and get recipe data
        seen_ids = set()
        unique_results = []
        for result in search_results:
            if result['recipe_id'] not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result['recipe_id'])
        
        replacement_recipes = []
        if unique_results:
            recipe_ids = [result['recipe_id'] for result in unique_results[:15]]
            replacement_recipes = [recipe for recipe in all_recipes if recipe['id'] in recipe_ids]
        
        if not replacement_recipes:
            replacement_recipes = all_recipes[:15]  # Fallback
        
        # Use AI to select specific recipes for each day to change
        new_meals = meal_plan["meals"].copy()
        selected_recipes = []
        
        for day in days_to_change:
            if day in new_meals:
                # Get current recipe to avoid selecting the same one
                current_recipe_id = new_meals[day].get("lunch")
                available_for_day = [r for r in replacement_recipes if r["id"] != current_recipe_id and r["id"] not in selected_recipes]
                
                if available_for_day:
                    # Let AI pick the best recipe for this day
                    day_request = f"{requirements} for {day}"
                    day_search_results = [{"recipe_id": r["id"], "name": r["name"], "tags": r.get("tags", []), "score": 1.0} for r in available_for_day[:5]]
                    selected_recipe_ids = ai_service.suggest_recipes_for_request(day_request, day_search_results)
                    
                    if selected_recipe_ids:
                        new_recipe_id = selected_recipe_ids[0]
                        new_meals[day]["lunch"] = new_recipe_id
                        selected_recipes.append(new_recipe_id)
        
        # Update the meal plan in the database
        updated_meal_plan_data = {
            "week_starting": meal_plan["week_starting"],
            "meals": new_meals
        }
        
        # Save as new meal plan (you might want to update existing instead)
        updated_meal_plan = db.create_meal_plan(updated_meal_plan_data)
        
        return {
            "updated_meal_plan": updated_meal_plan,
            "interpretation": edit_interpretation,
            "days_changed": days_to_change,
            "requirements": requirements,
            "original_meal_plan_id": request.meal_plan_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error editing meal plan: {str(e)}")

@router.post("/switch-meal")
def switch_meal(request: SwitchMealRequest):
    """Switch a single meal for a specific day with optional requirements"""
    try:
        # Get the existing meal plan
        meal_plan = db.get_meal_plan(request.meal_plan_id)
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        
        if request.day not in meal_plan["meals"]:
            raise HTTPException(status_code=400, detail=f"Day '{request.day}' not found in meal plan")
        
        # Get current recipe to avoid selecting the same one
        current_recipe_id = meal_plan["meals"][request.day].get("lunch")
        
        # Search for alternative recipes
        search_query = request.requirements if request.requirements else "lunch main course"
        search_queries = ai_service.analyze_meal_request_and_generate_searches(search_query)
        
        # Get all recipes and search
        all_recipes = db.get_all_recipes()
        search_results = []
        
        if chroma_search.enabled:
            for query in search_queries:
                query_results = chroma_search.search_recipes(query, n_results=10)
                search_results.extend(query_results)
        
        if not search_results:
            for query in search_queries:
                query_results = basic_search.search_recipes(query, n_results=10)
                search_results.extend(query_results)
        
        # Filter out current recipe and get alternatives
        alternative_results = [r for r in search_results if r['recipe_id'] != current_recipe_id]
        
        if not alternative_results:
            # Fallback: get any recipe that's not the current one
            alternative_results = [{"recipe_id": r["id"], "name": r["name"], "score": 1.0} 
                                 for r in all_recipes if r["id"] != current_recipe_id][:10]
        
        if not alternative_results:
            raise HTTPException(status_code=400, detail="No alternative recipes found")
        
        # Let AI pick the best alternative
        selected_recipe_ids = ai_service.suggest_recipes_for_request(search_query, alternative_results[:5])
        
        if not selected_recipe_ids:
            new_recipe_id = alternative_results[0]['recipe_id']
        else:
            new_recipe_id = selected_recipe_ids[0]
        
        # Update the meal plan
        new_meals = meal_plan["meals"].copy()
        new_meals[request.day]["lunch"] = new_recipe_id
        
        updated_meal_plan_data = {
            "week_starting": meal_plan["week_starting"],
            "meals": new_meals
        }
        
        # Save as new meal plan
        updated_meal_plan = db.create_meal_plan(updated_meal_plan_data)
        
        # Get recipe details for response
        old_recipe = next((r for r in all_recipes if r["id"] == current_recipe_id), None)
        new_recipe = next((r for r in all_recipes if r["id"] == new_recipe_id), None)
        
        return {
            "updated_meal_plan": updated_meal_plan,
            "day": request.day,
            "old_recipe": {"id": current_recipe_id, "name": old_recipe["name"] if old_recipe else "Unknown"},
            "new_recipe": {"id": new_recipe_id, "name": new_recipe["name"] if new_recipe else "Unknown"},
            "requirements": request.requirements,
            "original_meal_plan_id": request.meal_plan_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching meal: {str(e)}")