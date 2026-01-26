
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
        // Строгая проверка: должны быть выполнены ВСЕ условия
        
        // 1. WebApp должен существовать
        if (!this.webApp) {
            console.log('[TelegramService] isInTelegram: false - no webApp');
            return false;
        }
        
        // 2. Проверка user agent - если это не Telegram, сразу false
        const userAgent = typeof navigator !== 'undefined' ? navigator.userAgent : '';
        const isTelegramUserAgent = userAgent.includes('Telegram') || userAgent.includes('WebApp');
        
        // 3. initData должен быть непустой строкой с реальными данными
        const initData = this.webApp.initData;
        const hasInitData = initData && typeof initData === 'string' && initData.length > 0;
        
        // 4. initDataUnsafe.user должен существовать (это реальный признак Telegram MiniApp)
        const user = this.webApp.initDataUnsafe?.user;
        const hasUser = !!user && !!user.id;
        
        // 5. Проверка платформы (в браузере обычно 'web', 'unknown' или undefined)
        const platform = this.webApp.platform;
        const isRealTelegramPlatform = platform && platform !== 'web' && platform !== 'unknown' && platform !== undefined;
        
        // 6. Проверка версии (в реальном Telegram всегда есть версия)
        const version = this.webApp.version;
        const hasVersion = version && typeof version === 'string';
        
        // Логирование для отладки (только в development)
        if (import.meta.env.DEV) {
            console.log('[TelegramService] isInTelegram check:', {
                hasWebApp: !!this.webApp,
                isTelegramUserAgent,
                hasInitData,
                hasUser,
                isRealTelegramPlatform,
                hasVersion,
                platform,
                version,
                initDataLength: initData?.length || 0,
                userId: user?.id
            });
        }
        
        // Возвращаем true ТОЛЬКО если:
        // - Есть initData с данными
        // - Есть пользователь с ID
        // - И (есть Telegram user agent ИЛИ реальная платформа Telegram)
        const result = hasInitData && hasUser && (isTelegramUserAgent || isRealTelegramPlatform);
        
        if (import.meta.env.DEV) {
            console.log('[TelegramService] isInTelegram result:', result);
        }
        
        return result;
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
