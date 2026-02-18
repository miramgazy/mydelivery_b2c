import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { tab: 'menu' },
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('@/views/CartView.vue'),
    meta: { tab: 'cart' },
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/views/CheckoutView.vue'),
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { tab: 'profile' },
  },
]

const router = createRouter({
  history: createWebHistory('/webapp'),
  routes,
})

export default router
