import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

class ChromaSearchService:
    def __init__(self):
        self.persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Use default embedding function (sentence transformers)
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Get or create recipes collection
            self.recipes_collection = self.client.get_or_create_collection(
                name="recipes",
                embedding_function=self.embedding_function,
                metadata={"description": "Recipe collection for semantic search"}
            )
            
            self.enabled = True
            print("✅ ChromaDB initialized successfully!")
            
        except Exception as e:
            print(f"❌ Warning: Could not initialize ChromaDB: {e}")
            print("   Falling back to basic text search")
            self.client = None
            self.recipes_collection = None
            self.enabled = False
    
    def add_recipe(self, recipe_id: int, recipe_name: str, ingredients: list, tags: list, instructions: str = "", cooking_time: int = None):
        """Add a recipe to the vector database for semantic search"""
        if not self.enabled:
            return
            
        try:
            # Create rich searchable text from recipe data
            ingredient_names = [ing.get('name', '') for ing in ingredients if isinstance(ing, dict)]
            ingredient_text = ', '.join(ingredient_names)
            tags_text = ', '.join(tags) if tags else ''
            
            # Build comprehensive searchable content
            searchable_parts = [
                f"Recipe: {recipe_name}",
                f"Ingredients: {ingredient_text}",
                f"Tags: {tags_text}",
            ]
            
            if cooking_time:
                if cooking_time <= 15:
                    searchable_parts.append("quick meal, fast cooking, under 15 minutes")
                elif cooking_time <= 30:
                    searchable_parts.append("quick meal, under 30 minutes")
                elif cooking_time <= 60:
                    searchable_parts.append("medium cooking time, under 1 hour")
                else:
                    searchable_parts.append("long cooking time, over 1 hour")
            
            # Add cooking method hints based on instructions
            if instructions:
                instructions_lower = instructions.lower()
                if any(word in instructions_lower for word in ['bake', 'oven', 'roast']):
                    searchable_parts.append("baked, oven-cooked")
                if any(word in instructions_lower for word in ['fry', 'pan', 'skillet']):
                    searchable_parts.append("fried, pan-cooked")
                if any(word in instructions_lower for word in ['boil', 'simmer', 'steam']):
                    searchable_parts.append("boiled, steamed, wet cooking")
                if any(word in instructions_lower for word in ['grill', 'barbecue']):
                    searchable_parts.append("grilled, barbecued")
                if 'salad' in instructions_lower or any(word in instructions_lower for word in ['raw', 'fresh', 'uncooked']):
                    searchable_parts.append("raw, fresh, salad, no cooking")
            
            # Add cuisine and dietary hints based on ingredients and tags
            if any(word in ' '.join([recipe_name.lower(), ingredient_text.lower(), tags_text.lower()]) 
                   for word in ['tomato', 'pasta', 'parmesan', 'basil', 'mozzarella']):
                searchable_parts.append("Italian cuisine, Mediterranean")
                
            if any(word in ' '.join([recipe_name.lower(), ingredient_text.lower(), tags_text.lower()]) 
                   for word in ['rice', 'soy', 'ginger', 'sesame', 'noodle']):
                searchable_parts.append("Asian cuisine, oriental")
                
            if any(word in tags_text.lower() for word in ['vegetarian', 'vegan', 'plant-based']):
                searchable_parts.append("vegetarian, plant-based, no meat")
                
            if any(word in ' '.join([recipe_name.lower(), ingredient_text.lower()]) 
                   for word in ['salad', 'lettuce', 'spinach', 'kale', 'cucumber']):
                searchable_parts.append("healthy, fresh, salad, greens, vegetables")
            
            searchable_text = ' '.join(searchable_parts)
            
            # Store in ChromaDB
            self.recipes_collection.upsert(
                documents=[searchable_text],
                metadatas=[{
                    "recipe_id": recipe_id,
                    "name": recipe_name,
                    "tags": tags,
                    "cooking_time": cooking_time,
                    "ingredient_count": len(ingredient_names)
                }],
                ids=[str(recipe_id)]
            )
            
        except Exception as e:
            print(f"Warning: Could not add recipe {recipe_id} to ChromaDB: {e}")
    
    def search_recipes(self, query: str, n_results: int = 10) -> List[Dict]:
        """Search for recipes using semantic similarity"""
        if not self.enabled:
            return []
            
        try:
            # Enhance query with common cooking terms
            enhanced_query = query
            
            # Add context for common requests
            if any(word in query.lower() for word in ['vegetarisch', 'vegetarian', 'vegan']):
                enhanced_query += " plant-based no meat vegetarian"
            
            if any(word in query.lower() for word in ['schnell', 'quick', 'fast', 'unter', 'under']):
                enhanced_query += " quick fast cooking short time"
                
            if any(word in query.lower() for word in ['gesund', 'healthy', 'light']):
                enhanced_query += " healthy fresh vegetables salad"
                
            if any(word in query.lower() for word in ['italienisch', 'italian']):
                enhanced_query += " Italian Mediterranean pasta tomato"
            
            results = self.recipes_collection.query(
                query_texts=[enhanced_query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            search_results = []
            if results and results["metadatas"] and results["metadatas"][0]:
                for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
                    search_results.append({
                        "recipe_id": metadata["recipe_id"],
                        "name": metadata["name"],
                        "tags": metadata["tags"],
                        "cooking_time": metadata.get("cooking_time"),
                        "score": 1 - distance  # Convert distance to similarity score
                    })
            
            return search_results
            
        except Exception as e:
            print(f"Warning: ChromaDB search failed: {e}")
            return []
    
    def update_recipe(self, recipe_id: int, recipe_name: str, ingredients: list, tags: list, instructions: str = "", cooking_time: int = None):
        """Update a recipe in the vector database"""
        if not self.enabled:
            return
            
        # ChromaDB upsert will automatically update existing entries
        self.add_recipe(recipe_id, recipe_name, ingredients, tags, instructions, cooking_time)
    
    def delete_recipe(self, recipe_id: int):
        """Delete a recipe from the vector database"""
        if not self.enabled:
            return
            
        try:
            self.recipes_collection.delete(ids=[str(recipe_id)])
        except Exception as e:
            print(f"Warning: Could not delete recipe {recipe_id} from ChromaDB: {e}")
    
    def get_stats(self) -> Dict:
        """Get statistics about the recipe collection"""
        if not self.enabled:
            return {"enabled": False, "total_recipes": 0}
            
        try:
            collection_info = self.recipes_collection.get()
            return {
                "enabled": True,
                "total_recipes": len(collection_info["ids"]) if collection_info["ids"] else 0,
                "collection_name": self.recipes_collection.name
            }
        except Exception as e:
            return {"enabled": False, "error": str(e)}

# Global instance
chroma_search = ChromaSearchService()