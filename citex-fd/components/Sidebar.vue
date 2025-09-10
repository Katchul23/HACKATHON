<!-- components/Sidebar.vue -->
<template>
  <aside class="w-64 border-r bg-white p-4 overflow-y-auto">
    <h2 class="text-lg font-bold mb-4">📁 Historique</h2>
    <ul>
      <li
        v-for="session in sessions"
        :key="session.id"
        class="mb-2 cursor-pointer hover:text-green-600"
        @click="$emit('select', session.id)"
      >
        {{ session.titre || 'Session sans titre' }}
      </li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
defineProps<{
  sessions: { id: number; titre: string }[]
}>()

defineEmits<{
  (e: 'select', id: number): void
}>()
</script>
