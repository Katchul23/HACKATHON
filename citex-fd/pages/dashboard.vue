<template>
  <div class="max-w-3xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">🎛️ Tableau de bord</h1>

    <div class="bg-white shadow p-4 rounded">
      <p><strong>Nom d'utilisateur :</strong> {{ user?.username }}</p>
      <p><strong>Email :</strong> {{ user?.email }}</p>
      <p><strong>Rôle :</strong> {{ user?.role }}</p>
      <p><strong>Statut :</strong>
        <span :class="user?.is_active ? 'text-green-600' : 'text-red-600'">
          {{ user?.is_active ? 'Actif' : 'Désactivé' }}
        </span>
      </p>
      <p><strong>Vérifié :</strong>
        <span :class="user?.is_verified ? 'text-green-600' : 'text-yellow-600'">
          {{ user?.is_verified ? 'Oui' : 'Non' }}
        </span>
      </p>
      <p><strong>Dernière connexion :</strong>
        {{ user?.last_login ? new Date(user.last_login).toLocaleString() : 'Jamais' }}
      </p>
    </div>

    <div class="mt-6 text-right">
      <button @click="logoutAndGo" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded">
        Se déconnecter
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'
import { useToast } from '~/composables/useToast'
import { useRouter } from 'vue-router'

definePageMeta({
  middleware: 'auth'
})

const { user, logout } = useAuth()
const { show } = useToast()
const router = useRouter()

const logoutAndGo = () => {
  logout()
  show({ type: 'info', message: 'Déconnecté avec succès' })
  router.push('/login')
}
</script>
