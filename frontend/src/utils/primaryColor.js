/**
 * Default primary color (sky-600) when organization has no custom color.
 */
const DEFAULT_PRIMARY = '#0284c7'

/**
 * Default Tailwind-style palette for sky-600 (used as fallback in CSS).
 */
const DEFAULT_PALETTE = {
  50: '#f0f9ff',
  100: '#e0f2fe',
  200: '#bae6fd',
  300: '#7dd3fc',
  400: '#38bdf8',
  500: '#0ea5e9',
  600: '#0284c7',
  700: '#0369a1',
  800: '#075985',
  900: '#0c4a6e',
}

/**
 * Parse hex color to RGB components (0-255).
 * @param {string} hex - e.g. "#0284c7" or "0284c7"
 * @returns {{ r: number, g: number, b: number } | null}
 */
function hexToRgb(hex) {
  const s = hex.replace(/^#/, '')
  if (!/^[0-9A-Fa-f]{6}$/.test(s)) return null
  return {
    r: parseInt(s.slice(0, 2), 16),
    g: parseInt(s.slice(2, 4), 16),
    b: parseInt(s.slice(4, 6), 16),
  }
}

/**
 * @param {number} r
 * @param {number} g
 * @param {number} b
 * @returns {string} #rrggbb
 */
function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map((x) => Math.round(Math.max(0, Math.min(255, x))).toString(16).padStart(2, '0')).join('')
}

/**
 * Blend color with white (0 = full color, 1 = full white).
 * @param {{ r, g, b }} rgb
 * @param {number} t - 0..1
 */
function lighten(rgb, t) {
  return {
    r: rgb.r + (255 - rgb.r) * t,
    g: rgb.g + (255 - rgb.g) * t,
    b: rgb.b + (255 - rgb.b) * t,
  }
}

/**
 * Blend color with black (0 = full color, 1 = full black).
 */
function darken(rgb, t) {
  return {
    r: rgb.r * (1 - t),
    g: rgb.g * (1 - t),
    b: rgb.b * (1 - t),
  }
}

/**
 * Generate a Tailwind-style primary palette (50..900) from a single hex.
 * @param {string} hex - e.g. "#0284c7"
 * @returns {{ 50: string, 100: string, 200: string, 300: string, 400: string, 500: string, 600: string, 700: string, 800: string, 900: string }}
 */
export function paletteFromHex(hex) {
  const normalized = hex && hex.startsWith('#') ? hex : hex ? '#' + hex : DEFAULT_PRIMARY
  const rgb = hexToRgb(normalized)
  if (!rgb) return DEFAULT_PALETTE

  // 600 = base, 500/700 slight variants, 50-400 lighten, 800-900 darken
  const mix = (light, dark) => {
    if (light > 0) return rgbToHex(...Object.values(lighten(rgb, light)))
    return rgbToHex(...Object.values(darken(rgb, -dark)))
  }
  return {
    50: mix(0.95, 0),
    100: mix(0.9, 0),
    200: mix(0.75, 0),
    300: mix(0.5, 0),
    400: mix(0.25, 0),
    500: mix(0.08, 0),
    600: normalized,
    700: mix(0, 0.2),
    800: mix(0, 0.4),
    900: mix(0, 0.55),
  }
}

/**
 * Normalized primary hex for organization (valid #rrggbb or default).
 * @param {string | null | undefined} raw
 * @returns {string}
 */
export function normalizePrimaryHex(raw) {
  if (!raw) return DEFAULT_PRIMARY
  const s = String(raw).trim()
  const hex = s.startsWith('#') ? s : '#' + s
  return /^#[0-9A-Fa-f]{6}$/.test(hex) ? hex : DEFAULT_PRIMARY
}
