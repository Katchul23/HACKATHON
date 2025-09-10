<!-- CitationTable.vue -->
<template>
  <div class="overflow-x-auto bg-white shadow rounded-lg border">
    <table class="min-w-full table-auto text-sm text-left">
      <thead class="bg-gray-100 border-b">
        <tr>
          <th class="px-4 py-2 font-semibold">#</th>
          <th class="px-4 py-2 font-semibold">Texte</th>
          <th class="px-4 py-2 font-semibold">Type</th>
          <th class="px-4 py-2 font-semibold">Contexte</th>
          <th class="px-4 py-2 font-semibold">Source</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="r in citations"
          :key="r.phrase_index"
          class="border-b hover:bg-gray-50"
        >
          <td class="px-4 py-2">{{ r.phrase_index }}</td>
          <td class="px-4 py-2 text-gray-700 max-w-xs truncate" :title="r.citation_text">
            {{ r.citation_text }}
          </td>
          <td class="px-4 py-2">
            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
              {{ r.type_de_donnee }}
            </span>
          </td>
          <td class="px-4 py-2 text-gray-600 max-w-xs truncate" :title="r.contexte">
            {{ r.contexte }}
          </td>
          <td class="px-4 py-2 text-blue-600">
            <a v-if="r.source" :href="r.source" target="_blank" class="hover:underline">
              [Lien]
            </a>
            <span v-else class="italic text-gray-400">-</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  citations: {
    type: Array,
    required: true
  }
})
</script>
