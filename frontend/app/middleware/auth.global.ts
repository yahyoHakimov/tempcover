// Runs on every route: guards /admin/** and /superadmin/**, keeps the dashboard URL in sync
import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware((to) => {
  // The session is stored in localStorage, so only the client can decide; every gated page fetches in onMounted.
  if (import.meta.server) return

  const auth = useAuthStore()
  auth.init()

  const isLoginRoute      = to.path === '/admin/login'
  const isAdminRoute      = to.path.startsWith('/admin') && !isLoginRoute
  const isSuperAdminRoute = to.path.startsWith('/superadmin')

  // Already signed in — skip the login page
  if (isLoginRoute && auth.isLoggedIn) {
    return navigateTo(auth.homePath)
  }

  if ((isAdminRoute || isSuperAdminRoute) && !auth.isLoggedIn) {
    return navigateTo('/admin/login')
  }

  // /superadmin is for super admins only
  if (isSuperAdminRoute && !auth.isSuperAdmin) {
    return navigateTo(auth.homePath)
  }

  // /admin and /admin/dashboard -> /admin/dashboard/<username>
  if (isAdminRoute && (to.path === '/admin' || to.path === '/admin/' || to.path === '/admin/dashboard' || to.path === '/admin/dashboard/')) {
    return navigateTo(auth.homePath)
  }

  // Dashboard URL carries the username: keep it honest
  if (to.path.startsWith('/admin/dashboard/')) {
    const slug = to.params.username
    if (slug && auth.username && slug !== auth.username) {
      return navigateTo(auth.homePath)
    }
  }
})
