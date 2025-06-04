from sqlalchemy import create_engine, Column, Integer, String, Text, Float, JSON, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
import os
from datetime import datetime, date

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chefchat.db")

# Create engine with proper SQLite configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    ingredients = Column(JSON, nullable=False)  # [{"amount": 200, "unit": "g", "name": "flour"}]
    instructions = Column(Text, nullable=False)
    cooking_time = Column(Integer)  # minutes
    servings = Column(Integer, default=4)
    is_cookidoo = Column(Boolean, default=False)
    tags = Column(JSON, default=list)  # ["vegetarian", "quick"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MealPlan(Base):
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    week_starting = Column(Date, nullable=False, index=True)
    meals = Column(JSON, nullable=False)  # {"monday": {"lunch": recipe_id}, ...}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"))
    items = Column(JSON, nullable=False)  # [{"name": "tomatoes", "amount": 500, "unit": "g", "section": "produce"}]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    meal_plan = relationship("MealPlan", backref="shopping_lists")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ SQLite database initialized successfully!")

# Database operations class
class DatabaseOperations:
    def __init__(self):
        self.SessionLocal = SessionLocal
    
    def get_session(self):
        return self.SessionLocal()
    
    # Recipe operations
    def create_recipe(self, recipe_data: dict):
        db = self.get_session()
        try:
            db_recipe = Recipe(**recipe_data)
            db.add(db_recipe)
            db.commit()
            db.refresh(db_recipe)
            return self._recipe_to_dict(db_recipe)
        finally:
            db.close()
    
    def get_recipe(self, recipe_id: int):
        db = self.get_session()
        try:
            recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
            return self._recipe_to_dict(recipe) if recipe else None
        finally:
            db.close()
    
    def get_all_recipes(self, skip: int = 0, limit: int = 100):
        db = self.get_session()
        try:
            recipes = db.query(Recipe).offset(skip).limit(limit).all()
            return [self._recipe_to_dict(recipe) for recipe in recipes]
        finally:
            db.close()
    
    def update_recipe(self, recipe_id: int, recipe_data: dict):
        db = self.get_session()
        try:
            recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not recipe:
                return None
            
            for key, value in recipe_data.items():
                if hasattr(recipe, key):
                    setattr(recipe, key, value)
            
            recipe.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(recipe)
            return self._recipe_to_dict(recipe)
        finally:
            db.close()
    
    def delete_recipe(self, recipe_id: int):
        db = self.get_session()
        try:
            recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not recipe:
                return False
            
            db.delete(recipe)
            db.commit()
            return True
        finally:
            db.close()
    
    # Meal plan operations
    def create_meal_plan(self, meal_plan_data: dict):
        db = self.get_session()
        try:
            # Convert week_starting string to date object if needed
            meal_plan_data_copy = meal_plan_data.copy()
            if isinstance(meal_plan_data_copy.get('week_starting'), str):
                from datetime import datetime
                meal_plan_data_copy['week_starting'] = datetime.strptime(
                    meal_plan_data_copy['week_starting'], '%Y-%m-%d'
                ).date()
            
            db_meal_plan = MealPlan(**meal_plan_data_copy)
            db.add(db_meal_plan)
            db.commit()
            db.refresh(db_meal_plan)
            return self._meal_plan_to_dict(db_meal_plan)
        finally:
            db.close()
    
    def get_meal_plan(self, meal_plan_id: int):
        db = self.get_session()
        try:
            meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
            return self._meal_plan_to_dict(meal_plan) if meal_plan else None
        finally:
            db.close()
    
    def get_all_meal_plans(self, skip: int = 0, limit: int = 100):
        db = self.get_session()
        try:
            meal_plans = db.query(MealPlan).offset(skip).limit(limit).all()
            return [self._meal_plan_to_dict(meal_plan) for meal_plan in meal_plans]
        finally:
            db.close()
    
    def delete_meal_plan(self, meal_plan_id: int):
        db = self.get_session()
        try:
            meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
            if meal_plan:
                db.delete(meal_plan)
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    # Shopping list operations
    def create_shopping_list(self, shopping_list_data: dict):
        db = self.get_session()
        try:
            db_shopping_list = ShoppingList(**shopping_list_data)
            db.add(db_shopping_list)
            db.commit()
            db.refresh(db_shopping_list)
            return self._shopping_list_to_dict(db_shopping_list)
        finally:
            db.close()
    
    def get_shopping_list(self, shopping_list_id: int):
        db = self.get_session()
        try:
            shopping_list = db.query(ShoppingList).filter(ShoppingList.id == shopping_list_id).first()
            return self._shopping_list_to_dict(shopping_list) if shopping_list else None
        finally:
            db.close()
    
    def get_all_shopping_lists(self, skip: int = 0, limit: int = 100):
        db = self.get_session()
        try:
            shopping_lists = db.query(ShoppingList).offset(skip).limit(limit).all()
            return [self._shopping_list_to_dict(shopping_list) for shopping_list in shopping_lists]
        finally:
            db.close()
    
    # Helper methods to convert SQLAlchemy models to dicts
    def _recipe_to_dict(self, recipe):
        return {
            "id": recipe.id,
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "cooking_time": recipe.cooking_time,
            "servings": recipe.servings,
            "is_cookidoo": recipe.is_cookidoo,
            "tags": recipe.tags or [],
            "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
            "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None
        }
    
    def _meal_plan_to_dict(self, meal_plan):
        return {
            "id": meal_plan.id,
            "week_starting": meal_plan.week_starting.isoformat() if meal_plan.week_starting else None,
            "meals": meal_plan.meals,
            "created_at": meal_plan.created_at.isoformat() if meal_plan.created_at else None,
            "updated_at": meal_plan.updated_at.isoformat() if meal_plan.updated_at else None
        }
    
    def _shopping_list_to_dict(self, shopping_list):
        return {
            "id": shopping_list.id,
            "meal_plan_id": shopping_list.meal_plan_id,
            "items": shopping_list.items,
            "created_at": shopping_list.created_at.isoformat() if shopping_list.created_at else None,
            "updated_at": shopping_list.updated_at.isoformat() if shopping_list.updated_at else None
        }

# Global database instance
sqlite_db = DatabaseOperations()