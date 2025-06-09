import { defineStore } from 'pinia'
import axios from 'axios'

export const useShoppingListsStore = defineStore('shoppingLists', {
  state: () => ({
    shoppingLists: [],
    currentShoppingList: null,
    loading: false,
    error: null
  }),

  getters: {
    getShoppingListByMealPlan: (state) => (mealPlanId) => {
      return state.shoppingLists.find(list => list.meal_plan_id === mealPlanId)
    },
    
    getItemsBySection: (state) => {
      if (!state.currentShoppingList) return {}
      
      return state.currentShoppingList.items.reduce((sections, item) => {
        if (!sections[item.section]) {
          sections[item.section] = []
        }
        sections[item.section].push(item)
        return sections
      }, {})
    }
  },

  actions: {
    async fetchShoppingLists() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/shopping-lists/')
        this.shoppingLists = response.data
      } catch (error) {
        this.error = error.message
        console.error('Error fetching shopping lists:', error)
      } finally {
        this.loading = false
      }
    },

    async createShoppingList(shoppingListData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/shopping-lists/', shoppingListData)
        this.shoppingLists.push(response.data)
        this.currentShoppingList = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error creating shopping list:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async generateShoppingListFromMealPlan(mealPlanId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post(`/api/shopping-lists/generate/${mealPlanId}`)
        const shoppingList = response.data
        
        // Update existing list or add new one
        const existingIndex = this.shoppingLists.findIndex(list => list.meal_plan_id === mealPlanId)
        if (existingIndex !== -1) {
          this.shoppingLists[existingIndex] = shoppingList
        } else {
          this.shoppingLists.push(shoppingList)
        }
        
        this.currentShoppingList = shoppingList
        return shoppingList
      } catch (error) {
        this.error = error.message
        console.error('Error generating shopping list:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentShoppingList(shoppingList) {
      this.currentShoppingList = shoppingList
    }
  }
})