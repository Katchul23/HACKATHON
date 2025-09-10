<template>
  <div class="flex h-screen bg-gray-50">
    <!-- 📁 Historique -->
    <Sidebar
      :sessions="sessions"
      @select="(id) => $emit('select', id)"
    />

    <!-- 💬 Espace Chat -->
    <div class="flex-1 flex flex-col">
      <div class="flex-1 overflow-y-auto p-6 space-y-3">
        <ChatMessage
          v-for="(msg, i) in messages"
          :key="i"
          :sender="msg.sender"
          :text="msg.text"
        />
      </div>

      <!-- ⌨️ Saisie utilisateur -->
      <PromptInput
        @submit="(text) => $emit('submit', text)"
        :loading="loading"
      />
    </div>

    <!-- 📎 Zone d'upload -->
    <UploadZone
      @file="(file) => $emit('upload', file)"
    />
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import PromptInput from './PromptInput.vue'
import UploadZone from './UploadZone.vue'
import ChatMessage from './ChatMessage.vue'
import type { ChatMessage as Msg, ChatSession } from '~/types/chat'

defineProps<{
  messages: Msg[]
  sessions: ChatSession[]
  loading: boolean
}>()

defineEmits<{
  (e: 'submit', prompt: string): void
  (e: 'upload', file: File): void
  (e: 'select', id: number): void
}>()
</script>
