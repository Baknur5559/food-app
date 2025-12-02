<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const categories = ref([])
const token = localStorage.getItem('token')

// Загружаем категории и блюда при открытии страницы
onMounted(async () => {
  if (!token) return
  try {
    // Получаем категории (tenant_id=1 пока хардкод для теста)
    const response = await axios.get('http://213.148.7.107:8002/api/v1/menu/categories/?tenant_id=1')
    categories.value = response.data
    
    // Для каждой категории загружаем её блюда
    for (let cat of categories.value) {
      const itemsRes = await axios.get(`http://213.148.7.107:8002/api/v1/menu/items/${cat.id}?tenant_id=1`)
      cat.items = itemsRes.data
    }
  } catch (e) {
    console.error("Ошибка загрузки меню:", e)
  }
})
</script>

<template>
  <div class="p-6 bg-dark min-h-screen text-white">
    <h1 class="text-3xl font-bold text-primary mb-8">Управление Меню</h1>

    <div v-for="cat in categories" :key="cat.id" class="mb-10">
      <h2 class="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">{{ cat.name }}</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="item in cat.items" :key="item.id" class="bg-surface p-4 rounded-lg border border-gray-700 hover:border-primary transition">
          <div class="flex justify-between items-start">
            <h3 class="text-xl font-bold">{{ item.name }}</h3>
            <span class="text-primary font-bold">{{ item.price }} с.</span>
          </div>
          <p class="text-gray-400 text-sm mt-2">{{ item.description }}</p>
        </div>
        
        <div class="border-2 border-dashed border-gray-700 rounded-lg p-4 flex items-center justify-center cursor-pointer hover:border-primary text-gray-500 hover:text-primary transition h-32">
          + Добавить блюдо
        </div>
      </div>
    </div>
  </div>
</template>