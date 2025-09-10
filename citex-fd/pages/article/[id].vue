<template>
  <div class="max-w-5xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">🧾 Détails de l'article</h1>

    <!-- 🔔 Affichage de l’alerte -->
    <Alert
      v-if="alert && alert.message"
      :type="alert.type"
      :title="alert.title"
      :message="alert.message"
      @close="clear"
    />

    <div v-if="article">
      <div class="bg-white shadow p-4 rounded mb-6">
        <p><strong>Titre :</strong> {{ article.titre }}</p>
        <p><strong>DOI :</strong> {{ article.doi || 'Non disponible' }}</p>
        <p><strong>Auteurs :</strong> {{ article.auteurs }}</p>
        <p><strong>Section analysée :</strong> {{ article.section_analysee }}</p>
        <p><strong>Date d’analyse :</strong> {{ new Date(article.date_analyse).toLocaleString() }}</p>
      </div>

      <h2 class="text-xl font-semibold mb-2">📚 Citations détectées</h2>

      <div v-if="article.citations.length">
        <table class="min-w-full bg-white border border-gray-300">
          <thead>
            <tr class="bg-gray-100 text-left text-sm">
              <th class="p-2 border">#</th>
              <th class="p-2 border">Type</th>
              <th class="p-2 border">Contexte</th>
              <th class="p-2 border">Source</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(citation, index) in article.citations" :key="citation.id" class="text-sm hover:bg-gray-50">
              <td class="p-2 border">{{ index + 1 }}</td>
              <td class="p-2 border font-medium">
                <span :class="{
                  'text-green-600': citation.type_de_donnee === 'primaire',
                  'text-blue-600': citation.type_de_donnee === 'secondaire'
                }">{{ citation.type_de_donnee }}</span>
              </td>
              <td class="p-2 border">{{ citation.contexte || citation.texte }}</td>
              <td class="p-2 border text-xs truncate">{{ citation.source || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-gray-500 mt-4">Aucune citation enregistrée.</div>
    </div>

    <div v-else class="text-gray-600 text-sm">Chargement en cours...</div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAlert } from '~/composables/useAlert'
import Alert from '~/components/Alert.vue'

const route = useRoute()
const id = route.params.id
const config = useRuntimeConfig()

const { alert, show, clear } = useAlert()

const { data: article, error } = await useFetch(`${config.public.apiBase}/articles/${id}`)

if (error.value) {
  show({
    type: 'error',
    title: 'Chargement échoué',
    message: `Impossible de charger l'article ID ${id}`
  })
}
</script>
