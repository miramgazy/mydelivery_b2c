import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

// Глобальный отлов ошибок для отладки в TMA
window.onerror = function (msg, url, line, col, error) {
    console.error(`GLOBAL ERROR: ${msg} at ${line}:${col}. Error:`, error);
    return false;
};

window.onunhandledrejection = function (event) {
    console.error('UNHANDLED PROMISE REJECTION:', event.reason);
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