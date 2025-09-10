// 3. ChatMessage.vue
<template>
  <div :class="['mb-2 flex', sender === 'user' ? 'justify-end' : 'justify-start']">
    <div
      :class="[
        'px-4 py-2 rounded max-w-xl',
        sender === 'user'
          ? 'bg-green-600 text-white'
          : 'bg-gray-200 text-gray-800'
      ]"
    >
      {{ text }}
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  sender: String, // 'user' ou 'ia'
  text: String
})
</script>