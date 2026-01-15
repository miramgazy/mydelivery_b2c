import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import telegramService from '@/services/telegram'

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('@/views/HomeView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/menu',
        name: 'menu',
        component: () => import('@/views/MenuView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/orders',
        name: 'orders',
        component: () => import('@/views/OrdersView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/orders/:id',
        name: 'order-detail',
        component: () => import('@/views/OrderDetailView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/profile',
        name: 'profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/checkout',
        name: 'checkout',
        component: () => import('@/views/CheckoutView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
        meta: { requiresAuth: false }
    },
    // Admin routes with DesktopLayout
    {
        path: '/admin',
        component: () => import('@/layouts/DesktopLayout.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
        children: [
            {
                path: '',
                redirect: '/admin/organization/settings'
            },
            // Organization routes
            {
                path: 'organization/settings',
                name: 'admin-organization-settings',
                component: () => import('@/views/admin/OrganizationSettings.vue')
            },
            {
                path: 'organization/terminals',
                name: 'admin-organization-terminals',
                component: () => import('@/views/admin/TerminalsManagement.vue')
            },
            {
                path: 'organization/payment-types',
                name: 'admin-organization-payment-types',
                component: () => import('@/views/admin/PaymentTypesManagement.vue')
            },
            {
                path: 'organization/menu',
                name: 'admin-organization-menu',
                component: () => import('@/views/admin/MenuManagement.vue')
            },
            // Orders routes
            {
                path: 'orders',
                name: 'admin-orders',
                component: () => import('@/views/admin/OrdersManagement.vue')
            },
            // Users routes
            {
                path: 'users',
                name: 'admin-users',
                component: () => import('@/views/admin/UsersManagement.vue')
            },
            // Products routes
            {
                path: 'products',
                name: 'admin-products',
                component: () => import('@/views/admin/ProductsManagement.vue')
            },
            {
                path: 'modifiers',
                name: 'admin-modifiers',
                component: () => import('@/views/admin/ModifiersManagement.vue')
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // Если требуется авторизация и пользователь не авторизован
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        // Если мы в Telegram, пускаем на главную (там сработает авто-вход)
        // Если не в Telegram, отправляем на страницу логина
        if (telegramService.isInTelegram()) {
            next('/')
        } else {
            next('/login')
        }
        return
    }

    // Если авторизован и идет на логин - редирект на главную или админку
    if (to.name === 'login' && authStore.isAuthenticated) {
        if (authStore.isSuperAdmin || authStore.isOrgAdmin) {
            next('/admin')
        } else {
            next('/')
        }
        return
    }

    // Если требуются права админа
    if (to.meta.requiresAdmin && !authStore.isSuperAdmin && !authStore.isOrgAdmin) {
        // Перенаправляем на главную
        next('/')
        return
    }

    next()
})

export default router