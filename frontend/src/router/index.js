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
        path: '/profile/addresses',
        name: 'profile-addresses',
        component: () => import('@/views/DeliveryAddressesView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/checkout',
        name: 'checkout',
        component: () => import('@/views/CheckoutView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/fast-menu/:groupId',
        name: 'fast-menu-group',
        component: () => import('@/views/FastMenuGroupView.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/LoginView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/access-denied',
        name: 'access-denied',
        component: () => import('@/views/AccessDeniedView.vue'),
        meta: { requiresAuth: false }
    },
    // Onboarding routes
    {
        path: '/onboarding/welcome',
        name: 'onboarding-welcome',
        component: () => import('@/views/onboarding/WelcomeView.vue'),
        meta: { requiresAuth: true, isOnboarding: true }
    },
    {
        path: '/onboarding/phone',
        name: 'onboarding-phone',
        component: () => import('@/views/onboarding/PhoneInputView.vue'),
        meta: { requiresAuth: true, isOnboarding: true }
    },
    {
        path: '/onboarding/address',
        name: 'onboarding-address',
        component: () => import('@/views/onboarding/AddressInputView.vue'),
        meta: { requiresAuth: true, isOnboarding: true }
    },
    {
        path: '/onboarding/terminal',
        name: 'onboarding-terminal',
        component: () => import('@/views/onboarding/TerminalSelectionView.vue'),
        meta: { requiresAuth: true, isOnboarding: true }
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
            {
                path: 'organization/stop-list',
                name: 'admin-organization-stop-list',
                component: () => import('@/views/admin/StopListView.vue')
            },
            {
                path: 'organization/delivery-zones',
                name: 'admin-organization-delivery-zones',
                component: () => import('@/views/admin/DeliveryZonesView.vue')
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
            },
            {
                path: 'fast-menu',
                name: 'admin-fast-menu',
                component: () => import('@/views/admin/FastMenuManagement.vue')
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
            if (to.path === '/') {
                next()
            } else {
                next('/')
            }
        } else {
            next('/login')
        }
        return
    }

    // Если авторизован и идет на логин - редирект на главную или админку
    if (to.name === 'login' && authStore.isAuthenticated) {
        const user = authStore.user
        const isAdmin = user?.role_name === 'superadmin' || user?.role_name === 'org_admin'
        if (isAdmin) {
            next('/admin')
        } else {
            next('/')
        }
        return
    }

    // Если требуются права админа
    if (to.meta.requiresAdmin) {
        const user = authStore.user
        const isAdmin = user?.role_name === 'superadmin' || user?.role_name === 'org_admin'
        if (!isAdmin) {
            // Перенаправляем на главную
            next('/')
            return
        }
    }
    
    // Если админ пытается попасть на главную (не в Telegram) - редирект в админку
    if (to.name === 'home' && !telegramService.isInTelegram() && authStore.isAuthenticated) {
        const user = authStore.user
        const isAdmin = user?.role_name === 'superadmin' || user?.role_name === 'org_admin'
        if (isAdmin) {
            next('/admin')
            return
        }
    }

    // Onboarding: только для Telegram MiniApp - если пользователь авторизован, но нет телефона/адреса/терминала - редирект на onboarding
    if (telegramService.isInTelegram() && authStore.isAuthenticated && !to.meta.isOnboarding) {
        const user = authStore.user
        // Если нет телефона - редирект на welcome (первый экран onboarding)
        if (!user?.phone && to.name !== 'onboarding-welcome' && to.name !== 'onboarding-phone' && to.name !== 'onboarding-address' && to.name !== 'onboarding-terminal') {
            next('/onboarding/welcome')
            return
        }
        // Если нет адреса - редирект на ввод адреса (но только если есть телефон)
        if (user?.phone && (!user?.addresses || user.addresses.length === 0) && to.name !== 'onboarding-address' && to.name !== 'onboarding-phone' && to.name !== 'onboarding-welcome' && to.name !== 'onboarding-terminal') {
            next('/onboarding/address')
            return
        }
        // Если нет терминалов - редирект на выбор терминала (но только если есть телефон и адрес)
        if (user?.phone && user?.addresses && user.addresses.length > 0 && (!user?.terminals || user.terminals.length === 0) && to.name !== 'onboarding-terminal' && to.name !== 'onboarding-phone' && to.name !== 'onboarding-address' && to.name !== 'onboarding-welcome') {
            next('/onboarding/terminal')
            return
        }
    }

    next()
})


router.onError((error, to) => {
    if (error.message.includes('Failed to fetch dynamically imported module') || error.message.includes('Importing a module script failed')) {
        // Важно: при обновлениях/кэше Telegram WebView может пытаться загрузить несуществующий chunk.
        // Делаем только ОДНУ попытку hard-reload (чтобы не уйти в бесконечный цикл).
        const fullPath = to?.fullPath || window.location.pathname + window.location.search
        const hasReloadFlag = (to?.query && to.query.reload) || new URLSearchParams(window.location.search).has('reload')
        if (!hasReloadFlag) {
            const sep = fullPath.includes('?') ? '&' : '?'
            window.location.replace(`${fullPath}${sep}reload=1`)
        }
    }
})

export default router