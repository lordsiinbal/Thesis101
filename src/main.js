import { createApp } from 'vue'
import App from './App.vue'
import VueChartkick from 'vue-chartkick'
import 'chartkick/chart.js'
import {createRouter,createWebHistory} from 'vue-router'
import Home from './components/Home.vue'
import Dashboard from './components/Dashboard.vue'
import Table from './components/Table.vue'
const routes=[
    {
        path:'/',
        component:Home,
    },
    {
        path:'/dashboard',
        component:Dashboard,
    },
    {
        path:'/table',
        component:Table,
    },
];
const router= createRouter({
    history:createWebHistory(),
    routes:routes
})
const app=createApp(App);
app.use(router)
app.use(VueChartkick).mount('#app')
 