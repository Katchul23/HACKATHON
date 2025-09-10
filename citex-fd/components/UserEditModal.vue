<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-30 z-50 flex items-center justify-center">
    <div class="bg-white rounded shadow-lg p-6 w-full max-w-md">
      <h2 class="text-lg font-bold mb-4 text-green-700">Modifier l'utilisateur</h2>

      <label class="block text-sm font-medium mb-1">Nom</label>
      <input v-model="form.username" class="w-full border px-3 py-2 rounded mb-3" />

      <label class="block text-sm font-medium mb-1">Email</label>
      <input v-model="form.email" class="w-full border px-3 py-2 rounded mb-3" type="email" />

      <label class="block text-sm font-medium mb-1">Rôle</label>
      <input v-model="form.role" class="w-full border px-3 py-2 rounded mb-3" />

      <div class="flex gap-4 items-center mb-4">
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="form.is_active" /> Actif
        </label>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="form.is_verified" /> Vérifié
        </label>
      </div>

      <div class="flex justify-end gap-3">
        <button @click="close" class="px-3 py-1 rounded bg-gray-300 text-sm">Annuler</button>
        <button @click="submit" class="px-4 py-1 rounded bg-green-600 text-white text-sm">Enregistrer</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ visible: boolean; user: any }>()
const emit = defineEmits(['close', 'save'])

const form = ref({ ...props.user })

watch(() => props.user, (newVal) => {
  form.value = { ...newVal }
})

const close = () => emit('close')
const submit = () => emit('save', form.value)
</script>
