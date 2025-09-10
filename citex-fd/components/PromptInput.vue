<!-- components/PromptInput.vue -->
<template>
  <form @submit.prevent="handleSubmit" class="flex gap-2 p-4 border-t bg-white">
    <input
      v-model="input"
      placeholder="Posez votre question ou collez un DOI..."
      class="flex-1 border px-3 py-2 rounded"
    />
    <button
      type="submit"
      :disabled="loading"
      class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
    >
      {{ loading ? '⏳' : 'Envoyer' }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['submit'])
const input = ref('')
const props = defineProps<{ loading: boolean }>()

const handleSubmit = () => {
  if (!input.value.trim()) return
  emit('submit', input.value) // ✅ Envoie le texte, pas un Event
  input.value = ''
}
</script>
