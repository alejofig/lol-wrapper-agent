/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'lol-gold': '#C8AA6E',
        'lol-blue': '#0AC8B9',
        'lol-dark': '#0A0E14',
        'lol-darker': '#000000',
        'lol-card': '#0F1419',
      }
    },
  },
  plugins: [],
}


