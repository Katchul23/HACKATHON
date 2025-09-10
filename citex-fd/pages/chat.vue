<template>
  <div class="flex h-screen overflow-hidden">
    <div class="flex-1 flex flex-col">
      <ChatInterface
        :messages="messages"
        :sessions="sessions"
        :loading="loading"
        @submit="handlePrompt"
        @upload="handleUpload"
        @select="selectSession"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ChatInterface from '~/components/ChatInterface.vue'
import type { ChatMessage, ChatSession } from '~/types/chat'
import { useChatContext } from '~/composables/useChatContext'

const config = useRuntimeConfig()

const messages = ref<ChatMessage[]>([])
const sessions = ref<ChatSession[]>([])
const selectedId = ref<number | null>(null)
const loading = ref(false)

const { chatContext, updateFromBackend, clearContext } = useChatContext()

const handlePrompt = async (prompt: string) => {
  loading.value = true
  messages.value.push({ sender: 'user', text: prompt })

  try {
   const { token } = useAuth()
    const { data } = await useFetch(`${config.public.apiBase}/chat/`, {
      method: 'POST',
      body: {
        prompt,
        sessionId: selectedId.value,
        context: chatContext.value,
        expecting: chatContext.value.expecting
      },
      headers: {
        Authorization: `Bearer ${token.value}`  // ✅ très important
      }
})
    if (data.value) {
      messages.value.push({ sender: 'assistant', text: data.value.response })
      updateFromBackend(data.value.context || {})
    }
  } catch {
    messages.value.push({ sender: 'assistant', text: '❌ Erreur de réponse' })
  } finally {
    loading.value = false
  }
}

const handleUpload = async (file: File) => {
  loading.value = true
  const filename = file.name
  messages.value.push({ sender: 'user', text: `📎 J’ai envoyé un document : ${filename}` })

  const formData = new FormData()
  formData.append('file', file)

  try {
    const { data } = await useFetch(`${config.public.apiBase}/chat/upload`, {
      method: 'POST',
      body: formData
    })

    if (data.value) {
      messages.value.push({ sender: 'assistant', text: data.value.response || '✅ Fichier analysé avec succès.' })
      if (data.value.preview) {
        messages.value.push({ sender: 'assistant', text: `📝 **Aperçu extrait du document :**\n\n${data.value.preview}` })
      }
      updateFromBackend(data.value.context || {})
    }
  } catch {
    messages.value.push({ sender: 'assistant', text: '❌ Erreur lors de l’analyse du fichier.' })
  } finally {
    loading.value = false
  }
}

const selectSession = async (id: number) => {
  selectedId.value = id
  messages.value = []

  try {
    const { data } = await useFetch(`${config.public.apiBase}/chat/history/${id}`)
    if (data.value?.messages) {
      messages.value = data.value.messages
    }
  } catch {
    console.warn('❌ Erreur chargement messages')
  }
}

onMounted(async () => {
  try {
    const { data } = await useFetch(`${config.public.apiBase}/chat/history`)
    if (data.value?.sessions) {
      sessions.value = data.value.sessions
    }
  } catch {
    console.warn('Erreur lors du chargement des sessions')
  }
})
</script>
