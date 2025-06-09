<template>
  <div class="px-4 py-6 sm:px-0">
    <!-- Header -->
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Meal Plans</h1>
        <p class="mt-2 text-sm text-gray-700">Plan your weekly meals with AI assistance</p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
        <button
          type="button"
          @click="showAIPlanner = true"
          class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700"
        >
          🤖 AI Meal Plan
        </button>
      </div>
    </div>

    <!-- AI Meal Planner -->
    <div v-if="showAIPlanner" class="mt-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium text-gray-900">AI Meal Planner</h2>
            <button
              @click="showAIPlanner = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="px-6 py-6">
          <div class="space-y-6">
            <!-- Request Input -->
            <div>
              <label for="meal-request" class="block text-sm font-medium text-gray-700">
                Tell me what you want for this week
              </label>
              <div class="mt-1">
                <textarea
                  id="meal-request"
                  v-model="mealRequest"
                  rows="3"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="e.g., '3x vegetarisch diese Woche', 'schnelle Mittagessen unter 30 Minuten', 'gesunde Salate und warme Gerichte'"
                ></textarea>
              </div>
              <p class="mt-2 text-sm text-gray-500">
                Describe your lunch preferences in natural language. I'll find the best recipes from your collection.
              </p>
            </div>

            <!-- Week Configuration -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Week Start Day -->
              <div>
                <label for="week-start-day" class="block text-sm font-medium text-gray-700">
                  Week starts on
                </label>
                <div class="mt-1">
                  <select
                    id="week-start-day"
                    v-model="weekStartDay"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                    <option value="0">Sunday</option>
                    <option value="1">Monday</option>
                    <option value="2">Tuesday</option>
                    <option value="3">Wednesday</option>
                    <option value="4">Thursday</option>
                    <option value="5">Friday</option>
                    <option value="6">Saturday</option>
                  </select>
                </div>
                <p class="mt-1 text-xs text-gray-500">
                  Choose which day your week begins
                </p>
              </div>

              <!-- Week Starting Date -->
              <div>
                <label for="week-starting-date" class="block text-sm font-medium text-gray-700">
                  Week starting date
                </label>
                <div class="mt-1">
                  <input
                    id="week-starting-date"
                    type="date"
                    v-model="weekStartingDate"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  >
                </div>
                <p class="mt-1 text-xs text-gray-500">
                  Automatically calculated based on your week start day
                </p>
              </div>
            </div>

            <!-- Generate Button -->
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showAIPlanner = false"
                class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                @click="generateMealPlan"
                :disabled="!mealRequest.trim() || isGenerating"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {{ isGenerating ? 'Generating...' : '🤖 Generate Lunch Plan' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Generated Meal Plan -->
    <div v-if="generatedPlan" class="mt-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium text-gray-900">Generated Lunch Plan</h2>
            <div class="flex space-x-3">
              <button
                @click="saveMealPlan"
                :disabled="isSaving"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
              >
                {{ isSaving ? 'Saving...' : 'Save Plan' }}
              </button>
              <button
                @click="generatedPlan = null"
                class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Discard
              </button>
            </div>
          </div>
        </div>

        <div class="px-6 py-6">
          <!-- AI Explanation -->
          <div v-if="generatedPlan.explanation" class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <h3 class="text-sm font-medium text-blue-800 mb-2">AI Explanation</h3>
            <p class="text-sm text-blue-700">{{ generatedPlan.explanation }}</p>
          </div>

          <!-- Chat Interface for Editing Generated Plan -->
          <div class="mb-6 bg-gray-50 rounded-lg p-4">
            <h3 class="text-sm font-medium text-gray-700 mb-3">💬 Want to change something? Just ask!</h3>
            <div class="space-y-3">
              <div>
                <textarea
                  v-model="generatedPlanEditRequest"
                  rows="2"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="e.g., 'bitte am dienstag und freitag etwas anderes. es sollten möglichst schnelle gerichte sein'"
                ></textarea>
              </div>
              <div class="flex justify-end">
                <button
                  @click="editGeneratedPlan"
                  :disabled="!generatedPlanEditRequest.trim() || isEditingGenerated"
                  class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                >
                  {{ isEditingGenerated ? 'Updating...' : '🤖 Update Plan' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Weekly Calendar with Edit Controls -->
          <div class="grid grid-cols-1 md:grid-cols-7 gap-4">
            <div
              v-for="(day, index) in orderedWeekDays"
              :key="day"
              class="border border-gray-200 rounded-lg p-4"
            >
              <h3 class="text-sm font-medium text-gray-900 mb-3 text-center">{{ day }}</h3>
              
              <div class="space-y-3">
                <!-- Lunch -->
                <div v-if="generatedPlan.meal_plan[getMealPlanDayKey(day, index)]?.lunch">
                  <div class="bg-blue-50 border border-blue-200 rounded p-3">
                    <!-- Recipe Title - Prominent Display -->
                    <div class="text-base font-semibold text-gray-900 mb-3 leading-tight">
                      {{ getRecipeName(generatedPlan.meal_plan[getMealPlanDayKey(day, index)].lunch) }}
                    </div>
                    
                    <!-- Key Info Only -->
                    <div class="mb-3">
                      <div class="flex items-center justify-between text-xs text-gray-600 mb-2">
                        <span v-if="getRecipeDetails(generatedPlan.meal_plan[getMealPlanDayKey(day, index)].lunch)?.cooking_time">
                          🕒 {{ getRecipeDetails(generatedPlan.meal_plan[getMealPlanDayKey(day, index)].lunch).cooking_time }} min
                        </span>
                        <span v-if="getRecipeDetails(generatedPlan.meal_plan[getMealPlanDayKey(day, index)].lunch)?.servings">
                          👥 {{ getRecipeDetails(generatedPlan.meal_plan[getMealPlanDayKey(day, index)].lunch).servings }}
                        </span>
                      </div>
                      
                      <!-- Only Most Important Tags -->
                      <div v-if="getRecipeDetails(generatedPlan.meal_plan[getMealPlanDayKey(day, index)].lunch)?.tags?.length > 0" class="flex flex-wrap gap-1">
                        <span 
                          v-for="tag in getRecipeDetails(generatedPlan.meal_plan[getMealPlanDayKey(day, index)].lunch).tags.slice(0, 2)"
                          :key="tag"
                          :class="getTagStyle(tag)"
                          class="px-2 py-0.5 text-xs rounded-full"
                        >
                          {{ getTagDisplay(tag) }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- Switch Meal Controls for Generated Plan -->
                    <div class="space-y-2">
                      <button
                        @click="switchGeneratedMeal(getMealPlanDayKey(day, index))"
                        :disabled="isSwitchingGenerated"
                        class="w-full px-2 py-1 text-xs font-medium text-indigo-600 bg-indigo-100 rounded hover:bg-indigo-200 disabled:opacity-50"
                      >
                        🔄 Switch Meal
                      </button>
                      
                    </div>
                  </div>
                </div>

                <!-- Empty state -->
                <div v-if="!generatedPlan.meal_plan[getMealPlanDayKey(day, index)]?.lunch" class="text-center text-gray-400 text-xs py-4">
                  No lunch planned
                </div>
              </div>
            </div>
          </div>

          <!-- Stats -->
          <div class="mt-6 flex items-center justify-between text-sm text-gray-500">
            <div>
              Based on {{ generatedPlan.available_recipes }} available recipes
              {{ generatedPlan.search_results ? `(${generatedPlan.search_results} matched your request)` : '' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Existing Meal Plans -->
    <div class="mt-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-medium text-gray-900">Your Meal Plans</h2>
        </div>
        
        <div class="px-6 py-6">
          <!-- Loading State -->
          <div v-if="mealPlansStore.loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p class="mt-2 text-sm text-gray-500">Loading meal plans...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="mealPlansStore.mealPlans.length === 0" class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3a4 4 0 118 0v4m-8 0h8v2H8V7zm0 0H3m5 0v2m0 0h8m-8 0V19a2 2 0 002 2h4a2 2 0 002-2V9" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No meal plans yet</h3>
            <p class="mt-1 text-sm text-gray-500">Create your first AI-powered meal plan!</p>
          </div>

          <!-- Meal Plans List -->
          <div v-else class="space-y-4">
            <div
              v-for="plan in mealPlansStore.mealPlans"
              :key="plan.id"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-medium text-gray-900">
                    Week of {{ formatDate(plan.week_starting) }}
                  </h3>
                  <p class="text-sm text-gray-500">
                    {{ countMeals(plan.meals) }} lunches planned
                  </p>
                </div>
                <div class="flex space-x-2">
                  <button 
                    @click="viewMealPlan(plan)"
                    class="text-indigo-600 hover:text-indigo-500 text-sm"
                  >
                    View & Edit
                  </button>
                  <button 
                    @click="deleteMealPlan(plan.id)"
                    class="text-red-600 hover:text-red-500 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Meal Plan Editor -->
    <div v-if="editingPlan" class="mt-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium text-gray-900">
              Edit Meal Plan - Week of {{ formatDate(editingPlan.week_starting) }}
            </h2>
            <button
              @click="editingPlan = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="px-6 py-6">
          <!-- Chat Interface for Editing -->
          <div class="mb-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">💬 Chat to Edit Your Meal Plan</h3>
            <div class="space-y-3">
              <div>
                <textarea
                  v-model="editRequest"
                  rows="2"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  placeholder="e.g., 'bitte am dienstag und freitag etwas anderes. es sollten möglichst schnelle gerichte sein'"
                ></textarea>
              </div>
              <div class="flex justify-end">
                <button
                  @click="editMealPlan"
                  :disabled="!editRequest.trim() || isEditing"
                  class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                >
                  {{ isEditing ? 'Updating...' : '🤖 Update Plan' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Weekly Calendar with Edit Controls -->
          <div class="grid grid-cols-1 md:grid-cols-7 gap-4">
            <div
              v-for="(day, index) in orderedWeekDays"
              :key="day"
              class="border border-gray-200 rounded-lg p-4"
            >
              <h3 class="text-sm font-medium text-gray-900 mb-3 text-center">{{ day }}</h3>
              
              <div class="space-y-3">
                <!-- Lunch -->
                <div v-if="editingPlan.meals[getMealPlanDayKey(day, index)]?.lunch">
                  <div class="bg-blue-50 border border-blue-200 rounded p-3">
                    <!-- Recipe Title - Prominent Display -->
                    <div class="text-base font-semibold text-gray-900 mb-3 leading-tight">
                      {{ getRecipeName(editingPlan.meals[getMealPlanDayKey(day, index)].lunch) }}
                    </div>
                    
                    <!-- Key Info Only -->
                    <div class="mb-3">
                      <div class="flex items-center justify-between text-xs text-gray-600 mb-2">
                        <span v-if="getRecipeDetails(editingPlan.meals[getMealPlanDayKey(day, index)].lunch)?.cooking_time">
                          🕒 {{ getRecipeDetails(editingPlan.meals[getMealPlanDayKey(day, index)].lunch).cooking_time }} min
                        </span>
                        <span v-if="getRecipeDetails(editingPlan.meals[getMealPlanDayKey(day, index)].lunch)?.servings">
                          👥 {{ getRecipeDetails(editingPlan.meals[getMealPlanDayKey(day, index)].lunch).servings }}
                        </span>
                      </div>
                      
                      <!-- Only Most Important Tags -->
                      <div v-if="getRecipeDetails(editingPlan.meals[getMealPlanDayKey(day, index)].lunch)?.tags?.length > 0" class="flex flex-wrap gap-1">
                        <span 
                          v-for="tag in getRecipeDetails(editingPlan.meals[getMealPlanDayKey(day, index)].lunch).tags.slice(0, 2)"
                          :key="tag"
                          :class="getTagStyle(tag)"
                          class="px-2 py-0.5 text-xs rounded-full"
                        >
                          {{ getTagDisplay(tag) }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- Switch Meal Controls -->
                    <div class="space-y-2">
                      <button
                        @click="switchMeal(getMealPlanDayKey(day, index))"
                        :disabled="isSwitching"
                        class="w-full px-2 py-1 text-xs font-medium text-indigo-600 bg-indigo-100 rounded hover:bg-indigo-200 disabled:opacity-50"
                      >
                        🔄 Switch Meal
                      </button>
                      
                    </div>
                  </div>
                </div>

                <!-- Empty state -->
                <div v-if="!editingPlan.meals[getMealPlanDayKey(day, index)]?.lunch" class="text-center text-gray-400 text-xs py-4">
                  No lunch planned
                </div>
              </div>
            </div>
          </div>

          <!-- Edit History -->
          <div v-if="editHistory.length > 0" class="mt-6 border-t border-gray-200 pt-4">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Recent Changes</h3>
            <div class="space-y-2">
              <div
                v-for="(change, index) in editHistory.slice(-3)"
                :key="index"
                class="text-sm text-gray-600 bg-gray-50 rounded p-2"
              >
                {{ change }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useMealPlansStore } from '../stores/mealPlans'
import { useRecipesStore } from '../stores/recipes'

const mealPlansStore = useMealPlansStore()
const recipesStore = useRecipesStore()

const showAIPlanner = ref(false)
const mealRequest = ref('')
const isGenerating = ref(false)
const isSaving = ref(false)
const generatedPlan = ref(null)

// Editing state
const editingPlan = ref(null)
const editRequest = ref('')
const isEditing = ref(false)
const isSwitching = ref(false)
const editHistory = ref([])

// Generated plan editing state
const generatedPlanEditRequest = ref('')
const isEditingGenerated = ref(false)
const isSwitchingGenerated = ref(false)

// Week configuration
const weekStartDay = ref(1) // Default to Monday (1)
const weekStartingDate = ref('')

const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

// Computed week days based on start day
const orderedWeekDays = computed(() => {
  const allDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const startIndex = parseInt(weekStartDay.value)
  return [...allDays.slice(startIndex), ...allDays.slice(0, startIndex)]
})

// Simplified day mapping - just use the display day name directly
const getMealPlanDayKey = (displayDay, dayIndex) => {
  return displayDay.toLowerCase()
}

// Watch for week start day changes to update the starting date
watch(weekStartDay, (newStartDay) => {
  updateWeekStartingDate()
})

const updateWeekStartingDate = () => {
  const today = new Date()
  const currentDay = today.getDay() // 0 = Sunday, 1 = Monday, etc.
  const targetStartDay = parseInt(weekStartDay.value)
  
  // Calculate days to subtract to get to the start of the week
  let daysToSubtract = (currentDay - targetStartDay + 7) % 7
  
  const weekStart = new Date(today)
  weekStart.setDate(today.getDate() - daysToSubtract)
  weekStartingDate.value = weekStart.toISOString().split('T')[0]
}

onMounted(() => {
  mealPlansStore.fetchMealPlans()
  recipesStore.fetchRecipes()
  updateWeekStartingDate() // Set initial week starting date
})

const generateMealPlan = async () => {
  if (!mealRequest.value.trim()) return
  
  isGenerating.value = true
  
  try {
    const result = await mealPlansStore.generateMealPlan(mealRequest.value)
    generatedPlan.value = result
    showAIPlanner.value = false
  } catch (error) {
    console.error('Error generating meal plan:', error)
    alert('Error generating meal plan. Please try again.')
  } finally {
    isGenerating.value = false
  }
}

const saveMealPlan = async () => {
  if (!generatedPlan.value) return
  
  isSaving.value = true
  
  try {
    const mealPlanData = {
      week_starting: weekStartingDate.value,
      meals: generatedPlan.value.meal_plan
    }
    
    console.log('Saving meal plan data:', mealPlanData)
    console.log('Generated plan structure:', generatedPlan.value)
    
    await mealPlansStore.createMealPlan(mealPlanData)
    
    generatedPlan.value = null
    mealRequest.value = ''
    
    alert('Meal plan saved successfully!')
  } catch (error) {
    console.error('Error saving meal plan:', error)
    alert('Error saving meal plan. Please try again.')
  } finally {
    isSaving.value = false
  }
}

const getRecipeName = (recipeId) => {
  const recipe = recipesStore.getRecipeById(recipeId)
  return recipe ? recipe.name : `Recipe #${recipeId}`
}

const getRecipeDetails = (recipeId) => {
  return recipesStore.getRecipeById(recipeId)
}

const getTagStyle = (tag) => {
  const styles = {
    'vegetarian': 'bg-green-100 text-green-800',
    'vegan': 'bg-green-200 text-green-900', 
    'gluten-free': 'bg-yellow-100 text-yellow-800',
    'dairy-free': 'bg-blue-100 text-blue-800',
    'quick': 'bg-orange-100 text-orange-800',
    'easy': 'bg-purple-100 text-purple-800'
  }
  return styles[tag] || 'bg-gray-100 text-gray-800'
}

const getTagDisplay = (tag) => {
  const displays = {
    'vegetarian': '🥗 Vegetarian',
    'vegan': '🌱 Vegan',
    'gluten-free': '🌾 Gluten-free', 
    'dairy-free': '🥛 Dairy-free',
    'quick': '⚡ Quick',
    'easy': '✅ Easy'
  }
  return displays[tag] || tag
}

const getMainIngredients = (recipeId) => {
  const recipe = recipesStore.getRecipeById(recipeId)
  if (!recipe?.ingredients) return []
  
  // Get the first 3 main ingredients (largest amounts or most important)
  return recipe.ingredients
    .slice(0, 3)
    .map(ingredient => ingredient.name)
    .filter(name => name && name.length > 0)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const countMeals = (meals) => {
  let count = 0
  Object.values(meals).forEach(day => {
    if (day.lunch) count++
  })
  return count
}

// Editing functions
const viewMealPlan = (plan) => {
  editingPlan.value = { ...plan }
  editHistory.value = []
}

const editMealPlan = async () => {
  if (!editRequest.value.trim() || !editingPlan.value) return
  
  isEditing.value = true
  
  try {
    const result = await mealPlansStore.editMealPlan(editingPlan.value.id, editRequest.value)
    
    if (result.updated_meal_plan) {
      editingPlan.value = result.updated_meal_plan
      editHistory.value.push(`Changed ${result.days_changed?.join(', ')} - ${result.requirements}`)
      editRequest.value = ''
      
      // Refresh the meal plans list
      mealPlansStore.fetchMealPlans()
    } else if (result.error) {
      alert(`Edit failed: ${result.error}`)
    }
  } catch (error) {
    console.error('Error editing meal plan:', error)
    alert('Error editing meal plan. Please try again.')
  } finally {
    isEditing.value = false
  }
}

const switchMeal = async (day) => {
  if (!editingPlan.value) return
  
  isSwitching.value = true
  
  try {
    const result = await mealPlansStore.switchMeal(editingPlan.value.id, day)
    
    if (result.updated_meal_plan) {
      editingPlan.value = result.updated_meal_plan
      editHistory.value.push(`Switched ${day}: ${result.old_recipe.name} → ${result.new_recipe.name}`)
      
      // Refresh the meal plans list
      mealPlansStore.fetchMealPlans()
    }
  } catch (error) {
    console.error('Error switching meal:', error)
    alert('Error switching meal. Please try again.')
  } finally {
    isSwitching.value = false
  }
}

const switchMealWithRequirement = async (day, requirement) => {
  if (!editingPlan.value) return
  
  isSwitching.value = true
  
  try {
    const result = await mealPlansStore.switchMealWithRequirement(editingPlan.value.id, day, requirement)
    
    if (result.updated_meal_plan) {
      editingPlan.value = result.updated_meal_plan
      editHistory.value.push(`Switched ${day} to ${requirement}: ${result.old_recipe.name} → ${result.new_recipe.name}`)
      
      // Refresh the meal plans list
      mealPlansStore.fetchMealPlans()
    }
  } catch (error) {
    console.error('Error switching meal:', error)
    alert('Error switching meal. Please try again.')
  } finally {
    isSwitching.value = false
  }
}

const deleteMealPlan = async (planId) => {
  if (!confirm('Are you sure you want to delete this meal plan?')) return
  
  try {
    await mealPlansStore.deleteMealPlan(planId)
    if (editingPlan.value?.id === planId) {
      editingPlan.value = null
    }
  } catch (error) {
    console.error('Error deleting meal plan:', error)
    alert('Error deleting meal plan. Please try again.')
  }
}

// Generated plan editing functions
const editGeneratedPlan = async () => {
  if (!generatedPlanEditRequest.value.trim() || !generatedPlan.value) return
  
  isEditingGenerated.value = true
  
  try {
    // Use the same AI logic but apply to generated plan directly
    const editResult = await mealPlansStore.editGeneratedPlan(generatedPlan.value, generatedPlanEditRequest.value)
    
    if (editResult) {
      generatedPlan.value = editResult
      generatedPlanEditRequest.value = ''
    }
  } catch (error) {
    console.error('Error editing generated plan:', error)
    alert('Error editing plan. Please try again.')
  } finally {
    isEditingGenerated.value = false
  }
}

const switchGeneratedMeal = async (day) => {
  if (!generatedPlan.value) return
  
  isSwitchingGenerated.value = true
  
  try {
    const result = await mealPlansStore.switchGeneratedMeal(generatedPlan.value, day)
    generatedPlan.value = result
  } catch (error) {
    console.error('Error switching meal:', error)
    alert('Error switching meal. Please try again.')
  } finally {
    isSwitchingGenerated.value = false
  }
}

const switchGeneratedMealWithRequirement = async (day, requirement) => {
  if (!generatedPlan.value) return
  
  isSwitchingGenerated.value = true
  
  try {
    const result = await mealPlansStore.switchGeneratedMealWithRequirement(generatedPlan.value, day, requirement)
    generatedPlan.value = result
  } catch (error) {
    console.error('Error switching meal:', error)
    alert('Error switching meal. Please try again.')
  } finally {
    isSwitchingGenerated.value = false
  }
}
</script>