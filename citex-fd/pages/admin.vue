<script setup lang="ts">
definePageMeta({
  middleware: 'admin',
})

import { ref, computed, onMounted } from 'vue'
import { useToast } from '~/composables/useToast'
import { useAuth } from '~/composables/useAuth'

interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
}

const users = ref<User[]>([])
const searchQuery = ref('')
const selectedUser = ref<User | null>(null)
const { token } = useAuth()
const { show } = useToast()
const config = useRuntimeConfig()

const fetchUsers = async () => {
  try {
    const { data, error } = await useFetch<User[]>(`${config.public.apiBase}/auth/users`, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    if (error.value) {
      show({ type: 'error', message: 'Erreur chargement des utilisateurs' })
    } else {
      users.value = data.value || []
    }
  } catch (err) {
    show({ type: 'error', message: 'Erreur de connexion au serveur' })
  }
}

const deleteUser = async (id: number) => {
  if (!confirm('Confirmer la suppression de cet utilisateur ?')) return
  try {
    await $fetch(`${config.public.apiBase}/auth/delete/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token.value}` }
    })
    users.value = users.value.filter((u) => u.id !== id)
    show({ type: 'success', message: 'Utilisateur supprimé' })
  } catch {
    show({ type: 'error', message: 'Erreur lors de la suppression' })
  }
}

const handleSave = async (updatedUser: User) => {
  try {
    await $fetch(`${config.public.apiBase}/auth/admin/update_user/${updatedUser.id}`, {
      method: 'PUT',
      body: updatedUser,
      headers: { Authorization: `Bearer ${token.value}` }
    })
    show({ type: 'success', message: `Utilisateur ${updatedUser.username} mis à jour.` })
    selectedUser.value = null
    await fetchUsers()
  } catch {
    show({ type: 'error', message: 'Échec de la mise à jour' })
  }
}


const openEditModal = (user: User) => {
  selectedUser.value = { ...user }
}

const filteredUsers = computed(() => {
  return users.value.filter(u =>
    u.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    u.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

onMounted(fetchUsers)
</script>
<template>
  <div class="max-w-6xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6 text-green-800">🔐 Tableau de bord Admin</h1>

    <div class="flex justify-between items-center mb-4">
      <p class="text-gray-700">Liste des utilisateurs inscrits :</p>
      <input v-model="searchQuery" type="text" placeholder="🔍 Rechercher par nom/email..." class="border px-3 py-1 rounded text-sm" />
    </div>

    <table class="min-w-full bg-white border border-gray-300 text-sm">
      <thead>
        <tr class="bg-gray-100 text-left">
          <th class="p-2 border">#</th>
          <th class="p-2 border">Nom</th>
          <th class="p-2 border">Email</th>
          <th class="p-2 border">Rôle</th>
          <th class="p-2 border">Actif</th>
          <th class="p-2 border">Vérifié</th>
          <th class="p-2 border">Superuser</th>
          <th class="p-2 border text-center">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(u, i) in filteredUsers" :key="u.id" class="hover:bg-gray-50">
          <td class="p-2 border">{{ i + 1 }}</td>
          <td class="p-2 border">{{ u.username }}</td>
          <td class="p-2 border">{{ u.email }}</td>
          <td class="p-2 border">{{ u.role }}</td>
          <td class="p-2 border text-center">
            <span :class="u.is_active ? 'text-green-600' : 'text-red-600'">
              {{ u.is_active ? '✔' : '✘' }}
            </span>
          </td>
          <td class="p-2 border text-center">
            <span :class="u.is_verified ? 'text-green-600' : 'text-red-600'">
              {{ u.is_verified ? '✔' : '✘' }}
            </span>
          </td>
          <td class="p-2 border text-center">
            <span :class="u.is_superuser ? 'text-blue-600' : 'text-gray-400'">
              {{ u.is_superuser ? '✔' : '—' }}
            </span>
          </td>
          <td class="p-2 border text-center space-x-1">
            <button @click="openEditModal(u)" class="text-blue-600 text-xs">✏️</button>
            <button @click="deleteUser(u.id)" class="text-red-500 text-xs">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="filteredUsers.length === 0" class="mt-4 text-gray-600">
      Aucun utilisateur correspondant.
    </div>

    <UserEditModal
      :visible="!!selectedUser"
      v-if="selectedUser"
      :user="selectedUser"
      @close="selectedUser = null"
      @save="handleSave"
      @updated="fetchUsers"
    />
  </div>
</template>

