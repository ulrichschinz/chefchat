from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database_sqlite import sqlite_db as db

router = APIRouter()

# Pydantic models
class ShoppingItemBase(BaseModel):
    name: str
    amount: float
    unit: str
    section: str

class ShoppingListBase(BaseModel):
    meal_plan_id: int
    items: List[ShoppingItemBase]

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingList(ShoppingListBase):
    id: int
    created_at: str

@router.post("/", response_model=ShoppingList)
def create_shopping_list(shopping_list: ShoppingListCreate):
    shopping_list_data = shopping_list.dict()
    db_shopping_list = db.create_shopping_list(shopping_list_data)
    return db_shopping_list

@router.get("/", response_model=List[ShoppingList])
def read_shopping_lists(skip: int = 0, limit: int = 100):
    shopping_lists = db.get_all_shopping_lists(skip, limit)
    return shopping_lists

@router.get("/{shopping_list_id}", response_model=ShoppingList)
def read_shopping_list(shopping_list_id: int):
    shopping_list = db.get_shopping_list(shopping_list_id)
    if shopping_list is None:
        raise HTTPException(status_code=404, detail="Shopping list not found")
    return shopping_list