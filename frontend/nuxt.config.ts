export default defineNuxtConfig({
  pages: true,
  compatibilityDate: '2024-04-03',
  modules: ['@pinia/nuxt'],
  css: ['~/assets/css/main.css'],

  routeRules: {
    '/':              { redirect: '/driver/login' },
    // Signed-in areas render on the client only: the session lives in localStorage, so SSR
    // would produce a different (signed-out) tree and hydration mismatches.
    '/superadmin/**': { ssr: false, headers: { 'Cache-Control': 'no-store' } },
    '/admin/**':      { ssr: false, headers: { 'Cache-Control': 'no-store' } },
    '/admin/login':   { ssr: true,  headers: { 'Cache-Control': 'no-store' } },
    '/driver/portal': { ssr: false },
    '/verifydetailspolicy/**': { ssr: false },
  },

  // Local development: the Nuxt dev server proxies /api and /static to the FastAPI backend,
  // so the frontend talks to the API the same way it does behind the production gateway.
  nitro: {
    devProxy: {
      '/api':    { target: process.env.DEV_API_URL || 'http://127.0.0.1:8001/api',    changeOrigin: true },
      '/static': { target: process.env.DEV_STATIC_URL || 'http://127.0.0.1:8001/static', changeOrigin: true },
    },
  },

  runtimeConfig: {
    public: {
      // Empty string = same-origin (/api is routed by the gateway). Override with NUXT_PUBLIC_API_BASE.
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '',
    },
  },

  app: {
    head: {
      htmlAttrs: { lang: 'en' },
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'theme-color', content: '#FF5100' },
      ],
      link: [
        { rel: 'icon', type: 'image/png', href: '/favicon.png' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Ubuntu:wght@400;500;700&family=Nunito:wght@700;800&display=swap' },
      ],
    },
  },
})
