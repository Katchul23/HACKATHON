
// composables/useAuth.ts
import { useCookie } from '#app'

type LoginResponse = {
  access_token: string
  token_type: string
}

type User = {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  is_superuser: boolean
  is_verified: boolean
  last_login: string | null
}

export function useAuth() {
  const token = useCookie<string | null>('access_token')
  const user = useState<User | null>('user', () => null)
  const config = useRuntimeConfig()

  const login = async (email: string, password: string) => {
    const { data, error } = await useFetch<LoginResponse>(`${config.public.apiBase}/auth/login`, {
      method: 'POST',
      body: new URLSearchParams({
        username: email,
        password: password
      }),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
    })

    if (error.value || !data.value?.access_token) {
      throw new Error('Échec de la connexion')
    }

    token.value = data.value.access_token
    await fetchUser()

    if (!user.value?.is_active) {
      throw new Error("Compte désactivé")
    }
    if (!user.value?.is_verified) {
      throw new Error("Compte non vérifié")
    }
  }

  const fetchUser = async () => {
    if (!token.value) return

    const { data, error } = await useFetch<User>(`${config.public.apiBase}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token.value}`
      },
    })

    if (data.value) user.value = data.value
  }

  const logout = () => {
    token.value = null
    user.value = null
  }

  const isAuthenticated = computed(() => !!user.value)

  return { user, token, login, fetchUser, logout, isAuthenticated }
}
