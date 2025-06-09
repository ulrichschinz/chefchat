<template>
  <div class="max-w-2xl mx-auto bg-white shadow rounded-lg p-6">
    <h2 class="text-xl font-semibold text-gray-900 mb-6">{{ isEditing ? 'Edit Recipe' : 'Add New Recipe' }}</h2>
    
    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Recipe Name -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700">Recipe Name</label>
        <input
          type="text"
          id="name"
          v-model="recipe.name"
          required
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          placeholder="Enter recipe name"
        />
      </div>

      <!-- Cooking Time, Servings, and Cookidoo -->
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label for="cooking_time" class="block text-sm font-medium text-gray-700">Cooking Time (minutes)</label>
          <input
            type="number"
            id="cooking_time"
            v-model.number="recipe.cooking_time"
            min="1"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="30"
          />
        </div>
        <div>
          <label for="servings" class="block text-sm font-medium text-gray-700">Servings</label>
          <input
            type="number"
            id="servings"
            v-model.number="recipe.servings"
            min="1"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="4"
          />
        </div>
        <div class="flex items-end">
          <div class="flex items-center h-10">
            <input
              id="is_cookidoo"
              type="checkbox"
              v-model="recipe.is_cookidoo"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label for="is_cookidoo" class="ml-2 block text-sm text-gray-900">
              Cookidoo Recipe
            </label>
          </div>
        </div>
      </div>

      <!-- Cookidoo Info -->
      <div v-if="recipe.is_cookidoo" class="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">Cookidoo Recipe</h3>
            <div class="mt-2 text-sm text-blue-700">
              <p>This recipe is available on Cookidoo with Thermomix cooking program. Detailed instructions can be found in the Cookidoo app.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tags -->
      <div>
        <label for="tags" class="block text-sm font-medium text-gray-700">Tags</label>
        <div class="mt-1 flex flex-wrap gap-2 mb-2">
          <span
            v-for="(tag, index) in recipe.tags"
            :key="index"
            class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
          >
            {{ tag }}
            <button
              type="button"
              @click="removeTag(index)"
              class="ml-2 h-4 w-4 rounded-full inline-flex items-center justify-center text-indigo-400 hover:bg-indigo-200 hover:text-indigo-500"
            >
              ×
            </button>
          </span>
        </div>
        <div class="flex">
          <input
            type="text"
            v-model="newTag"
            @keyup.enter="addTag"
            class="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Add tag (press Enter)"
          />
          <button
            type="button"
            @click="addTag"
            class="px-4 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-700 hover:bg-gray-100"
          >
            Add
          </button>
        </div>
      </div>

      <!-- Ingredients -->
      <div>
        <div class="flex justify-between items-center mb-3">
          <label class="block text-sm font-medium text-gray-700">Ingredients</label>
          <button
            type="button"
            @click="addIngredient"
            class="text-sm text-indigo-600 hover:text-indigo-500"
          >
            + Add Ingredient
          </button>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="(ingredient, index) in recipe.ingredients"
            :key="index"
            class="grid grid-cols-12 gap-2 items-center"
          >
            <input
              type="number"
              v-model.number="ingredient.amount"
              step="0.1"
              min="0"
              required
              :data-ingredient-index="index"
              data-field="amount"
              class="col-span-3 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Amount"
            />
            <select
              v-model="ingredient.unit"
              required
              class="col-span-2 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="">Unit</option>
              <option value="g">g</option>
              <option value="kg">kg</option>
              <option value="ml">ml</option>
              <option value="l">l</option>
              <option value="cup">cup</option>
              <option value="tbsp">tbsp</option>
              <option value="tsp">tsp</option>
              <option value="EL">EL (Esslöffel)</option>
              <option value="TL">TL (Teelöffel)</option>
              <option value="piece">piece</option>
              <option value="clove">clove</option>
              <option value="slice">slice</option>
            </select>
            <input
              type="text"
              v-model="ingredient.name"
              required
              @keydown.enter.prevent="handleIngredientEnter(index)"
              :data-ingredient-index="index"
              data-field="name"
              class="col-span-6 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Ingredient name"
            />
            <button
              type="button"
              @click="removeIngredient(index)"
              class="col-span-1 text-red-600 hover:text-red-500"
            >
              ×
            </button>
          </div>
        </div>
        
        <p v-if="recipe.ingredients.length === 0" class="text-sm text-gray-500 italic">
          No ingredients added yet. Click "Add Ingredient" to start.
        </p>
      </div>

      <!-- Instructions -->
      <div>
        <label for="instructions" class="block text-sm font-medium text-gray-700">Instructions</label>
        <textarea
          id="instructions"
          v-model="recipe.instructions"
          required
          rows="6"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          placeholder="Enter step-by-step cooking instructions..."
        ></textarea>
      </div>

      <!-- Submit Buttons -->
      <div class="flex justify-end space-x-3">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {{ isSubmitting ? 'Saving...' : (isEditing ? 'Update Recipe' : 'Save Recipe') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, defineEmits, defineProps, watch, nextTick } from 'vue'

const props = defineProps({
  initialRecipe: {
    type: Object,
    default: () => ({})
  },
  isEditing: {
    type: Boolean,
    default: false
  },
  isSubmitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const recipe = reactive({
  name: '',
  cooking_time: null,
  servings: 4,
  is_cookidoo: false,
  tags: [],
  ingredients: [],
  instructions: ''
})

const newTag = ref('')

// Initialize form with existing recipe data
watch(() => props.initialRecipe, (newValue) => {
  if (newValue && Object.keys(newValue).length > 0) {
    Object.assign(recipe, {
      name: newValue.name || '',
      cooking_time: newValue.cooking_time || null,
      servings: newValue.servings || 4,
      is_cookidoo: newValue.is_cookidoo || false,
      tags: [...(newValue.tags || [])],
      ingredients: [...(newValue.ingredients || [])],
      instructions: newValue.instructions || ''
    })
  }
}, { immediate: true })

const addTag = () => {
  if (newTag.value.trim() && !recipe.tags.includes(newTag.value.trim())) {
    recipe.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

const removeTag = (index) => {
  recipe.tags.splice(index, 1)
}

const addIngredient = () => {
  recipe.ingredients.push({
    amount: null,
    unit: '',
    name: ''
  })
}

const removeIngredient = (index) => {
  recipe.ingredients.splice(index, 1)
}

const handleIngredientEnter = async (index) => {
  const ingredient = recipe.ingredients[index]
  
  // Only add new ingredient if current one is complete
  if (ingredient.amount && ingredient.unit && ingredient.name.trim()) {
    addIngredient()
    
    // Wait for DOM update, then focus on the new ingredient's amount field
    await nextTick()
    
    // Find the amount input of the newly added ingredient
    const newIngredientIndex = recipe.ingredients.length - 1
    const newAmountInput = document.querySelector(`input[data-ingredient-index="${newIngredientIndex}"][data-field="amount"]`)
    
    if (newAmountInput) {
      newAmountInput.focus()
      newAmountInput.select()
    }
  }
}

const submitForm = () => {
  // Basic validation
  if (!recipe.name.trim()) {
    alert('Please enter a recipe name')
    return
  }
  
  if (recipe.ingredients.length === 0) {
    alert('Please add at least one ingredient')
    return
  }
  
  if (!recipe.instructions.trim()) {
    alert('Please enter cooking instructions')
    return
  }
  
  // Validate ingredients
  for (let ingredient of recipe.ingredients) {
    if (!ingredient.amount || !ingredient.unit || !ingredient.name.trim()) {
      alert('Please fill in all ingredient fields')
      return
    }
  }
  
  emit('submit', { ...recipe })
}

// Add initial ingredient if none exist and not editing
if (!props.isEditing && recipe.ingredients.length === 0) {
  addIngredient()
}
</script>