<template>
  <div class="p-6 max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Analyseur de Citations de Données</h1>

    <Alert
      v-if="alert && alert.message"
      :type="alert.type"
      :title="alert.title"
      :message="alert.message"
      @close="clear"
    />

    <form @submit.prevent="handleSubmit">
      <input
        v-model="source"
        type="text"
        placeholder="DOI, URL ou texte brut..."
        class="w-full mb-3 p-2 border rounded"
      />

      <select v-model="section" class="w-full mb-4 p-2 border rounded">
        <option value="all">🔎 Toutes les sections</option>
        <option value="méthodologie">📘 Méthodologie</option>
        <option value="résultats">📊 Résultats</option>
        <option value="conclusion">📌 Conclusion</option>
      </select>

      <button
        type="submit"
        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
      >
        Analyser
      </button>
    </form>

    <div v-if="loading" class="mt-6 text-blue-600">⏳ Analyse en cours...</div>

    <CitationTable
      v-if="results.length"
      class="mt-6"
      :citations="results"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAlert } from '~/composables/useAlert'
import Alert from '~/components/Alert.vue'
import { useCitationAnalyse } from '~/composables/useCitationAnalyse'
import CitationTable from '~/components/CitationTable.vue'
import type { AlertType } from '~/composables/useAlert'

const source = ref("")
const section = ref("all")

const { results, loading, submitAnalyse } = useCitationAnalyse(source, section)
const { alert, show, clear } = useAlert()

const handleSubmit = async () => {
  clear()
  try {
    await submitAnalyse()
    if (results.value.length === 0) {
      show({
        type: 'info' as AlertType,
        title: 'Aucune citation détectée',
        message: 'Aucune mention de donnée n’a été trouvée.'
      })
    } else {
      show({
        type: 'success' as AlertType,
        title: 'Analyse réussie',
        message: `${results.value.length} citation(s) trouvée(s).`
      })
    }
  } catch (err) {
    show({
      type: 'error' as AlertType,
      title: 'Erreur',
      message: 'Échec de l’analyse. Vérifie la source ou réessaie.'
    })
  }
}
</script>
