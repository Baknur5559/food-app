import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const savedCart = localStorage.getItem('cart')
  const initialItems = savedCart ? JSON.parse(savedCart).items : []
  const initialRestId = savedCart ? JSON.parse(savedCart).restaurantId : null
  // НОВОЕ ПОЛЕ:
  const initialBotName = savedCart ? JSON.parse(savedCart).botUsername : null

  const items = ref(initialItems)
  const restaurantId = ref(initialRestId)
  const botUsername = ref(initialBotName) // Храним имя бота

  watch([items, restaurantId, botUsername], () => {
    localStorage.setItem('cart', JSON.stringify({
      items: items.value,
      restaurantId: restaurantId.value,
      botUsername: botUsername.value
    }))
  }, { deep: true })

  // Обновили функцию добавления: теперь она принимает и имя бота
  const addToCart = (product, tenantId, botName) => {
    if (restaurantId.value && restaurantId.value !== tenantId) {
      if (!confirm("Очистить корзину? Вы перешли в другой ресторан.")) return
      items.value = []
    }
    restaurantId.value = tenantId
    botUsername.value = botName // Запоминаем бота

    const existing = items.value.find(i => i.id === product.id)
    if (existing) {
      existing.quantity++
    } else {
      items.value.push({ ...product, quantity: 1 })
    }
  }

  const removeFromCart = (productId) => {
    const idx = items.value.findIndex(i => i.id === productId)
    if (idx === -1) return
    if (items.value[idx].quantity > 1) {
      items.value[idx].quantity--
    } else {
      items.value.splice(idx, 1)
    }
  }

  const clearCart = () => {
    items.value = []
    // restaurantId и botUsername НЕ стираем сразу, чтобы показать ссылку на бота
    // Но items чистим
    localStorage.setItem('cart', JSON.stringify({
      items: [],
      restaurantId: restaurantId.value,
      botUsername: botUsername.value
    }))
  }

  const totalAmount = computed(() => {
    return items.value.reduce((sum, i) => sum + (i.price * i.quantity), 0)
  })

  const totalItems = computed(() => {
    return items.value.reduce((sum, i) => sum + i.quantity, 0)
  })

  return { items, addToCart, removeFromCart, clearCart, totalAmount, totalItems, restaurantId, botUsername }
})