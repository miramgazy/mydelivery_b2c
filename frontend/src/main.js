import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

// Глобальный отлов ошибок для отладки в TMA
window.onerror = function (msg, url, line, col, error) {
    console.error(`GLOBAL ERROR: ${msg} at ${line}:${col}. Error:`, error);
    try {
        // Отправляем на бэкенд, чтобы видеть реальную причину падения в Telegram WebView
        const payload = {
            type: 'window.onerror',
            msg: String(msg),
            url: String(url || ''),
            line,
            col,
            stack: String(error?.stack || ''),
            userAgent: navigator.userAgent
        }
        navigator.sendBeacon?.('/api/client-log/', new Blob([JSON.stringify(payload)], { type: 'application/json' }))
    } catch (_) {}
    // Показываем ошибку пользователю в Telegram WebView, иначе будет "белый экран" без контекста
    try {
        const webApp = window.Telegram?.WebApp
        if (webApp?.showAlert) {
            const shortMsg = String(msg || error?.message || 'Unknown error').slice(0, 200)
            webApp.showAlert(`Ошибка приложения: ${shortMsg}`)
        }
    } catch (_) {}
    return false;
};

window.onunhandledrejection = function (event) {
    console.error('UNHANDLED PROMISE REJECTION:', event.reason);
    try {
        const payload = {
            type: 'unhandledrejection',
            reason: String(event?.reason?.message || event?.reason || ''),
            stack: String(event?.reason?.stack || ''),
            userAgent: navigator.userAgent
        }
        navigator.sendBeacon?.('/api/client-log/', new Blob([JSON.stringify(payload)], { type: 'application/json' }))
    } catch (_) {}
    try {
        const webApp = window.Telegram?.WebApp
        if (webApp?.showAlert) {
            const shortMsg = String(event?.reason?.message || event?.reason || 'Unknown rejection').slice(0, 200)
            webApp.showAlert(`Ошибка приложения: ${shortMsg}`)
        }
    } catch (_) {}
};

// Удаляем Service Worker'ы, если они есть
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function (registrations) {
        for (let registration of registrations) {
            console.log('Unregistering SW:', registration);
            registration.unregister();
        }
    });
}

const app = createApp(App)

// Pinia store
app.use(createPinia())

// Vue Router
app.use(router)

// Mount app
app.mount('#app')