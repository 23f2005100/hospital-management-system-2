import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/style.css'   // ← global styles, applies to all pages

const app = createApp(App)
app.use(router)
app.mount('#app')