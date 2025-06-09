<template>
  <div class="px-4 py-6 sm:px-0">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Welcome to ChefChat</h1>
      <p class="text-xl text-gray-600 mb-8">Your AI-powered recipe management and meal planning assistant</p>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <router-link to="/recipes" class="block">
          <div class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
            <h3 class="text-lg font-semibold mb-2">Manage Recipes</h3>
            <p class="text-gray-600">Add, edit, and organize your favorite recipes</p>
          </div>
        </router-link>
        
        <router-link to="/meal-plans" class="block">
          <div class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
            <h3 class="text-lg font-semibold mb-2">Plan Meals</h3>
            <p class="text-gray-600">Create weekly meal plans with AI assistance</p>
          </div>
        </router-link>
        
        <router-link to="/shopping-list" class="block">
          <div class="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
            <h3 class="text-lg font-semibold mb-2">Shopping Lists</h3>
            <p class="text-gray-600">Generate organized shopping lists from meal plans</p>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Component logic will go here
</script>