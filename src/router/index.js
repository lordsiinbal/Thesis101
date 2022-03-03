import {createRouter,createWebHistory} from 'vue-router'
import Home from '../components/Home.vue'
import Dashboard from '../components/Dashboard.vue'
import Table from '../components/Table.vue'
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
    history:createWebHistory(process.env.BASE_URL),
    routes:routes
})

export default router