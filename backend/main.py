from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.api.routes import recipes, meal_plans, shopping_lists
from app.database_sqlite import init_db

load_dotenv()

# Initialize SQLite database
init_db()

app = FastAPI(title="ChefChat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(meal_plans.router, prefix="/api/meal-plans", tags=["meal-plans"])
app.include_router(shopping_lists.router, prefix="/api/shopping-lists", tags=["shopping-lists"])

@app.get("/")
def read_root():
    return {"message": "ChefChat API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)