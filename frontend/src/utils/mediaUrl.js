/**
 * Нормализует URL изображения с бэкенда для отображения в браузере.
 * - Относительный путь (/media/...) превращаем в URL с текущим origin (в проде) или с базой API.
 * - Полный URL с внутренним хостом (backend:8000) подменяем на текущий origin.
 * - Полный URL с другим доступным хостом (например localhost:8090) оставляем как есть.
 * @param {string|null|undefined} url - URL от API
 * @returns {string|null}
 */
export function normalizeMediaUrl(url) {
  if (url == null || url === '') return null
  if (typeof url !== 'string') return null
  const s = url.trim()
  if (s.startsWith('blob:')) return s
  try {
    if (s.startsWith('http://') || s.startsWith('https://')) {
      const u = new URL(s)
      if (u.host === window.location.host) return s
      const hostname = (u.hostname || u.host.split(':')[0] || '').toLowerCase()
      if (hostname === 'backend') {
        return window.location.origin + u.pathname
      }
      return s
    }
    if (s.startsWith('/')) {
      return window.location.origin + s
    }
    return s
  } catch {
    return url
  }
}
