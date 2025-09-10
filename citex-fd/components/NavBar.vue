<template>
  <header class="bg-green-700 text-white px-6 py-4 shadow flex items-center justify-between">
    <NuxtLink to="/" class="text-lg font-semibold">📚 DataTrace</NuxtLink>

    <nav v-if="!authLoading" class="flex items-center gap-4 text-sm">
      <template v-if="isAuthenticated">
        <NuxtLink to="/chat" class="hover:underline">Assistant</NuxtLink>

        <NuxtLink to="/dashboard" class="hover:underline">
          Bonjour, {{ user?.username }}
        </NuxtLink>

        <NuxtLink
          v-if="user?.is_superuser"
          to="/admin"
          class="hover:underline text-yellow-300"
        >
          Admin
        </NuxtLink>

        <button @click="logoutAndRedirect" class="hover:underline text-red-300">
          Déconnexion
        </button>
      </template>

      <template v-else>
        <NuxtLink to="/chat" class="hover:underline">Assistant</NuxtLink>
        <NuxtLink to="/login" class="hover:underline">Connexion</NuxtLink>
        <NuxtLink to="/register" class="hover:underline">S’inscrire</NuxtLink>
      </template>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRouter } from 'vue-router'
import { useToast } from '~/composables/useToast'

const { user, isAuthenticated, logout, fetchUser } = useAuth()
const { show } = useToast()
const router = useRouter()

// Gestion d’un flag de chargement
const authLoading = useState('auth-loading', () => true)

onMounted(async () => {
  // Recharge l’utilisateur s’il y a un token mais pas encore de profil
  if (!user.value) {
    await fetchUser()
  }
  authLoading.value = false
})

const logoutAndRedirect = () => {
  logout()
  show({ type: 'info', message: 'Déconnecté avec succès' })
  router.push('/login')
}
</script>
