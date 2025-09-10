// middleware/admin.ts
import { useAuth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware(async () => {
  const { token, fetchUser, isAuthenticated, user } = useAuth()

  if (!token.value) return navigateTo('/login')
  if (!isAuthenticated.value) await fetchUser()
  if (!user.value || !user.value.is_superuser) {
    return navigateTo('/unauthorized')
  }
})
