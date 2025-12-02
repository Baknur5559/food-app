<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const token = localStorage.getItem('token')
const currentUser = ref(null)

const orders = ref([])
const menuItems = ref([])
const loading = ref(false)

// Фильтры
const activeTab = ref('active')
const subTab = ref('all')
const searchQuery = ref('')

// Модалка
const showEditModal = ref(false)
const editingOrder = ref(null)
const itemSearchQuery = ref('')

// --- ФУНКЦИЯ ВЫХОДА (ИСПРАВЛЕНО) ---
const logout = () => {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

const init = async () => {
  if (!token) return window.location.href = '/login'
  try {
    loading.value = true
    const meRes = await axios.get('http://213.148.7.107:8002/api/v1/users/me', { headers: { Authorization: `Bearer ${token}` } })
    currentUser.value = meRes.data
    await Promise.all([loadOrders(), loadMenu(currentUser.value.tenant_id)])
  } catch (e) {
    console.error(e)
    logout()
  } finally {
    loading.value = false
  }
}

const loadOrders = async () => {
  const res = await axios.get('http://213.148.7.107:8002/api/v1/orders/', { headers: { Authorization: `Bearer ${token}` } })
  orders.value = res.data
}

const loadMenu = async (tenantId) => {
  const res = await axios.get(`http://213.148.7.107:8002/api/v1/menu/categories/?tenant_id=${tenantId}`)
  const allItems = []
  for (let cat of res.data) {
    const itemsRes = await axios.get(`http://213.148.7.107:8002/api/v1/menu/items/${cat.id}?tenant_id=${tenantId}`)
    allItems.push(...itemsRes.data)
  }
  menuItems.value = allItems
}

const statusFlow = {
  new: { label: 'Новый', color: 'bg-blue-600', btn: 'На кухню', next: 'cooking' },
  cooking: { label: 'Готовится', color: 'bg-yellow-600', btn: 'Готов / Курьер', next: 'transport' },
  transport: { label: 'В пути / Готов', color: 'bg-purple-600', btn: 'Завершить', next: 'done' },
  done: { label: 'Завершен', color: 'bg-green-600' },
  cancel: { label: 'Отменен', color: 'bg-red-900' }
}

const changeStatus = async (order, status) => {
  if (!confirm(`Перевести заказ в статус "${statusFlow[status]?.label || status}"?`)) return
  try {
    await axios.patch(`http://213.148.7.107:8002/api/v1/orders/${order.id}`, { status }, { headers: { Authorization: `Bearer ${token}` } })
    loadOrders()
  } catch (e) { alert(e.message) }
}

const filteredOrders = computed(() => {
  let list = orders.value
  if (activeTab.value === 'active') {
    list = list.filter(o => ['new', 'cooking', 'transport'].includes(o.status))
    if (subTab.value !== 'all') list = list.filter(o => o.status === subTab.value)
  } else {
    list = list.filter(o => ['done', 'cancel'].includes(o.status))
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o => o.client_name.toLowerCase().includes(q) || o.client_phone.includes(q) || String(o.id).includes(q))
  }
  return list
})

const counts = computed(() => {
  const active = orders.value.filter(o => ['new', 'cooking', 'transport'].includes(o.status))
  return {
    new: active.filter(o => o.status === 'new').length,
    cooking: active.filter(o => o.status === 'cooking').length,
    transport: active.filter(o => o.status === 'transport').length
  }
})

// --- РЕДАКТИРОВАНИЕ ---
const openEdit = (order) => {
  editingOrder.value = JSON.parse(JSON.stringify(order))
  showEditModal.value = true
}

const saveClientData = async () => {
  try {
    await axios.patch(`http://213.148.7.107:8002/api/v1/orders/${editingOrder.value.id}`, 
      { 
        client_name: editingOrder.value.client_name,
        client_phone: editingOrder.value.client_phone,
        delivery_address: editingOrder.value.delivery_address,
        comment: editingOrder.value.comment,
        order_type: editingOrder.value.order_type
      },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    alert("Данные сохранены")
    showEditModal.value = false
    loadOrders()
  } catch (e) { alert(e.message) }
}

const removeItem = async (item) => {
  if (!confirm("Удалить позицию?")) return
  try {
    await axios.delete(`http://213.148.7.107:8002/api/v1/orders/${editingOrder.value.id}/items/${item.id}`, { headers: { Authorization: `Bearer ${token}` } })
    const idx = editingOrder.value.items.findIndex(i => i.id === item.id)
    if (idx !== -1) editingOrder.value.items.splice(idx, 1)
    loadOrders()
  } catch (e) { alert(e.message) }
}

const foundItems = computed(() => {
  if (!itemSearchQuery.value) return menuItems.value.slice(0, 5)
  return menuItems.value.filter(i => i.name.toLowerCase().includes(itemSearchQuery.value.toLowerCase())).slice(0, 5)
})

const addItemToOrder = async (menuItem) => {
  try {
    await axios.post(`http://213.148.7.107:8002/api/v1/orders/${editingOrder.value.id}/items`, 
      { menu_item_id: menuItem.id, quantity: 1 },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    const res = await axios.get('http://213.148.7.107:8002/api/v1/orders/', { headers: { Authorization: `Bearer ${token}` } })
    const updatedOrder = res.data.find(o => o.id === editingOrder.value.id)
    if (updatedOrder) editingOrder.value.items = updatedOrder.items
    itemSearchQuery.value = ''
    loadOrders()
  } catch (e) { alert(e.message) }
}

onMounted(() => {
  init()
  setInterval(loadOrders, 10000)
})
</script>

<template>
  <div class="min-h-screen bg-dark text-white flex">
    
    <aside class="w-64 bg-surface border-r border-gray-700 p-6 flex flex-col fixed h-full z-20">
      <h1 class="text-2xl font-bold text-primary mb-10">Resto Admin</h1>
      <nav class="flex-1 space-y-4">
        <button @click="router.push('/restaurant')" class="w-full text-left block py-2 px-4 text-gray-400 hover:text-white hover:bg-gray-800 rounded">🍔 Меню</button>
        <button @click="router.push('/restaurant/orders')" class="w-full text-left block py-2 px-4 bg-gray-800 rounded text-white font-bold">📦 Заказы</button>
      </nav>
      <div class="mt-auto pt-6 border-t border-gray-600">
        <button @click="logout" class="text-red-400 hover:text-white text-sm">Выйти</button>
      </div>
    </aside>

    <main class="flex-1 p-8 ml-64">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">📦 Управление заказами</h1>
        <div class="relative w-96">
          <input v-model="searchQuery" placeholder="🔍 Поиск..." class="w-full p-3 bg-surface border border-gray-700 rounded-lg text-white outline-none focus:border-primary">
        </div>
      </div>

      <div class="flex gap-6 border-b border-gray-700 mb-6">
        <button @click="activeTab = 'active'" :class="activeTab === 'active' ? 'text-primary border-b-2 border-primary' : 'text-gray-400'" class="pb-3 text-lg font-bold transition">🔥 Активные</button>
        <button @click="activeTab = 'history'" :class="activeTab === 'history' ? 'text-primary border-b-2 border-primary' : 'text-gray-400'" class="pb-3 text-lg font-bold transition">📜 История</button>
      </div>

      <div v-if="activeTab === 'active'" class="flex gap-2 mb-6">
        <button @click="subTab = 'all'" :class="subTab === 'all' ? 'bg-gray-700 text-white' : 'bg-transparent text-gray-500 border border-gray-700'" class="px-4 py-1.5 rounded-full text-sm font-bold transition">Все</button>
        <button @click="subTab = 'new'" :class="subTab === 'new' ? 'bg-blue-600 text-white' : 'bg-transparent text-gray-500 border border-gray-700'" class="px-4 py-1.5 rounded-full text-sm font-bold transition flex items-center gap-2">Новые <span v-if="counts.new" class="bg-white text-blue-600 px-1.5 rounded-full text-xs">{{ counts.new }}</span></button>
        <button @click="subTab = 'cooking'" :class="subTab === 'cooking' ? 'bg-yellow-600 text-white' : 'bg-transparent text-gray-500 border border-gray-700'" class="px-4 py-1.5 rounded-full text-sm font-bold transition flex items-center gap-2">Готовятся <span v-if="counts.cooking" class="bg-white text-yellow-600 px-1.5 rounded-full text-xs">{{ counts.cooking }}</span></button>
        <button @click="subTab = 'transport'" :class="subTab === 'transport' ? 'bg-purple-600 text-white' : 'bg-transparent text-gray-500 border border-gray-700'" class="px-4 py-1.5 rounded-full text-sm font-bold transition flex items-center gap-2">В пути <span v-if="counts.transport" class="bg-white text-purple-600 px-1.5 rounded-full text-xs">{{ counts.transport }}</span></button>
      </div>

      <div v-if="filteredOrders.length === 0" class="text-center py-20 text-gray-500 text-xl">Список пуст 😴</div>

      <div class="grid gap-4">
        <div v-for="order in filteredOrders" :key="order.id" class="bg-surface p-5 rounded-lg border border-gray-700 shadow-lg relative overflow-hidden group">
          <div class="flex justify-between items-start mb-4 border-b border-gray-700 pb-3">
            <div>
              <div class="flex items-center gap-3 mb-2">
                <span :class="statusFlow[order.status]?.color || 'bg-gray-600'" class="px-3 py-1 rounded text-xs font-bold uppercase">{{ statusFlow[order.status]?.label || order.status }}</span>
                <span class="text-gray-400 text-sm font-mono">#{{ order.id }}</span>
              </div>
              <h3 class="text-xl font-bold">{{ order.client_name }}</h3>
              <div class="text-sm text-primary">{{ order.client_phone }}</div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold">{{ order.total_amount }} с.</div>
              <div class="text-xs text-gray-400 uppercase mt-1">{{ order.order_type === 'delivery' ? '🚗 Доставка' : '🏃 Самовывоз' }}</div>
            </div>
          </div>

          <div class="mb-4 text-sm text-gray-300">
            <div v-for="item in order.items" :key="item.id" class="flex justify-between py-1 border-b border-gray-800 last:border-0">
              <span>{{ item.name }} x{{ item.quantity }}</span>
            </div>
            <div v-if="order.delivery_address" class="mt-3 text-gray-400 italic">📍 {{ order.delivery_address }}</div>
          </div>

          <div class="flex gap-3 mt-4">
            <button v-if="statusFlow[order.status]?.next" @click="changeStatus(order, statusFlow[order.status].next)" class="flex-1 bg-green-700 hover:bg-green-600 text-white font-bold py-2.5 rounded transition text-sm uppercase tracking-wide">{{ statusFlow[order.status].btn }} →</button>
            <button @click="openEdit(order)" class="px-4 bg-gray-700 hover:bg-gray-600 rounded font-bold text-gray-200">✏️</button>
            <button v-if="!['done', 'cancel'].includes(order.status)" @click="changeStatus(order, 'cancel')" class="px-4 bg-red-900 hover:bg-red-800 rounded font-bold text-red-200">✕</button>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
      <div class="bg-surface rounded-xl w-full max-w-4xl border border-gray-600 shadow-2xl flex flex-col md:flex-row overflow-hidden max-h-[90vh]">
        
        <div class="w-full md:w-1/3 bg-gray-800 p-6 border-r border-gray-700 flex flex-col overflow-y-auto">
          <h3 class="text-lg font-bold text-white mb-6 border-b border-gray-600 pb-2">👤 Клиент</h3>
          
          <div class="mb-4">
            <label class="text-xs text-gray-400 block mb-1">Тип заказа</label>
            <div class="flex gap-2">
              <button @click="editingOrder.order_type = 'delivery'" :class="editingOrder.order_type === 'delivery' ? 'bg-primary text-black' : 'bg-dark border border-gray-600 text-gray-400'" class="flex-1 py-1.5 rounded text-sm font-bold transition">🚗 Доставка</button>
              <button @click="editingOrder.order_type = 'pickup'" :class="editingOrder.order_type === 'pickup' ? 'bg-primary text-black' : 'bg-dark border border-gray-600 text-gray-400'" class="flex-1 py-1.5 rounded text-sm font-bold transition">🏃 Самовывоз</button>
            </div>
          </div>

          <div class="space-y-4 flex-1">
            <div><label class="text-xs text-gray-400 block mb-1">Имя</label><input v-model="editingOrder.client_name" class="w-full p-2 bg-dark border border-gray-600 rounded text-white text-sm"></div>
            <div><label class="text-xs text-gray-400 block mb-1">Телефон</label><input v-model="editingOrder.client_phone" class="w-full p-2 bg-dark border border-gray-600 rounded text-white text-sm"></div>
            <div><label class="text-xs text-gray-400 block mb-1">Адрес</label><textarea v-model="editingOrder.delivery_address" rows="3" class="w-full p-2 bg-dark border border-gray-600 rounded text-white text-sm"></textarea></div>
            <div><label class="text-xs text-gray-400 block mb-1">Комментарий</label><textarea v-model="editingOrder.comment" rows="2" class="w-full p-2 bg-dark border border-gray-600 rounded text-white text-sm"></textarea></div>
          </div>
          <button @click="saveClientData" class="w-full mt-6 bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 rounded transition">Сохранить данные</button>
        </div>

        <div class="w-full md:w-2/3 p-6 bg-surface flex flex-col">
          <div class="flex justify-between items-center mb-4 border-b border-gray-700 pb-2">
            <h3 class="text-lg font-bold text-white">🛒 Состав заказа</h3>
            <button @click="showEditModal = false" class="text-gray-400 hover:text-white text-2xl">✕</button>
          </div>
          <div class="flex-1 overflow-y-auto mb-4 pr-2">
            <table class="w-full text-left text-sm text-gray-300">
              <thead><tr class="text-gray-500 border-b border-gray-700"><th class="pb-2">Блюдо</th><th class="pb-2">Цена</th><th class="pb-2">Действие</th></tr></thead>
              <tbody>
                <tr v-for="item in editingOrder.items" :key="item.id" class="border-b border-gray-800">
                  <td class="py-3 font-medium text-white">{{ item.name }} <span class="text-gray-500 text-xs">x{{ item.quantity }}</span></td>
                  <td class="py-3">{{ item.price * item.quantity }} с.</td>
                  <td class="py-3"><button @click="removeItem(item)" class="text-red-400 hover:text-red-300 bg-red-900/30 p-1.5 rounded">🗑️</button></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="bg-dark p-4 rounded border border-gray-600">
            <label class="text-xs text-gray-400 block mb-2 font-bold">ДОБАВИТЬ БЛЮДО:</label>
            <input v-model="itemSearchQuery" placeholder="Начни вводить название..." class="w-full p-3 bg-surface border border-gray-500 rounded text-white outline-none mb-3 focus:border-primary">
            <div class="grid grid-cols-2 gap-2">
              <button v-for="item in foundItems" :key="item.id" @click="addItemToOrder(item)" class="text-left bg-surface border border-gray-700 p-2 rounded hover:border-primary hover:text-primary transition flex justify-between group">
                <span class="truncate">{{ item.name }}</span>
                <span class="text-gray-500 group-hover:text-primary font-bold">{{ item.price }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>