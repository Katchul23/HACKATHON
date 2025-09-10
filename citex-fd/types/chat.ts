// ~/types/chat.ts

export interface ChatMessage {
  sender: 'user' | 'assistant'
  text: string
  timestamp?: string
}

export interface ChatSession {
  id: number
  titre: string
  doi: string
  date_analyse: string
}

export interface ChatState {
  sessions: ChatSession[]
  selectedSessionId?: number
}