<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tenants = ref([])
const token = localStorage.getItem('token')

// Функция выхода
const logout = () => {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

// Формы Компаний
// ДОБАВИЛ bot_username сюда
const newTenant = ref({ name: '', slug: '', branch_limit: 1, custom_domain: '', telegram_bot_token: '', bot_username: '', active_until: '' })
const editingTenant = ref(null)
const showEditModal = ref(false)

// Формы Юзеров (ВОССТАНОВЛЕНО)
const editingUser = ref(null)
const showUserEditModal = ref(false)
const currentUserTenant = ref(null)

// Загрузка
const loadTenants = async () => {
  try {
    const response = await axios.get('http://213.148.7.107:8002/api/v1/tenants/')
    tenants.value = response.data.map(t => ({
      ...t,
      users: [],
      newOwner: { phone: '', password: '', full_name: '' },
      showOwnerForm: false
    }))
    for (let t of tenants.value) loadUsersForTenant(t)
  } catch (e) { console.error(e) }
}

const loadUsersForTenant = async (tenant) => {
  try {
    const res = await axios.get(`http://213.148.7.107:8002/api/v1/users/?tenant_id=${tenant.id}`)
    tenant.users = res.data
  } catch (e) { console.error(e) }
}

// --- КОМПАНИИ ---
const createTenant = async () => {
  if (!newTenant.value.name) return
  const payload = { ...newTenant.value }
  if (!payload.active_until) delete payload.active_until
  try {
    await axios.post('http://213.148.7.107:8002/api/v1/tenants/', payload)
    alert("Компания создана!")
    // Очищаем форму (включая bot_username)
    newTenant.value = { name: '', slug: '', branch_limit: 1, custom_domain: '', telegram_bot_token: '', bot_username: '', active_until: '' }
    loadTenants()
  } catch (e) { alert(e.message) }
}

const openEditModal = (t) => { editingTenant.value = { ...t }; showEditModal.value = true }

const updateTenant = async () => {
  try {
    const payload = { ...editingTenant.value }
    delete payload.id; delete payload.users; delete payload.newOwner; delete payload.showOwnerForm
    if (!payload.active_until) payload.active_until = null 
    await axios.put(`http://213.148.7.107:8002/api/v1/tenants/${editingTenant.value.id}`, payload)
    alert("Настройки обновлены!")
    showEditModal.value = false
    loadTenants()
  } catch (e) { alert(e.message) }
}

// --- СОТРУДНИКИ (ВОССТАНОВЛЕНО) ---
const createOwner = async (tenant) => {
  const user = tenant.newOwner
  if (!user.phone || !user.password) return alert("Заполните данные")
  try {
    await axios.post('http://213.148.7.107:8002/api/v1/users/', {
      phone: user.phone, password: user.password, full_name: user.full_name,
      is_active: true, is_superuser: false, tenant_id: tenant.id
    })
    alert(`Сотрудник создан!`)
    tenant.newOwner = { phone: '', password: '', full_name: '' }
    tenant.showOwnerForm = false
    loadUsersForTenant(tenant)
  } catch (e) { alert(e.response?.data?.detail || e.message) }
}

const deleteUser = async (user, tenant) => {
  if (!confirm(`Удалить сотрудника ${user.full_name}?`)) return
  try {
    await axios.delete(`http://213.148.7.107:8002/api/v1/users/${user.id}`)
    loadUsersForTenant(tenant)
  } catch (e) { alert("Ошибка удаления: " + e.message) }
}

const openUserEditModal = (user, tenant) => {
  editingUser.value = { ...user, password: '' }
  currentUserTenant.value = tenant
  showUserEditModal.value = true
}

const updateUser = async () => {
  try {
    const payload = { ...editingUser.value }
    if (!payload.password) delete payload.password
    
    await axios.put(`http://213.148.7.107:8002/api/v1/users/${editingUser.value.id}`, payload)
    alert("Сотрудник обновлен!")
    showUserEditModal.value = false
    loadUsersForTenant(currentUserTenant.value)
  } catch (e) { alert(e.response?.data?.detail || e.message) }
}

onMounted(() => { if (token) loadTenants() })
</script>

<template>
  <div class="p-6 bg-dark min-h-screen text-white relative">
    <div class="max-w-6xl mx-auto">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-primary">🏢 Компании и Владельцы</h1>
        <button @click="logout" class="text-gray-400 hover:text-white">Выйти</button>
      </div>

      <div class="bg-surface p-6 rounded-lg border border-gray-700 mb-10 shadow-lg">
        <h2 class="text-xl font-bold mb-6 text-primary border-b border-gray-700 pb-2">Новый Клиент</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div><label class="block text-gray-400 text-sm mb-1">Название</label><input v-model="newTenant.name" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Slug</label><input v-model="newTenant.slug" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Бот Токен</label><input v-model="newTenant.telegram_bot_token" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Имя Бота (без @)</label><input v-model="newTenant.bot_username" placeholder="SuperSushiBot" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          
          <div><label class="block text-gray-400 text-sm mb-1">Подписка до</label><input v-model="newTenant.active_until" type="date" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
        </div>
        <button @click="createTenant" class="w-full bg-primary text-black font-bold py-3 rounded hover:bg-yellow-500">Создать Компанию</button>
      </div>

      <div class="grid grid-cols-1 gap-6">
        <div v-for="t in tenants" :key="t.id" class="bg-surface p-5 rounded-lg border border-gray-700">
          
          <div class="flex justify-between items-start mb-6 border-b border-gray-700 pb-4">
            <div>
              <h3 class="text-2xl font-bold text-white">{{ t.name }}</h3>
              <p class="text-gray-400 text-sm">Домен: {{ t.custom_domain || 'Нет' }} | Бот: {{ t.bot_username || 'Нет' }}</p>
            </div>
            <button @click="openEditModal(t)" class="bg-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-600 transition text-white font-medium">
              ✏️ Настройки
            </button>
          </div>

          <div class="mb-4">
            <h4 class="text-sm font-bold text-gray-400 uppercase mb-2">Команда:</h4>
            <div v-if="t.users.length === 0" class="text-gray-500 text-sm italic mb-2">Нет сотрудников</div>
            
            <div v-for="u in t.users" :key="u.id" class="flex justify-between items-center bg-dark p-2 rounded mb-2 border border-gray-600">
              <div>
                <span class="text-white font-bold">{{ u.full_name }}</span>
                <span class="text-gray-400 text-xs ml-2">({{ u.phone }})</span>
              </div>
              <div class="flex gap-2">
                <button @click="openUserEditModal(u, t)" class="text-xs bg-blue-900 text-blue-200 px-2 py-1 rounded hover:bg-blue-800">✏️ Изм.</button>
                <button @click="deleteUser(u, t)" class="text-xs bg-red-900 text-red-200 px-2 py-1 rounded hover:bg-red-800">🗑️</button>
              </div>
            </div>
          </div>

          <div v-if="!t.showOwnerForm">
            <button @click="t.showOwnerForm = true" class="w-full py-2 border border-dashed border-gray-600 text-gray-400 rounded hover:border-primary hover:text-primary transition">
              + Добавить сотрудника
            </button>
          </div>

          <div v-else class="bg-dark p-4 rounded border border-gray-500">
            <h4 class="text-white font-bold mb-3">Новый пользователь</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
              <input v-model="t.newOwner.full_name" placeholder="Имя" class="p-2 bg-surface border border-gray-600 rounded text-white text-sm">
              <input v-model="t.newOwner.phone" placeholder="Телефон" class="p-2 bg-surface border border-gray-600 rounded text-white text-sm">
              <input v-model="t.newOwner.password" placeholder="Пароль" class="p-2 bg-surface border border-gray-600 rounded text-white text-sm">
            </div>
            <div class="flex gap-3">
              <button @click="createOwner(t)" class="bg-primary text-black font-bold px-4 py-2 rounded text-sm">Добавить</button>
              <button @click="t.showOwnerForm = false" class="text-gray-400 px-3">Отмена</button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center p-4 z-50">
      <div class="bg-surface p-8 rounded-lg w-full max-w-2xl border border-gray-600">
        <h2 class="text-2xl font-bold mb-6 text-white">Настройки: {{ editingTenant.name }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div><label class="block text-gray-400 text-sm mb-1">Название</label><input v-model="editingTenant.name" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Slug</label><input v-model="editingTenant.slug" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Домен</label><input v-model="editingTenant.custom_domain" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Бот Токен</label><input v-model="editingTenant.telegram_bot_token" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Имя Бота</label><input v-model="editingTenant.bot_username" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          
          <div><label class="block text-gray-400 text-sm mb-1">Подписка до</label><input v-model="editingTenant.active_until" type="date" class="w-full p-3 bg-dark border border-gray-600 rounded text-white"></div>
          <div class="flex items-center gap-3 mt-6">
            <button @click="editingTenant.is_active = !editingTenant.is_active" :class="editingTenant.is_active ? 'bg-green-600' : 'bg-red-600'" class="px-4 py-2 rounded text-white font-bold w-full">{{ editingTenant.is_active ? 'АКТИВЕН' : 'ЗАБЛОКИРОВАН' }}</button>
          </div>
        </div>
        <div class="flex justify-end gap-4 border-t border-gray-700 pt-4">
          <button @click="showEditModal = false" class="px-6 py-3 text-gray-400 hover:text-white">Отмена</button>
          <button @click="updateTenant" class="bg-primary text-black font-bold px-6 py-3 rounded hover:bg-yellow-500">Сохранить</button>
        </div>
      </div>
    </div>

    <div v-if="showUserEditModal" class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center p-4 z-50">
      <div class="bg-surface p-8 rounded-lg w-full max-w-md border border-gray-600 shadow-2xl">
        <h2 class="text-xl font-bold mb-6 text-white border-b border-gray-700 pb-2">
          Сотрудник: {{ editingUser.full_name }}
        </h2>
        
        <div class="flex flex-col gap-4 mb-6">
          <div><label class="block text-gray-400 text-sm mb-1">Имя</label><input v-model="editingUser.full_name" class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Телефон (Логин)</label><input v-model="editingUser.phone" class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Новый пароль</label><input v-model="editingUser.password" placeholder="Оставьте пустым, если не меняете" class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"></div>
          <div class="flex items-center gap-3">
             <label class="text-gray-400">Доступ:</label>
             <button @click="editingUser.is_active = !editingUser.is_active" :class="editingUser.is_active ? 'bg-green-600' : 'bg-red-600'" class="px-3 py-1 rounded text-white text-xs font-bold">{{ editingUser.is_active ? 'РАЗРЕШЕН' : 'ЗАПРЕЩЕН' }}</button>
          </div>
        </div>

        <div class="flex justify-end gap-4 border-t border-gray-700 pt-4">
          <button @click="showUserEditModal = false" class="px-4 py-2 text-gray-400 hover:text-white">Отмена</button>
          <button @click="updateUser" class="bg-primary text-black font-bold px-6 py-2 rounded hover:bg-yellow-500">Сохранить</button>
        </div>
      </div>
    </div>

  </div>
</template>