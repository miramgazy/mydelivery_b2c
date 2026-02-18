/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary-color, #FF5733)',
        secondary: 'var(--secondary-color, #333333)',
        background: 'var(--background-color, #FFFFFF)',
      },
      fontFamily: {
        main: 'var(--font-main, "Inter", sans-serif)',
      },
      borderRadius: {
        main: 'var(--radius-main, 12px)',
      },
    },
  },
  plugins: [],
}
