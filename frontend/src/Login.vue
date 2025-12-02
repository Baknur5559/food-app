<script setup>
import { ref } from 'vue'
import axios from 'axios'

const phone = ref('')
const password = ref('')
const token = ref('')
const error = ref('')

const handleLogin = async () => {
  try {
    error.value = ''
    // Отправляем данные на твой FastAPI сервер (порт 8002)
    const formData = new URLSearchParams()
    formData.append('username', phone.value)
    formData.append('password', password.value)

    const response = await axios.post('http://213.148.7.107:8002/api/v1/login/access-token', formData)
    
    // Сохраняем токен в память браузера
    localStorage.setItem('token', response.data.access_token)
    // Перекидываем на главную
    window.location.href = '/check-role'
  } catch (e) {
    console.error(e)
    error.value = "Ошибка входа. Проверьте логин и пароль."
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-dark">
    
    <div v-if="!token" class="bg-surface p-8 rounded-lg shadow-lg w-96 border border-gray-700">
      <h1 class="text-2xl font-bold text-primary mb-6 text-center">FoodTech Login</h1>
      
      <div class="mb-4">
        <label class="block text-gray-400 mb-2">Телефон</label>
        <input 
          v-model="phone" 
          type="text" 
          placeholder="996555..." 
          class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"
        >
      </div>

      <div class="mb-6">
        <label class="block text-gray-400 mb-2">Пароль</label>
        <input 
          v-model="password" 
          type="password" 
          class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"
        >
      </div>

      <button 
        @click="handleLogin"
        class="w-full bg-primary text-black font-bold p-3 rounded hover:bg-yellow-500 transition"
      >
        Войти
      </button>

      <p v-if="error" class="text-red-500 mt-4 text-center">{{ error }}</p>
    </div>

    <div v-else class="text-center">
      <h2 class="text-3xl text-green-500 font-bold mb-4">Доступ разрешен! 🔓</h2>
      <p class="text-gray-400 break-all max-w-lg mx-auto">Твой токен: {{ token }}</p>
    </div>

  </div>
</template>