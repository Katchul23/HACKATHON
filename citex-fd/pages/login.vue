<template>
  <div class="max-w-md mx-auto mt-12 bg-white p-6 rounded shadow">
    <h1 class="text-xl font-bold mb-4 text-center">🔐 Connexion</h1>

    <form @submit.prevent="submitLogin">
      <input
        v-model="email"
        type="email"
        placeholder="Email"
        class="w-full p-2 border mb-3 rounded"
      />
      <input
        v-model="password"
        type="password"
        placeholder="Mot de passe"
        class="w-full p-2 border mb-3 rounded"
      />

      <button
        type="submit"
        class="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded"
      >
        Se connecter
      </button>
    </form>

    <p class="text-sm text-red-600 mt-3 text-center" v-if="errorMsg">{{ errorMsg }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { useToast } from '~/composables/useToast'

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const router = useRouter()

const { login } = useAuth()
const { show } = useToast()

const submitLogin = async () => {
  errorMsg.value = ''
  try {
    await login(email.value, password.value)
    show({ type: 'success', message: 'Connexion réussie ✅' })
    router.push('/') // ou '/dashboard'
  } catch (err) {
    errorMsg.value = 'Email ou mot de passe invalide.'
    show({ type: 'error', message: 'Erreur de connexion ❌' })
  }
}
</script>
