import { createApp } from 'vue'
import { createPinia } from 'pinia' // <-- Импорт Pinia
import './style.css'
import App from './App.vue'
import router from './router'

const pinia = createPinia() // <-- Создаем экземпляр

createApp(App)
  .use(pinia) // <-- Подключаем
  .use(router)
  .mount('#app')