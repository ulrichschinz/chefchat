# ChefChat - AI-Powered Recipe Management & Meal Planning

An intelligent recipe management application with Claude 4 Opus-powered meal planning, semantic recipe search, and smart lunch planning for busy professionals.

## ✨ Key Features

- 🤖 **AI Meal Planning** - Natural language requests: "3x vegetarisch diese Woche", "schnelle Mittagessen unter 30 Minuten"
- 🧠 **Semantic Recipe Search** - ChromaDB-powered search that understands ingredients, cuisines, and cooking methods
- 🚫 **No Duplicate Meals** - Intelligent variety optimization ensures different recipes each day
- 🇩🇪 **German-First** - Built for German cooking with support for German units (TL, EL) and language
- 🤖 **Cookidoo Integration** - Special handling for Thermomix Cookidoo recipes
- 📱 **Mobile-First Design** - Optimized for quick lunch planning on mobile devices

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Simple JSON Database** - Lightweight file-based storage (Python 3.13 compatible)
- **ChromaDB** - Vector database for semantic recipe search with intelligent fallback
- **Claude 4 Opus** - Advanced AI meal planning and recipe suggestions
- **Dual Search System** - ChromaDB + text search fallback for maximum reliability

### Frontend
- **Vue.js 3** - Frontend framework with Composition API
- **Vite** - Build tool and dev server
- **Pinia** - State management
- **Tailwind CSS** - Modern utility-first styling
- **Vue Router** - Client-side routing with recipe detail views

## 🚀 Getting Started

### Prerequisites
- Python 3.13+ (required for compatibility)
- Node.js 18+ 
- Claude API key from Anthropic

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements-simple-db.txt
   ```

4. Create `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

5. Add your Claude API key to `.env`:
   ```env
   ANTHROPIC_API_KEY=your_claude_api_key_here
   DATABASE_URL=sqlite:///./chefchat.db
   CHROMA_PERSIST_DIRECTORY=./chroma_db
   ```

6. Run the development server:
   ```bash
   python main_simple.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

### 🎯 Quick Test

1. Visit `http://localhost:5173`
2. Add a few recipes with German ingredients
3. Go to "Meal Plans" → "🤖 AI Meal Plan"
4. Try: "3x vegetarisch diese Woche"
5. Watch Claude 4 Opus create your intelligent lunch plan!

## 📋 Features Status

### ✅ Implemented Features
- **Recipe Management** - Complete CRUD with excellent UX
  - Dynamic ingredient entry with Enter key support
  - German/English units (TL, EL, tbsp, tsp, g, kg, ml, l)
  - Cookidoo recipe flagging for Thermomix integration
  - Recipe tags and cooking time tracking
  - Mobile-responsive recipe cards with preview

- **AI-Powered Meal Planning** - Claude 4 Opus integration
  - Natural language processing: "3x vegetarisch diese Woche"
  - Intelligent recipe selection based on preferences
  - Automatic variety optimization (no duplicates when possible)
  - AI explanations for meal plan choices
  - Weekly lunch-focused planning

- **Semantic Recipe Search** - ChromaDB + fallback system
  - Understands cooking methods, cuisines, and ingredients
  - Automatic dietary detection (vegetarian, healthy, quick)
  - Time-based categorization (quick <15min, medium <30min)
  - Reliable fallback to text search when needed

- **Modern Recipe Views**
  - Detailed recipe pages with ingredients and instructions
  - Click-to-view recipe cards
  - Edit recipes with URL-based routing
  - Beautiful weekly meal plan calendar
  - Mobile-first responsive design

### 🚧 Coming Next
- **Shopping List Generation** - Auto-generate from meal plans
- **Recipe Import/Export** - Bulk recipe management
- **Advanced Search Filters** - Filter by time, tags, ingredients
- **Recipe Categories** - Better organization for growing collection

## 🔧 API Endpoints

### Recipes
- `GET /api/recipes/` - List all recipes
- `POST /api/recipes/` - Create new recipe
- `GET /api/recipes/{id}` - Get recipe by ID
- `PUT /api/recipes/{id}` - Update recipe
- `DELETE /api/recipes/{id}` - Delete recipe
- `GET /api/recipes/search/{query}` - Semantic recipe search

### Meal Planning
- `GET /api/meal-plans/` - List meal plans
- `POST /api/meal-plans/` - Create meal plan
- `POST /api/meal-plans/generate` - AI-powered meal plan generation
- `POST /api/meal-plans/save-generated` - Save generated meal plan

### Shopping Lists
- `GET /api/shopping-lists/` - List shopping lists
- `POST /api/shopping-lists/` - Create shopping list

## 🛠️ Development Notes

- **Python 3.13 Compatible** - Uses simplified JSON database instead of SQLAlchemy
- **Dual Search System** - ChromaDB with automatic fallback ensures reliability
- **Claude 4 Opus** - Latest AI model for best meal planning quality
- **Hot Reload** - Both frontend and backend support live development
- **API Proxy** - Frontend automatically routes API calls to backend
- **Error Handling** - Graceful fallbacks for all AI and search operations

## 🎨 Architecture Decisions

1. **No Complex Import Pipeline** - Manual recipe entry with excellent UX for 30+ recipes
2. **All LLM Logic in Backend** - Frontend displays results, backend handles AI complexity
3. **ChromaDB for Semantic Search** - Essential for 50+ recipe collections
4. **Simple JSON Database** - Python 3.13 compatible, fast for development
5. **Lunch-Only Focus** - Simplified meal planning for busy professionals