<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import axios from 'axios'

const cart = useCartStore()
const router = useRouter()

const form = ref({
  client_name: '', client_phone: '', delivery_address: '',
  order_type: 'delivery', payment_method: 'cash', comment: ''
})

const loading = ref(false)
const showSuccessModal = ref(false)
const createdOrderId = ref(null)

const submitOrder = async () => {
  if (!cart.restaurantId) {
    alert("Ошибка: Неизвестный ресторан. Пожалуйста, вернитесь в меню.")
    router.push('/')
    return
  }
  if (!form.value.client_name || !form.value.client_phone) return alert("Введите Имя и Телефон")
  if (form.value.order_type === 'delivery' && !form.value.delivery_address) return alert("Нужен Адрес")
  if (cart.items.length === 0) return alert("Корзина пуста")

  loading.value = true
  try {
    const payload = {
      tenant_id: cart.restaurantId,
      client_name: form.value.client_name,
      client_phone: form.value.client_phone,
      delivery_address: form.value.delivery_address,
      order_type: form.value.order_type,
      payment_method: form.value.payment_method,
      comment: form.value.comment,
      items: cart.items.map(i => ({ menu_item_id: i.id, quantity: i.quantity }))
    }

    const res = await axios.post('http://213.148.7.107:8002/api/v1/client/orders', payload)
    
    // УСПЕХ: Показываем модалку
    createdOrderId.value = res.data.id
    showSuccessModal.value = true
    
    // Чистим корзину (товары), но данные ресторана оставляем
    cart.clearCart()
    
  } catch (e) {
    alert("Ошибка заказа: " + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

// Переход в телеграм
const openTelegram = () => {
  if (cart.botUsername) {
    // Ссылка с DeepLink: start=order_123
    window.location.href = `https://t.me/${cart.botUsername}?start=order_${createdOrderId.value}`
  } else {
    alert("Бот не настроен для этого ресторана.")
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white p-6 pb-24">
    
    <div class="flex items-center mb-6">
      <button @click="router.go(-1)" class="text-gray-400 text-2xl mr-4">←</button>
      <h1 class="text-2xl font-bold">Оформление</h1>
    </div>

    <div class="bg-gray-800 rounded-lg p-4 mb-6">
      <h3 class="text-gray-400 text-sm mb-2 uppercase font-bold">Ваш заказ</h3>
      <div v-for="item in cart.items" :key="item.id" class="flex justify-between py-2 border-b border-gray-700 last:border-0">
        <span>{{ item.name }} <span class="text-primary text-xs">x{{ item.quantity }}</span></span>
        <span>{{ item.price * item.quantity }} с.</span>
      </div>
      <div class="flex justify-between mt-4 text-xl font-bold">
        <span>Итого:</span><span class="text-primary">{{ cart.totalAmount }} с.</span>
      </div>
    </div>

    <div class="space-y-4">
      <div class="bg-gray-800 p-2 rounded-lg flex">
        <button @click="form.order_type = 'delivery'" :class="form.order_type === 'delivery' ? 'bg-primary text-black' : 'text-gray-400'" class="flex-1 py-2 rounded-md font-bold transition">🚗 Доставка</button>
        <button @click="form.order_type = 'pickup'" :class="form.order_type === 'pickup' ? 'bg-primary text-black' : 'text-gray-400'" class="flex-1 py-2 rounded-md font-bold transition">🏃 Самовывоз</button>
      </div>

      <input v-model="form.client_name" placeholder="Ваше имя" class="w-full p-4 bg-gray-800 rounded-lg text-white outline-none focus:ring-2 ring-primary">
      <input v-model="form.client_phone" type="tel" placeholder="Телефон (0555...)" class="w-full p-4 bg-gray-800 rounded-lg text-white outline-none focus:ring-2 ring-primary">
      <textarea v-if="form.order_type === 'delivery'" v-model="form.delivery_address" placeholder="Адрес доставки..." rows="2" class="w-full p-4 bg-gray-800 rounded-lg text-white outline-none focus:ring-2 ring-primary"></textarea>
      <textarea v-model="form.comment" placeholder="Комментарий..." class="w-full p-4 bg-gray-800 rounded-lg text-white outline-none"></textarea>

      <div>
        <h3 class="text-gray-400 text-sm mb-2 uppercase font-bold mt-4">Оплата</h3>
        <div class="flex gap-3">
          <label class="flex-1 bg-gray-800 p-3 rounded-lg flex items-center gap-3 cursor-pointer border border-transparent has-[:checked]:border-primary">
            <input type="radio" value="cash" v-model="form.payment_method" class="accent-primary"><span>💵 Наличные</span>
          </label>
          <label class="flex-1 bg-gray-800 p-3 rounded-lg flex items-center gap-3 cursor-pointer border border-transparent has-[:checked]:border-primary">
            <input type="radio" value="mbank" v-model="form.payment_method" class="accent-primary"><span>📱 MBank</span>
          </label>
        </div>
      </div>
    </div>

    <div class="fixed bottom-4 left-4 right-4 max-w-2xl mx-auto">
      <button @click="submitOrder" :disabled="loading" class="w-full bg-primary text-black p-4 rounded-xl font-bold shadow-xl text-lg disabled:opacity-50">
        {{ loading ? 'Отправка...' : `Заказать на ${cart.totalAmount} с.` }}
      </button>
    </div>

    <div v-if="showSuccessModal" class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
      <div class="bg-gray-800 p-8 rounded-2xl w-full max-w-md text-center border border-gray-700 shadow-2xl animate-fade-in">
        <div class="text-6xl mb-4">🎉</div>
        <h2 class="text-2xl font-bold text-white mb-2">Заказ №{{ createdOrderId }} принят!</h2>
        <p class="text-gray-400 mb-8">Спасибо, {{ form.client_name }}! Мы уже начали готовить.</p>
        
        <div class="space-y-3">
          <button 
            @click="openTelegram"
            class="w-full bg-[#0088cc] hover:bg-[#0077b5] text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 transition transform hover:scale-105"
          >
            <span class="text-2xl">✈️</span>
            <span>Следить в Telegram</span>
          </button>
          
          <p class="text-xs text-gray-500 mt-2">Там статус заказа и ваши бонусы</p>

          <button @click="router.go(-1)" class="w-full text-gray-400 hover:text-white py-3 mt-4 font-medium">
            Вернуться в меню
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
</style>