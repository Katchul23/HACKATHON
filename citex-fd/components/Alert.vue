<template>
  <div
    v-if="visible"
    :class="[
      'p-4 mb-4 rounded-md shadow text-sm flex items-start',
      alertClass
    ]"
    role="alert"
  >
    <span class="font-semibold mr-2">{{ title }}</span>
    <span class="flex-1">{{ message }}</span>
    <button @click="close" class="ml-4 text-xl leading-none">&times;</button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  type: { type: String, default: 'info' }, // 'success' | 'error' | 'info' | 'warning'
  title: { type: String, default: '' },
  message: { type: String, required: true },
  duration: { type: Number, default: 5000 }, // en ms
})

const emit = defineEmits(['close'])

const visible = ref(true)

watch(
  () => props.message,
  (msg) => {
    if (!msg) return
    visible.value = true

    if (props.duration > 0) {
      setTimeout(() => {
        visible.value = false
        emit('close') // 👈 informe le parent que l'alerte est terminée
      }, props.duration)
    }
  },
  { immediate: true }
)

function close() {
  visible.value = false
  emit('close')
}

const alertClass = computed(() => ({
  success: 'bg-green-100 text-green-800 border border-green-300',
  error: 'bg-red-100 text-red-800 border border-red-300',
  info: 'bg-blue-100 text-blue-800 border border-blue-300',
  warning: 'bg-yellow-100 text-yellow-800 border border-yellow-300',
}[props.type] || 'bg-gray-100 text-gray-800 border border-gray-300'))
</script>
