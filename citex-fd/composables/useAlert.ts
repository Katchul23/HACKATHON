import { ref } from 'vue'

export type AlertType = 'success' | 'error' | 'info' | 'warning'

export const alert = ref<{
  type: AlertType
  title: string
  message: string
} | null>(null)

export function useAlert() {
  function show({
    type,
    title,
    message
  }: {
    type: AlertType // 🔐 typage littéral
    title: string
    message: string
  }) {
    alert.value = { type, title, message }
  }

  function clear() {
    alert.value = null
  }

  return { alert, show, clear }
}
