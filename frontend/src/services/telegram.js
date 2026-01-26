
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
        // Если VITE_DEV_MODE=true, принудительно используем desktop режим (кроме реального Telegram)
        const devMode = import.meta.env.VITE_DEV_MODE === 'true' || import.meta.env.VITE_DEV_MODE === true;
        
        if (!this.webApp) return false;
        
        // initData должен быть непустой строкой
        const hasInitData = this.webApp.initData && typeof this.webApp.initData === 'string' && this.webApp.initData.length > 0;
        
        // initDataUnsafe.user должен существовать (это реальный признак Telegram MiniApp)
        const hasUser = !!this.webApp.initDataUnsafe?.user;
        
        // Дополнительная проверка: версия платформы (в браузере обычно 'web' или 'unknown')
        const platform = this.webApp.platform;
        const isRealTelegram = platform && platform !== 'web' && platform !== 'unknown';
        
        // В dev режиме, если не реальный Telegram - возвращаем false
        if (devMode && !isRealTelegram) {
            return false;
        }
        
        // Возвращаем true только если есть initData и пользователь (или реальная платформа Telegram)
        return hasInitData && hasUser;
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
}

export default new TelegramService();
