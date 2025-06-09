<template>
  <div class="px-4 py-6 sm:px-0">
    <!-- Header -->
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Recipes</h1>
        <p class="mt-2 text-sm text-gray-700">Manage your recipe collection</p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
        <button
          type="button"
          @click="showForm = true"
          class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700"
        >
          Add Recipe
        </button>
      </div>
    </div>

    <!-- Recipe Form -->
    <div v-if="showForm" class="mt-8">
      <RecipeForm 
        :initial-recipe="editingRecipe"
        :is-editing="isEditing"
        :is-submitting="isSubmitting"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </div>

    <!-- Recipe List -->
    <div v-else class="mt-8">
      <!-- Loading State -->
      <div v-if="recipesStore.loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p class="mt-2 text-sm text-gray-500">Loading recipes...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="recipesStore.error" class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex">
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading recipes</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ recipesStore.error }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="recipesStore.recipes.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No recipes</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating your first recipe.</p>
        <div class="mt-6">
          <button
            type="button"
            @click="showForm = true"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Add Recipe
          </button>
        </div>
      </div>

      <!-- Recipes Grid -->
      <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="recipe in recipesStore.recipes"
          :key="recipe.id"
          class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow cursor-pointer"
          @click="viewRecipe(recipe.id)"
        >
          <div class="p-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <h3 class="text-lg font-medium text-gray-900 truncate">{{ recipe.name }}</h3>
                <span 
                  v-if="recipe.is_cookidoo" 
                  class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800"
                  title="Cookidoo Recipe with Thermomix program"
                >
                  🤖 Cookidoo
                </span>
              </div>
              <div class="flex space-x-2">
                <button
                  @click.stop="editRecipe(recipe)"
                  class="text-indigo-600 hover:text-indigo-500"
                  title="Edit recipe"
                >
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  @click.stop="deleteRecipe(recipe.id)"
                  class="text-red-600 hover:text-red-500"
                  title="Delete recipe"
                >
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="mt-2 flex items-center text-sm text-gray-500">
              <svg class="flex-shrink-0 mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ recipe.cooking_time ? `${recipe.cooking_time} min` : 'No time set' }}
              <span class="mx-2">•</span>
              <svg class="flex-shrink-0 mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              {{ recipe.servings }} servings
            </div>

            <div class="mt-3 flex flex-wrap gap-1">
              <span
                v-for="tag in recipe.tags.slice(0, 3)"
                :key="tag"
                class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800"
              >
                {{ tag }}
              </span>
              <span v-if="recipe.tags.length > 3" class="text-xs text-gray-500">
                +{{ recipe.tags.length - 3 }} more
              </span>
            </div>

            <p class="mt-3 text-sm text-gray-600 line-clamp-3">
              {{ recipe.instructions.substring(0, 100) }}{{ recipe.instructions.length > 100 ? '...' : '' }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecipesStore } from '../stores/recipes'
import RecipeForm from '../components/RecipeForm.vue'

const route = useRoute()
const router = useRouter()
const recipesStore = useRecipesStore()

const showForm = ref(false)
const isEditing = ref(false)
const editingRecipe = ref({})
const isSubmitting = ref(false)

onMounted(() => {
  recipesStore.fetchRecipes()
  checkForEditMode()
})

// Watch for URL changes to handle edit mode
watch(() => route.query.edit, () => {
  checkForEditMode()
})

const checkForEditMode = () => {
  const editId = route.query.edit
  if (editId) {
    const recipe = recipesStore.getRecipeById(parseInt(editId))
    if (recipe) {
      editingRecipe.value = { ...recipe }
      isEditing.value = true
      showForm.value = true
    }
  }
}

const handleSubmit = async (recipeData) => {
  isSubmitting.value = true
  
  try {
    if (isEditing.value) {
      await recipesStore.updateRecipe(editingRecipe.value.id, recipeData)
    } else {
      await recipesStore.createRecipe(recipeData)
    }
    
    handleCancel()
  } catch (error) {
    console.error('Error saving recipe:', error)
    alert('Error saving recipe. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  showForm.value = false
  isEditing.value = false
  editingRecipe.value = {}
  
  // Clear edit query parameter
  if (route.query.edit) {
    router.push('/recipes')
  }
}

const editRecipe = (recipe) => {
  router.push(`/recipes?edit=${recipe.id}`)
}

const viewRecipe = (recipeId) => {
  router.push(`/recipes/${recipeId}`)
}

const deleteRecipe = async (recipeId) => {
  if (confirm('Are you sure you want to delete this recipe?')) {
    try {
      await recipesStore.deleteRecipe(recipeId)
    } catch (error) {
      console.error('Error deleting recipe:', error)
      alert('Error deleting recipe. Please try again.')
    }
  }
}
</script>