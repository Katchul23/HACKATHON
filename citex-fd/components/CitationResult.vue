<template>
  <div class="rounded-lg border p-4 shadow-sm bg-white mb-4">
    <h3 class="font-semibold text-lg mb-2">Phrase {{ result.phrase_index }}</h3>

    <p class="mb-2">
      <span class="font-medium">Texte :</span>
      <span class="text-gray-700">{{ result.citation_text }}</span>
    </p>

    <p class="mb-2">
      <span class="font-medium">Type de données :</span>
      <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
        {{ result.type_de_donnee }}
      </span>
    </p>

    <p class="mb-2">
      <span class="font-medium">Contexte :</span>
      <span class="text-gray-700">{{ result.contexte }}</span>
    </p>

    <p class="mb-2">
      <span class="font-medium">Source :</span>
      <a v-if="result.source" :href="result.source" class="text-blue-600 hover:underline" target="_blank">
        {{ result.source }}
      </a>
      <span v-else class="italic text-gray-500">non spécifiée</span>
    </p>

    <div v-if="result.source_metadata" class="mt-2 text-sm text-gray-600 border-t pt-2">
      <p><span class="font-medium">Titre :</span> {{ result.source_metadata.titre }}</p>
      <p><span class="font-medium">Auteurs :</span> {{ result.source_metadata.auteurs?.join(', ') }}</p>
      <p><span class="font-medium">Journal :</span> {{ result.source_metadata.journal }}</p>
      <p><span class="font-medium">Année :</span> {{ result.source_metadata.annee }}</p>
      <p><span class="font-medium">Éditeur :</span> {{ result.source_metadata.editeur }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    required: true
  }
})
</script>
