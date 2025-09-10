<template>
  <div class="fixed bottom-4 right-4 space-y-3 z-50">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      :class="[
        'px-4 py-3 rounded shadow text-sm text-white',
        toastClass(toast.type)
      ]"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { useToast } from '~/composables/useToast'
const { toasts } = useToast()

function toastClass(type) {
  return {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-blue-600',
    warning: 'bg-yellow-600 text-black'
  }[type] || 'bg-gray-700'
}
</script>
