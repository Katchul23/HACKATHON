// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000'  // ou via .env
    }
  },
  css: ['@/assets/css/tailwind.css'],
  modules: ['@nuxtjs/tailwindcss'],
})
