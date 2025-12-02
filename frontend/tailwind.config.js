/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#E0A800',
        dark: '#121212',
        surface: '#1E1E1E'
      }
    },
  },
  plugins: [],
}
