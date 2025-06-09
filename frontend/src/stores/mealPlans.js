import { defineStore } from 'pinia'
import axios from 'axios'

export const useMealPlansStore = defineStore('mealPlans', {
  state: () => ({
    mealPlans: [],
    currentMealPlan: null,
    loading: false,
    error: null
  }),

  getters: {
    getCurrentWeekMealPlan: (state) => {
      const today = new Date()
      const monday = new Date(today.setDate(today.getDate() - today.getDay() + 1))
      const mondayStr = monday.toISOString().split('T')[0]
      
      return state.mealPlans.find(plan => plan.week_starting === mondayStr)
    }
  },

  actions: {
    async fetchMealPlans() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/meal-plans/')
        this.mealPlans = response.data
      } catch (error) {
        this.error = error.message
        console.error('Error fetching meal plans:', error)
      } finally {
        this.loading = false
      }
    },

    async createMealPlan(mealPlanData) {
      this.loading = true
      this.error = null
      
      try {
        console.log('Store: Creating meal plan with data:', mealPlanData)
        const response = await axios.post('/api/meal-plans/', mealPlanData)
        console.log('Store: Meal plan created successfully:', response.data)
        this.mealPlans.push(response.data)
        this.currentMealPlan = response.data
        return response.data
      } catch (error) {
        console.error('Store: Error creating meal plan:', error)
        console.error('Store: Error response data:', error.response?.data)
        console.error('Store: Error status:', error.response?.status)
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async generateMealPlan(request) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/meal-plans/generate', { request })
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error generating meal plan:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async editMealPlan(mealPlanId, editRequest) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/meal-plans/edit', {
          meal_plan_id: mealPlanId,
          edit_request: editRequest
        })
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error editing meal plan:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async switchMeal(mealPlanId, day, requirements = '') {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/meal-plans/switch-meal', {
          meal_plan_id: mealPlanId,
          day: day,
          requirements: requirements
        })
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error switching meal:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async switchMealWithRequirement(mealPlanId, day, requirement) {
      return this.switchMeal(mealPlanId, day, requirement)
    },

    // Generated plan editing (works with plan object directly, not saved plans)
    async editGeneratedPlan(generatedPlan, editRequest) {
      try {
        // Simply re-generate with the edit request
        const response = await axios.post('/api/meal-plans/generate', { 
          request: editRequest 
        })
        
        return response.data
      } catch (error) {
        this.error = error.message
        console.error('Error editing generated plan:', error)
        throw error
      }
    },

    async switchGeneratedMeal(generatedPlan, day, requirements = '') {
      try {
        // Generate a new plan with specific requirement for that day
        const searchQuery = requirements || `alternative meal for ${day}`
        const response = await axios.post('/api/meal-plans/generate', { 
          request: searchQuery 
        })
        
        // Take just the new recipe for that day
        const newMealPlan = { ...generatedPlan.meal_plan }
        const newRecipeId = response.data.meal_plan[day]?.lunch
        
        if (newRecipeId) {
          newMealPlan[day] = { lunch: newRecipeId }
        }
        
        return {
          ...generatedPlan,
          meal_plan: newMealPlan
        }
      } catch (error) {
        this.error = error.message
        console.error('Error switching generated meal:', error)
        throw error
      }
    },

    async switchGeneratedMealWithRequirement(generatedPlan, day, requirement) {
      return this.switchGeneratedMeal(generatedPlan, day, requirement)
    },

    async deleteMealPlan(mealPlanId) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/api/meal-plans/${mealPlanId}`)
        this.mealPlans = this.mealPlans.filter(plan => plan.id !== mealPlanId)
        if (this.currentMealPlan?.id === mealPlanId) {
          this.currentMealPlan = null
        }
      } catch (error) {
        this.error = error.message
        console.error('Error deleting meal plan:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentMealPlan(mealPlan) {
      this.currentMealPlan = mealPlan
    }
  }
})