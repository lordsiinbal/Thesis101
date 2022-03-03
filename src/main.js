import { createApp } from 'vue'
import App from './App.vue'
import VueChartkick from 'vue-chartkick'
import 'chartkick/chart.js'
import router from './router'




const app=createApp(App);
app.use(router)
app.use(VueChartkick).mount('#app')

export default app
 