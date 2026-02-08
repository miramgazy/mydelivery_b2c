/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Primary palette from organization.primary_color; set via CSS vars in App.vue (default: sky blue)
                primary: {
                    50: 'var(--color-primary-50, #f0f9ff)',
                    100: 'var(--color-primary-100, #e0f2fe)',
                    200: 'var(--color-primary-200, #bae6fd)',
                    300: 'var(--color-primary-300, #7dd3fc)',
                    400: 'var(--color-primary-400, #38bdf8)',
                    500: 'var(--color-primary-500, #0ea5e9)',
                    600: 'var(--color-primary-600, #0284c7)',
                    700: 'var(--color-primary-700, #0369a1)',
                    800: 'var(--color-primary-800, #075985)',
                    900: 'var(--color-primary-900, #0c4a6e)',
                },
                telegram: {
                    bg: '#17212b',
                    secondary: '#242f3d',
                    text: '#ffffff',
                    hint: '#708499',
                    link: '#2481cc',
                    button: '#5288c1',
                    button_text: '#ffffff',
                }
            },
            fontFamily: {
                sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
            },
            spacing: {
                'safe-top': 'env(safe-area-inset-top)',
                'safe-bottom': 'env(safe-area-inset-bottom)',
            }
        },
    },
    plugins: [],
}