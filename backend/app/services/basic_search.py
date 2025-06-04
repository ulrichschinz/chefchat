import json
import os
from typing import List, Dict
import re

class BasicSearchService:
    def __init__(self):
        self.recipes_file = "recipes_search.json"
        self.recipes_data = {}
        self.load_data()
    
    def save_data(self):
        """Save recipes to file"""
        with open(self.recipes_file, 'w') as f:
            json.dump(self.recipes_data, f)
    
    def load_data(self):
        """Load recipes from file"""
        if os.path.exists(self.recipes_file):
            try:
                with open(self.recipes_file, 'r') as f:
                    self.recipes_data = json.load(f)
            except:
                self.recipes_data = {}
    
    def add_recipe(self, recipe_id: int, recipe_name: str, ingredients: list, tags: list):
        """Add a recipe for text-based search"""
        # Create searchable text from recipe data
        ingredient_names = [ing['name'].lower() for ing in ingredients]
        tag_names = [tag.lower() for tag in tags]
        
        self.recipes_data[str(recipe_id)] = {
            "recipe_id": recipe_id,
            "name": recipe_name.lower(),
            "tags": tag_names,
            "ingredients": ingredient_names,
            "searchable_text": f"{recipe_name.lower()} {' '.join(ingredient_names)} {' '.join(tag_names)}"
        }
        
        self.save_data()
    
    def search_recipes(self, query: str, n_results: int = 10):
        """Search for recipes using text matching"""
        if not self.recipes_data:
            return []
        
        query_lower = query.lower()
        query_words = re.findall(r'\w+', query_lower)
        
        results = []
        for recipe_id, recipe_data in self.recipes_data.items():
            score = 0
            searchable_text = recipe_data["searchable_text"]
            
            # Score based on word matches
            for word in query_words:
                if word in searchable_text:
                    score += 1
                # Bonus for exact matches in name or tags
                if word in recipe_data["name"]:
                    score += 2
                if word in recipe_data["tags"]:
                    score += 1.5
            
            if score > 0:
                results.append({
                    "recipe_id": recipe_data["recipe_id"],
                    "name": recipe_data["name"].title(),
                    "tags": recipe_data["tags"],
                    "score": score / len(query_words)  # Normalize by query length
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:n_results]
    
    def update_recipe(self, recipe_id: int, recipe_name: str, ingredients: list, tags: list):
        """Update a recipe"""
        self.add_recipe(recipe_id, recipe_name, ingredients, tags)
    
    def delete_recipe(self, recipe_id: int):
        """Delete a recipe"""
        recipe_id_str = str(recipe_id)
        if recipe_id_str in self.recipes_data:
            del self.recipes_data[recipe_id_str]
            self.save_data()

# Global instance
basic_search = BasicSearchService()