import { ref } from 'vue'

export function useCitationAnalyse(source: any, section: any) {
  const results = ref([])
  const loading = ref(false)
  const config = useRuntimeConfig()

  const submitAnalyse = async () => {
    loading.value = true
    try {
      const response = await fetch(`${config.public.apiBase}/articles/analyse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          source: source.value,
          section: section.value,
          min_confidence: 0.6
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      results.value = data?.citations || []
    } catch (err) {
      console.error("Erreur analyse :", err)
    } finally {
      loading.value = false
    }
  }

  return { results, loading, submitAnalyse }
}
