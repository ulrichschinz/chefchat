<template>
  <div class="px-4 py-6 sm:px-0">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-sm text-gray-500">Loading recipe...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
      <div class="flex">
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error loading recipe</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
          <div class="mt-4">
            <button
              @click="$router.push('/recipes')"
              class="text-sm bg-red-100 text-red-800 px-3 py-1 rounded hover:bg-red-200"
            >
              Back to Recipes
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Recipe Content -->
    <div v-else-if="recipe" class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-6 py-8">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <button
                @click="$router.push('/recipes')"
                class="text-gray-400 hover:text-gray-600"
                title="Back to recipes"
              >
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div>
                <div class="flex items-center space-x-3">
                  <h1 class="text-3xl font-bold text-gray-900">{{ recipe.name }}</h1>
                  <span 
                    v-if="recipe.is_cookidoo" 
                    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800"
                    title="Cookidoo Recipe with Thermomix program"
                  >
                    🤖 Cookidoo
                  </span>
                </div>
              </div>
            </div>
            <div class="flex space-x-3">
              <button
                @click="editRecipe"
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit Recipe
              </button>
              <button
                @click="deleteRecipe"
                class="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
              >
                <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>

          <!-- Recipe Meta Info -->
          <div class="mt-6 flex items-center space-x-6 text-sm text-gray-500">
            <div class="flex items-center">
              <svg class="flex-shrink-0 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ recipe.cooking_time ? `${recipe.cooking_time} minutes` : 'No cooking time set' }}
            </div>
            <div class="flex items-center">
              <svg class="flex-shrink-0 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              {{ recipe.servings }} {{ recipe.servings === 1 ? 'serving' : 'servings' }}
            </div>
            <div v-if="recipe.tags.length > 0" class="flex items-center">
              <svg class="flex-shrink-0 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.99 1.99 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="tag in recipe.tags"
                  :key="tag"
                  class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- Cookidoo Info -->
          <div v-if="recipe.is_cookidoo" class="mt-6 bg-blue-50 border border-blue-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-blue-800">Cookidoo Recipe</h3>
                <div class="mt-1 text-sm text-blue-700">
                  <p>This recipe is available on Cookidoo with Thermomix cooking program. Detailed instructions can be found in the Cookidoo app.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Ingredients -->
        <div class="lg:col-span-1">
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Ingredients</h2>
            </div>
            <div class="px-6 py-4">
              <ul class="space-y-2">
                <li
                  v-for="(ingredient, index) in recipe.ingredients"
                  :key="index"
                  class="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0"
                >
                  <span class="text-sm text-gray-900">{{ ingredient.name }}</span>
                  <span class="text-sm text-gray-500 font-medium">
                    {{ ingredient.amount }} {{ ingredient.unit }}
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Instructions -->
        <div class="lg:col-span-2">
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Instructions</h2>
            </div>
            <div class="px-6 py-4">
              <div class="prose prose-sm max-w-none">
                <div class="whitespace-pre-wrap text-gray-700 leading-relaxed">{{ recipe.instructions }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecipesStore } from '../stores/recipes'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const route = useRoute()
const router = useRouter()
const recipesStore = useRecipesStore()

const recipe = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  await loadRecipe()
})

const loadRecipe = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Try to get from store first
    let foundRecipe = recipesStore.getRecipeById(parseInt(props.id))
    
    if (!foundRecipe) {
      // If not in store, fetch all recipes (simple approach)
      await recipesStore.fetchRecipes()
      foundRecipe = recipesStore.getRecipeById(parseInt(props.id))
    }
    
    if (foundRecipe) {
      recipe.value = foundRecipe
    } else {
      error.value = 'Recipe not found'
    }
  } catch (err) {
    error.value = 'Failed to load recipe'
    console.error('Error loading recipe:', err)
  } finally {
    loading.value = false
  }
}

const editRecipe = () => {
  router.push(`/recipes?edit=${props.id}`)
}

const deleteRecipe = async () => {
  if (confirm('Are you sure you want to delete this recipe?')) {
    try {
      await recipesStore.deleteRecipe(parseInt(props.id))
      router.push('/recipes')
    } catch (error) {
      console.error('Error deleting recipe:', error)
      alert('Error deleting recipe. Please try again.')
    }
  }
}
</script>