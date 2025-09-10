import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export type Toast = {
  id: number
  type: ToastType
  message: string
}

const toasts = ref<Toast[]>([])

export function useToast() {
  function show({
    type,
    message,
    duration = 4000
  }: {
    type: ToastType
    message: string
    duration?: number
  }) {
    const id = Date.now() + Math.random()
    toasts.value.push({ id, type, message })

    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, duration)
  }

  return {
    toasts,
    show
  }
}
