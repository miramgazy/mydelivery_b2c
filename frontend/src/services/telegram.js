
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
        // Проверяем наличие WebApp
        if (!this.webApp) {
            console.log('[TelegramService] isInTelegram: false - no webApp');
            return false;
        }
        
        // Проверяем наличие initData (не пустая строка и содержит данные)
        const initData = this.webApp.initData;
        if (!initData || typeof initData !== 'string' || initData.trim().length === 0) {
            console.log('[TelegramService] isInTelegram: false - no or empty initData', { 
                hasInitData: !!initData, 
                type: typeof initData,
                length: initData?.length 
            });
            return false;
        }
        
        // В реальном Telegram WebApp initData содержит параметры запроса (минимум несколько символов)
        // Пустая строка или очень короткая строка - это не Telegram
        if (initData.length < 10) {
            console.log('[TelegramService] isInTelegram: false - initData too short', { length: initData.length });
            return false;
        }
        
        // Дополнительная проверка: в реальном Telegram WebApp всегда есть initDataUnsafe
        // и обычно есть пользователь или platform определена
        const hasUser = !!this.webApp.initDataUnsafe?.user;
        const hasPlatform = !!this.webApp.platform;
        
        // Если нет ни пользователя, ни platform, но initData есть - это может быть мок
        // В реальном Telegram WebApp platform всегда определена ('web', 'ios', 'android', 'tdesktop', 'macos', 'unix')
        if (!hasPlatform && !hasUser) {
            console.log('[TelegramService] isInTelegram: false - no platform and no user', {
                platform: this.webApp.platform,
                hasUser,
                hasPlatform
            });
            return false;
        }
        
        // Финальная проверка: если есть platform, она должна быть одной из известных платформ Telegram
        if (hasPlatform) {
            const validPlatforms = ['web', 'ios', 'android', 'tdesktop', 'macos', 'unix', 'weba', 'webk'];
            if (!validPlatforms.includes(this.webApp.platform)) {
                console.log('[TelegramService] isInTelegram: false - invalid platform', { 
                    platform: this.webApp.platform,
                    validPlatforms 
                });
                return false;
            }
        }
        
        console.log('[TelegramService] isInTelegram: true', {
            platform: this.webApp.platform,
            hasUser,
            initDataLength: initData.length
        });
        return true;
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
