
class TelegramService {
    constructor() {
        this.webApp = (typeof window !== 'undefined') ? (window.Telegram?.WebApp || null) : null;
    }

    /**
     * Инициализация SDK
     */
    init() {
        if (this.webApp) {
            this.webApp.ready();
            this.webApp.expand();
            this.updateHeaderColor();
            console.log('Telegram WebApp initialized');
        }
    }

    /**
     * Проверка запуска в Telegram
     */
    isInTelegram() {
        // Проверяем наличие WebApp И initData (чтобы отличить от расширений браузера)
        return !!this.webApp && !!this.webApp.initData;
    }

    /**
     * Получить initData
     */
    getInitData() {
        return this.webApp?.initData;
    }

    /**
     * Получить данные пользователя
     */
    getUser() {
        return this.webApp?.initDataUnsafe?.user;
    }

    /**
     * Показать алерт
     */
    showAlert(message) {
        if (this.isInTelegram()) {
            this.webApp.showAlert(message);
        } else {
            alert(message);
        }
    }

    /**
     * Показать подтверждение
     */
    showConfirm(message, callback) {
        if (this.isInTelegram()) {
            this.webApp.showConfirm(message, (confirmed) => {
                if (confirmed && callback) callback();
            });
        } else {
            if (confirm(message) && callback) callback();
        }
    }

    /**
     * Вибрация
     * type: 'light', 'medium', 'heavy', 'rigid', 'soft'
     * style: 'success', 'warning', 'error'
     */
    vibrate(type = 'light') {
        if (!this.isInTelegram()) return;

        const haptic = this.webApp.HapticFeedback;

        if (['success', 'warning', 'error'].includes(type)) {
            haptic.notificationOccurred(type);
        } else {
            haptic.impactOccurred(type);
        }
    }

    /**
     * Показать кнопку назад
     */
    showBackButton(callback) {
        if (!this.isInTelegram()) return;

        this.webApp.BackButton.show();
        this.webApp.BackButton.onClick(callback);
    }

    /**
     * Скрыть кнопку назад
     */
    hideBackButton(callback) {
        if (!this.isInTelegram()) return;

        this.webApp.BackButton.hide();
        if (callback) {
            this.webApp.BackButton.offClick(callback);
        }
    }

    /**
     * Обновить цвет хедера
     */
    updateHeaderColor() {
        if (!this.isInTelegram()) return;

        // Используем цвет фона темы
        this.webApp.setHeaderColor(this.webApp.themeParams.bg_color || '#ffffff');
        this.webApp.setBackgroundColor(this.webApp.themeParams.bg_color || '#ffffff');
    }

    /**
     * Закрыть приложение
     */
    close() {
        if (this.isInTelegram()) {
            this.webApp.close();
        }
    }

    /**
     * Запросить геолокацию пользователя через Telegram
     * В Telegram Mini App используется специальный метод для запроса геолокации
     * Координаты будут обработаны сторонним инструментом и записаны в БД
     */
    requestLocation() {
        if (!this.isInTelegram()) {
            // В браузере используем стандартный API
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        // В браузере просто возвращаем координаты
                        console.log('Location:', {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        })
                    },
                    (error) => {
                        console.error('Geolocation error:', error)
                    }
                )
            }
            return
        }

        // В Telegram Mini App используем метод для запроса геолокации
        // Telegram откроет стандартный интерфейс для отправки геолокации
        // Координаты будут обработаны сторонним инструментом (ботом) и записаны в БД
        // Используем стандартный способ через открытие ссылки для отправки геолокации
        if (this.webApp && this.webApp.openTelegramLink) {
            // Открываем интерфейс отправки геолокации
            // В реальности это должно быть обработано ботом через webhook
            this.webApp.openTelegramLink('tg://location')
        } else {
            // Fallback: используем стандартный API браузера
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        console.log('Location:', {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        })
                    },
                    (error) => {
                        console.error('Geolocation error:', error)
                    }
                )
            }
        }
    }
}

export default new TelegramService();
