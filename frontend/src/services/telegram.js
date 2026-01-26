
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
        // ПРИОРИТЕТ 1: Проверка user agent - самая надежная проверка
        const userAgent = typeof navigator !== 'undefined' ? navigator.userAgent : '';
        const isTelegramUserAgent = userAgent.includes('Telegram') || userAgent.includes('WebApp');
        
        // Если user agent не Telegram - сразу false (даже если скрипт загружен)
        if (!isTelegramUserAgent) {
            console.log('[TelegramService] isInTelegram: false - not Telegram user agent:', userAgent.substring(0, 100));
            return false;
        }
        
        // ПРИОРИТЕТ 2: WebApp должен существовать
        if (!this.webApp) {
            console.log('[TelegramService] isInTelegram: false - no webApp (but user agent is Telegram)');
            return false;
        }
        
        // ПРИОРИТЕТ 3: initData должен быть непустой строкой с реальными данными
        const initData = this.webApp.initData;
        const hasInitData = initData && typeof initData === 'string' && initData.length > 20; // Минимум 20 символов
        
        // ПРИОРИТЕТ 4: initDataUnsafe.user должен существовать (это реальный признак Telegram MiniApp)
        const user = this.webApp.initDataUnsafe?.user;
        const hasUser = !!user && !!user.id && typeof user.id === 'number';
        
        // ПРИОРИТЕТ 5: Проверка платформы (в браузере обычно 'web', 'unknown' или undefined)
        const platform = this.webApp.platform;
        const isRealTelegramPlatform = platform && platform !== 'web' && platform !== 'unknown' && platform !== undefined;
        
        // Логирование для отладки (всегда, чтобы видеть в production)
        console.log('[TelegramService] isInTelegram check:', {
            userAgent: userAgent.substring(0, 50),
            isTelegramUserAgent,
            hasWebApp: !!this.webApp,
            hasInitData,
            initDataLength: initData?.length || 0,
            hasUser,
            userId: user?.id,
            platform,
            isRealTelegramPlatform
        });
        
        // Возвращаем true ТОЛЬКО если:
        // - User agent Telegram (уже проверили выше)
        // - Есть initData с данными (минимум 20 символов)
        // - Есть пользователь с числовым ID
        const result = hasInitData && hasUser;
        
        console.log('[TelegramService] isInTelegram result:', result);
        
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
