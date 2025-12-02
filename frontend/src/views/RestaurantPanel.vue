<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router' // <-- Добавил импорт роутера

const router = useRouter() // <-- Инициализируем роутер
const currentUser = ref(null)
const categories = ref([])
const newCategory = ref('')
const token = localStorage.getItem('token')

// Состояние товара
const showProductModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const targetCategoryId = ref(null)

const newProduct = ref({
  name: '', price: '', description: '', imageFile: null, image_url: ''
})

// Функция выхода
const logout = () => {
  localStorage.removeItem('token')
  window.location.href = '/login'
}

// Загрузка
onMounted(async () => {
  if (!token) return window.location.href = '/login'
  try {
    const meRes = await axios.get('http://213.148.7.107:8002/api/v1/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    currentUser.value = meRes.data
    if (currentUser.value.tenant_id) loadMenu(currentUser.value.tenant_id)
  } catch (e) {
    console.error(e)
    logout()
  }
})

const loadMenu = async (tenantId) => {
  try {
    const res = await axios.get(`http://213.148.7.107:8002/api/v1/menu/categories/?tenant_id=${tenantId}`)
    categories.value = res.data
    for (let cat of categories.value) {
      const itemsRes = await axios.get(`http://213.148.7.107:8002/api/v1/menu/items/${cat.id}?tenant_id=${tenantId}`)
      cat.items = itemsRes.data
    }
  } catch (e) { console.error(e) }
}

const addCategory = async () => {
  if (!newCategory.value) return
  try {
    await axios.post('http://213.148.7.107:8002/api/v1/menu/categories/', 
      { name: newCategory.value, sort_order: 0 },
      { params: { tenant_id: currentUser.value.tenant_id } }
    )
    newCategory.value = ''
    loadMenu(currentUser.value.tenant_id)
  } catch (e) { alert(e.message) }
}

const openAddProductModal = (categoryId) => {
  isEditing.value = false
  targetCategoryId.value = categoryId
  newProduct.value = { name: '', price: '', description: '', imageFile: null, image_url: '' }
  showProductModal.value = true
}

const openEditProductModal = (item) => {
  isEditing.value = true
  editingId.value = item.id
  targetCategoryId.value = item.category_id
  newProduct.value = {
    name: item.name,
    price: item.price,
    description: item.description,
    image_url: item.image_url,
    imageFile: null
  }
  showProductModal.value = true
}

const deleteProduct = async (item) => {
  if (!confirm(`Удалить блюдо "${item.name}"?`)) return
  try {
    await axios.delete(`http://213.148.7.107:8002/api/v1/menu/items/${item.id}`)
    loadMenu(currentUser.value.tenant_id)
  } catch (e) { alert("Ошибка удаления") }
}

const handleFileUpload = (event) => {
  newProduct.value.imageFile = event.target.files[0]
}

const saveProduct = async () => {
  if (!newProduct.value.name || !newProduct.value.price) return alert("Заполните поля")
  
  const formData = new FormData()
  formData.append('name', newProduct.value.name)
  formData.append('price', newProduct.value.price)
  formData.append('description', newProduct.value.description || '')
  formData.append('category_id', targetCategoryId.value)
  
  if (newProduct.value.imageFile) {
    formData.append('file', newProduct.value.imageFile)
  }

  try {
    if (isEditing.value) {
      await axios.put(
        `http://213.148.7.107:8002/api/v1/menu/items/${editingId.value}`, 
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      alert("Блюдо обновлено!")
    } else {
      await axios.post(
        `http://213.148.7.107:8002/api/v1/menu/items/?tenant_id=${currentUser.value.tenant_id}`, 
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      alert("Блюдо добавлено!")
    }
    showProductModal.value = false
    loadMenu(currentUser.value.tenant_id)
  } catch (e) {
    alert("Ошибка: " + (e.response?.data?.detail || e.message))
  }
}
</script>

<template>
  <div class="min-h-screen bg-dark text-white flex">
    <aside class="w-64 bg-surface border-r border-gray-700 p-6 flex flex-col fixed h-full">
      <h1 class="text-2xl font-bold text-primary mb-10">Resto Admin</h1>
      <nav class="flex-1 space-y-4">
        <button 
          @click="router.push('/restaurant')" 
          class="w-full text-left block py-2 px-4 bg-gray-800 rounded text-white font-bold"
        >
          🍔 Меню
        </button>
        
        <button 
          @click="router.push('/restaurant/orders')" 
          class="w-full text-left block py-2 px-4 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition"
        >
          📦 Заказы
        </button>
      </nav>
      <div class="mt-auto pt-6 border-t border-gray-600">
        <p class="text-sm text-gray-400 mb-2">{{ currentUser?.full_name }}</p>
        <button @click="logout" class="text-red-400 hover:text-white text-sm">Выйти</button>
      </div>
    </aside>

    <main class="flex-1 p-8 ml-64">
      <header class="flex justify-between items-center mb-8">
        <h2 class="text-3xl font-bold">Управление Меню</h2>
      </header>

      <div class="flex gap-4 mb-10 p-4 bg-surface rounded-lg border border-gray-700">
        <input v-model="newCategory" placeholder="Новая категория" class="flex-1 p-3 bg-dark border border-gray-600 rounded text-white outline-none">
        <button @click="addCategory" class="bg-primary text-black font-bold px-6 rounded hover:bg-yellow-500">+ Категория</button>
      </div>

      <div v-for="cat in categories" :key="cat.id" class="mb-12">
        <div class="flex justify-between items-center border-b border-gray-700 pb-3 mb-4">
          <h3 class="text-2xl font-bold text-white">{{ cat.name }}</h3>
          <button @click="openAddProductModal(cat.id)" class="text-sm bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded text-white font-medium">+ Блюдо</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="item in cat.items" :key="item.id" class="bg-surface rounded-lg border border-gray-700 overflow-hidden hover:border-primary transition group relative">
            <div class="h-48 bg-gray-800 flex items-center justify-center relative">
              <span v-if="!item.image_url" class="text-gray-600 text-4xl">🥘</span>
              <img v-else :src="item.image_url" class="w-full h-full object-cover">
              <div class="absolute top-2 right-2 bg-black bg-opacity-70 px-2 py-1 rounded text-primary font-bold">{{ item.price }} с.</div>
            </div>
            <div class="p-4 pb-14">
              <h4 class="font-bold text-lg mb-1">{{ item.name }}</h4>
              <p class="text-gray-400 text-sm line-clamp-2">{{ item.description || 'Нет описания' }}</p>
            </div>
            <div class="absolute bottom-0 left-0 w-full p-2 bg-gray-800 flex justify-between border-t border-gray-700">
                <button @click="openEditProductModal(item)" class="flex-1 text-blue-300 hover:text-white text-sm py-1">✏️ Изм.</button>
                <div class="w-px bg-gray-600 mx-1"></div>
                <button @click="deleteProduct(item)" class="flex-1 text-red-300 hover:text-white text-sm py-1">🗑️ Удал.</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showProductModal" class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center p-4 z-50">
      <div class="bg-surface p-8 rounded-lg w-full max-w-lg border border-gray-600 shadow-2xl">
        <h2 class="text-2xl font-bold mb-6 text-white border-b border-gray-700 pb-2">
          {{ isEditing ? 'Редактирование' : 'Новое блюдо' }}
        </h2>
        <div class="flex flex-col gap-4 mb-6">
          <div><label class="block text-gray-400 text-sm mb-1">Название</label><input v-model="newProduct.name" class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Цена</label><input v-model="newProduct.price" type="number" class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"></div>
          <div><label class="block text-gray-400 text-sm mb-1">Описание</label><textarea v-model="newProduct.description" rows="3" class="w-full p-3 bg-dark border border-gray-600 rounded text-white focus:border-primary outline-none"></textarea></div>
          <div><label class="block text-gray-400 text-sm mb-1">Фото</label><input type="file" @change="handleFileUpload" class="w-full p-2 bg-dark border border-gray-600 rounded text-gray-300 text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-gray-700 file:text-white hover:file:bg-gray-600"></div>
        </div>
        <div class="flex justify-end gap-4">
          <button @click="showProductModal = false" class="px-4 py-2 text-gray-400 hover:text-white">Отмена</button>
          <button @click="saveProduct" class="bg-primary text-black font-bold px-6 py-2 rounded hover:bg-yellow-500">{{ isEditing ? 'Обновить' : 'Сохранить' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>