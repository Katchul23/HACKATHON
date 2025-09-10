// 5. UploadZone.vue
<template>
  <div class="fixed bottom-4 right-4">
    <label class="cursor-pointer bg-white border px-3 py-2 rounded shadow">
      📎 Importer PDF
      <input type="file" accept="application/pdf" class="hidden" @change="handle" />
    </label>
  </div>
</template>

<script setup>
const emit = defineEmits(['file'])
const handle = (e) => {
  const file = e.target.files[0]
  if (file) emit('file', file)
}
</script>