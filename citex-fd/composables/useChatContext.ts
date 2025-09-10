// composables/useChatContext.ts
import { ref } from 'vue'

export type ExpectedField = 'doi' | 'section' | 'type'
export type ChatAction = 'citations' | 'analyse' | 'summary'

export interface ChatContextState {
  expecting?: ExpectedField
  last_action?: ChatAction
  pending_prompt?: string
}

const chatContext = ref<ChatContextState>({})

export function useChatContext() {
  /**
   * Définit complètement un nouveau contexte
   */
  const setContext = (ctx: ChatContextState) => {
    chatContext.value = { ...ctx }
  }

  /**
   * Réinitialise tout le contexte
   */
  const clearContext = () => {
    chatContext.value = {}
  }

  /**
   * Met à jour les champs connus depuis un payload (ex: retour du backend)
   */
  const updateFromBackend = (contextPayload: Partial<ChatContextState>) => {
    if (!contextPayload) return
    chatContext.value = {
      ...chatContext.value,
      ...contextPayload
    }
  }

  /**
   * Renvoie l'état courant
   */
  const getContext = () => chatContext.value

  return {
    chatContext,
    setContext,
    clearContext,
    updateFromBackend,
    getContext
  }
}
