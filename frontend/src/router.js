import { createRouter, createWebHistory } from 'vue-router'
import Tenants from './views/Tenants.vue'
import RestaurantPanel from './views/RestaurantPanel.vue'
import Orders from './views/Orders.vue'
import Login from './Login.vue'
import Checkout from './views/Checkout.vue'
import ClientMenu from './views/ClientMenu.vue'
import axios from 'axios'

const routes = [
  { path: '/', redirect: '/login' },
  
  // Технические страницы ВЫШЕ, чем /:slug
  { path: '/check-role', component: { template: '<div>Загрузка...</div>' } },
  { path: '/login', component: Login },
  { path: '/checkout', component: Checkout },
  
  // Админки
  { path: '/admin', component: Tenants, meta: { requiresAuth: true, role: 'superuser' } },
  { path: '/restaurant', component: RestaurantPanel, meta: { requiresAuth: true, role: 'owner' } },
  { path: '/restaurant/orders', component: Orders, meta: { requiresAuth: true, role: 'owner' } },
  
  // Витрина (В САМОМ НИЗУ)
  { path: '/:slug', component: ClientMenu } 
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  // Публичные страницы (меню, чекаут, логин)
  if (to.params.slug || to.path === '/checkout' || to.path === '/login') {
    // Если идем на логин и уже есть токен - проверяем роль
    if (to.path === '/login' && localStorage.getItem('token')) {
      return next('/check-role')
    }
    return next()
  }

  // Проверка токена
  const token = localStorage.getItem('token')
  if (!token) return next('/login')

  // Проверка роли
  if (to.path === '/check-role' || to.meta.requiresAuth) {
    try {
      const res = await axios.get('http://213.148.7.107:8002/api/v1/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const user = res.data
      
      // Распределение
      if (to.path === '/check-role') {
        if (user.is_superuser) return next('/admin')
        else return next('/restaurant')
      }
      
      // Защита
      if (to.meta.role === 'superuser' && !user.is_superuser) return next('/restaurant')
      if (to.meta.role === 'owner' && user.is_superuser) return next('/admin')
      
      return next()
    } catch (e) {
      localStorage.removeItem('token')
      return next('/login')
    }
  }
  
  next()
})

export default router