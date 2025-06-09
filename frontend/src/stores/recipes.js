import { defineStore } from 'pinia'
import axios from 'axios'

export const useRecipesStore = defineStore('recipes', {
  state: () => ({
    recipes: [],
    loading: false,
    error: null
  }),

  getters: {
    getRecipeById: (state) => (id) => {
      return state.recipes.find(recipe => recipe.id === id)
    },
    
    getRecipesByTags: (state) => (tags) => {
      return state.recipes.filter(recipe => 
        recipe.tags.some(tag => tags.includes(tag))
      )
    }
  },

  actions: {
    async fetchRecipes() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/recipes/')
        this.recipes = response.data
      } catch (error) {
        this.error = error.message
        console.error('Error fetching recipes:', error)
      } finally {
        this.loading = false
      }
    },

    async createRecipe(recipeData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/recipes/', recipeData)
        this.recipes.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error creating recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateRecipe(id, recipeData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/recipes/${id}`, recipeData)
        const index = this.recipes.findIndex(recipe => recipe.id === id)
        if (index !== -1) {
          this.recipes[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error updating recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteRecipe(id) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/api/recipes/${id}`)
        const index = this.recipes.findIndex(recipe => recipe.id === id)
        if (index !== -1) {
          this.recipes.splice(index, 1)
        }
      } catch (error) {
        this.error = error.message
        console.error('Error deleting recipe:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})