/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    200: '#fecaca',
                    300: '#fca5a5',
                    400: '#f87171',
                    500: '#ef4444',
                    600: '#fc2329',
                    700: '#dc2626',
                    800: '#b91c1c',
                    900: '#991b1b',
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