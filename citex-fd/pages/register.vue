<template>
  <div class="max-w-md mx-auto mt-12 bg-white p-6 rounded shadow">
    <h1 class="text-xl font-bold mb-4 text-center">📝 Inscription</h1>

    <form @submit.prevent="submitRegister">
      <input
        v-model="username"
        type="text"
        placeholder="Nom d'utilisateur"
        class="w-full p-2 border mb-3 rounded"
      />
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
        Créer un compte
      </button>
    </form>

    <p class="text-sm text-red-600 mt-3 text-center" v-if="errorMsg">{{ errorMsg }}</p>
    <p class="text-sm text-center mt-4">
      Déjà inscrit ?
      <NuxtLink to="/login" class="text-green-700 underline">Se connecter</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '~/composables/useToast'

const username = ref('')
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const router = useRouter()
const { show } = useToast()

const submitRegister = async () => {
  errorMsg.value = ''
  try {
    const { data, error } = await useFetch('http://localhost:8000/auth/register', {
      method: 'POST',
      body: {
        username: username.value,
        email: email.value,
        password: password.value
      }
    })

    if (error.value || !data.value) {
      const message = error.value?.data?.detail || 'Inscription échouée'
      errorMsg.value = message
      show({ type: 'error', message })
      return
    }

    show({
      type: 'success',
      message: 'Compte créé avec succès. Veuillez vérifier votre email.'
    })

    router.push('/login')
  } catch (err) {
    errorMsg.value = 'Erreur réseau ou serveur. Réessaie plus tard.'
    show({ type: 'error', message: errorMsg.value })
  }
}
</script>
