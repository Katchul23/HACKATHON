<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>

    <!-- Toast global -->
    <Toast />
  </div>
</template>

<script setup>
import Toast from '~/components/Toast.vue'
</script>
