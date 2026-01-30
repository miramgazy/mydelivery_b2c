import { createI18n } from 'vue-i18n'
import kz from './locales/kz.json'
import ru from './locales/ru.json'

const LOCALE_STORAGE_KEY = 'app_locale'
const DEFAULT_LOCALE = 'kz'
const FALLBACK_LOCALE = 'ru'

export function getStoredLocale() {
  try {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
    if (stored === 'kz' || stored === 'ru') return stored
  } catch (_) {}
  return null
}

export function setStoredLocale(locale) {
  try {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  } catch (_) {}
}

export const i18n = createI18n({
  legacy: false,
  locale: getStoredLocale() || DEFAULT_LOCALE,
  fallbackLocale: FALLBACK_LOCALE,
  messages: {
    kz,
    ru
  }
})

export { LOCALE_STORAGE_KEY, DEFAULT_LOCALE, FALLBACK_LOCALE }
