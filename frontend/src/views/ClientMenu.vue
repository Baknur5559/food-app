<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' // <-- Исправлено: один импорт
import axios from 'axios'
import { useCartStore } from '../stores/cart'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const restaurant = ref(null)
const loading = ref(true)
const error = ref('')

// Получаем slug из адресной строки (например, 'super-sushi')
const slug = route.params.slug

onMounted(async () => {
  try {
    // Делаем ПУБЛИЧНЫЙ запрос (без токена)
    const res = await axios.get(`http://213.148.7.107:8002/api/v1/client/${slug}`)
    restaurant.value = res.data
  } catch (e) {
    error.value = "Ресторан не найден или закрыт."
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white pb-20">
    
    <div v-if="loading" class="flex justify-center items-center h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-yellow-500"></div>
    </div>

    <div v-else-if="error" class="flex justify-center items-center h-screen text-red-500 text-xl font-bold">
      {{ error }}
    </div>

    <div v-else>
      <header class="bg-surface p-6 border-b border-gray-800 text-center sticky top-0 z-10 bg-gray-900 shadow-lg">
        <h1 class="text-2xl font-bold text-primary">{{ restaurant.name }}</h1>
        <p class="text-gray-400 text-sm mt-1">Доставка вкусной еды</p>
      </header>

      <div class="p-4 max-w-2xl mx-auto">
        <div v-for="cat in restaurant.categories" :key="cat.id" class="mb-8">
          <h2 class="text-xl font-bold mb-4 text-gray-200 border-l-4 border-primary pl-3">{{ cat.name }}</h2>
          
          <div class="space-y-4">
            <div v-for="item in cat.items" :key="item.id" class="bg-gray-800 p-4 rounded-xl flex gap-4 shadow-md">
              <div class="w-24 h-24 bg-gray-700 rounded-lg flex-shrink-0 overflow-hidden">
                <img v-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover">
                <span v-else class="flex items-center justify-center h-full text-2xl">🥘</span>
              </div>
              
              <div class="flex-1 flex flex-col justify-between">
                <div>
                  <h3 class="font-bold text-lg leading-tight">{{ item.name }}</h3>
                  <p class="text-gray-400 text-xs mt-1 line-clamp-2">{{ item.description }}</p>
                </div>
                
                <div class="flex justify-between items-center mt-3">
                  <span class="font-bold text-white">{{ item.price }} с.</span>
                  
                  <button 
                    @click="cart.addToCart(item, restaurant.id, restaurant.bot_username)"
                    class="bg-primary text-black px-4 py-1.5 rounded-full text-sm font-bold active:scale-95 transition"
                  >
                    + В корзину
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="cart.totalItems > 0" class="fixed bottom-4 left-4 right-4 max-w-2xl mx-auto">
        <button 
          @click="router.push('/checkout')"
          class="w-full bg-primary text-black p-4 rounded-xl font-bold shadow-xl flex justify-between items-center animate-bounce-short"
        >
          <span class="bg-black text-white px-3 py-1 rounded-full text-xs">{{ cart.totalItems }}</span>
          <span>Перейти к заказу</span>
          <span>{{ cart.totalAmount }} с.</span>
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-bounce-short {
  animation: bounce 0.3s ease-out;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
</style>