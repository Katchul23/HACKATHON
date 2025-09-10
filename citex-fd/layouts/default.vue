<template>
  <div>
    <NavBar />
    <main class="p-6">
      <slot />
    </main>
    <footer class="text-center text-sm text-gray-500 mt-10 pb-6">
      © 2025 – DataTraceAI • all rights reserved !
    </footer>
  </div>
</template>

<script setup>
import NavBar from '~/components/NavBar.vue'
</script>
