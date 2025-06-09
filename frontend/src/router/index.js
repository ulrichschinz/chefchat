import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Recipes from '../views/Recipes.vue'
import MealPlans from '../views/MealPlans.vue'
import ShoppingList from '../views/ShoppingList.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/recipes',
      name: 'recipes',
      component: Recipes
    },
    {
      path: '/recipes/:id',
      name: 'recipe-detail',
      component: () => import('../views/RecipeDetail.vue'),
      props: true
    },
    {
      path: '/meal-plans',
      name: 'meal-plans',
      component: MealPlans
    },
    {
      path: '/shopping-list',
      name: 'shopping-list',
      component: ShoppingList
    }
  ]
})

export default router