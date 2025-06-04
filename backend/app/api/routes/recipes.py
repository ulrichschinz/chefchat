from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.database_sqlite import sqlite_db as db
from app.services.basic_search import basic_search
from app.services.chroma_search import chroma_search
from app.services.auto_tagger import auto_tagger

router = APIRouter()

# Pydantic models
class IngredientBase(BaseModel):
    amount: float
    unit: str
    name: str

class RecipeBase(BaseModel):
    name: str
    ingredients: List[IngredientBase]
    instructions: str
    cooking_time: int = None
    servings: int = 4
    is_cookidoo: bool = False
    tags: List[str] = []

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
    created_at: str

@router.post("/", response_model=Recipe)
def create_recipe(recipe: RecipeCreate):
    recipe_data = recipe.dict()
    
    # Auto-tag the recipe with AI analysis
    try:
        recipe_data = auto_tagger.auto_tag_recipe(recipe_data)
    except Exception as e:
        print(f"⚠️ Auto-tagging failed for new recipe: {e}")
        # Continue with recipe creation even if tagging fails
    
    db_recipe = db.create_recipe(recipe_data)
    
    # Add to search indexes
    basic_search.add_recipe(
        db_recipe["id"], 
        db_recipe["name"], 
        db_recipe["ingredients"], 
        db_recipe["tags"]
    )
    
    chroma_search.add_recipe(
        db_recipe["id"],
        db_recipe["name"],
        db_recipe["ingredients"],
        db_recipe["tags"],
        db_recipe["instructions"],
        db_recipe.get("cooking_time")
    )
    
    return db_recipe

@router.get("/", response_model=List[Recipe])
def read_recipes(skip: int = 0, limit: int = 100):
    recipes = db.get_all_recipes(skip, limit)
    return recipes

@router.get("/{recipe_id}", response_model=Recipe)
def read_recipe(recipe_id: int):
    recipe = db.get_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.put("/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, recipe: RecipeCreate):
    recipe_data = recipe.dict()
    
    # Auto-tag the updated recipe with AI analysis
    try:
        recipe_data = auto_tagger.auto_tag_recipe(recipe_data)
    except Exception as e:
        print(f"⚠️ Auto-tagging failed for updated recipe: {e}")
        # Continue with recipe update even if tagging fails
    
    db_recipe = db.update_recipe(recipe_id, recipe_data)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Update search indexes
    basic_search.update_recipe(
        recipe_id, 
        db_recipe["name"], 
        db_recipe["ingredients"], 
        db_recipe["tags"]
    )
    
    chroma_search.update_recipe(
        recipe_id,
        db_recipe["name"],
        db_recipe["ingredients"],
        db_recipe["tags"],
        db_recipe["instructions"],
        db_recipe.get("cooking_time")
    )
    
    return db_recipe

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int):
    success = db.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Remove from search indexes
    basic_search.delete_recipe(recipe_id)
    chroma_search.delete_recipe(recipe_id)
    
    return {"message": "Recipe deleted"}

@router.get("/search/{query}")
def search_recipes(query: str, limit: int = 10):
    """Search recipes by text query using ChromaDB or fallback to basic search"""
    
    # Try ChromaDB first, fallback to basic search
    if chroma_search.enabled:
        results = chroma_search.search_recipes(query, limit)
        if results:
            return {
                "results": results,
                "search_method": "semantic (ChromaDB)",
                "total": len(results)
            }
    
    # Fallback to basic search
    results = basic_search.search_recipes(query, limit)
    return {
        "results": results,
        "search_method": "text-based (fallback)",
        "total": len(results)
    }