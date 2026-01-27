
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
     * Запросить геолокацию пользователя
     * В Telegram Mini App и браузере используется стандартный браузерный API
     * Возвращает Promise с координатами или ошибкой
     * 
     * @returns {Promise<{latitude: number, longitude: number}>}
     */
    requestLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation не поддерживается в этом браузере'))
                return
            }

            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const location = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    }
                    console.log('Location obtained:', location)
                    resolve(location)
                },
                (error) => {
                    let errorMessage = 'Не удалось получить геолокацию'
                    
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = 'Доступ к геолокации запрещен. Пожалуйста, разрешите доступ в настройках браузера.'
                            break
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = 'Информация о местоположении недоступна'
                            break
                        case error.TIMEOUT:
                            errorMessage = 'Превышено время ожидания запроса геолокации'
                            break
                        default:
                            errorMessage = 'Произошла ошибка при получении геолокации'
                            break
                    }
                    
                    console.error('Geolocation error:', error)
                    reject(new Error(errorMessage))
                },
                options
            )
        })
    }
}

export default new TelegramService();
