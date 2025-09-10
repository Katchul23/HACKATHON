// middleware/auth.ts
import { useAuth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware(async () => {
  const { token, isAuthenticated, fetchUser } = useAuth()

  if (!token.value) {
    return navigateTo('/login')
  }

  // On essaie de récupérer les infos si non chargé
  if (!isAuthenticated.value) {
    await fetchUser()
  }

  // Toujours pas connecté après fetch ? Redirection
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
