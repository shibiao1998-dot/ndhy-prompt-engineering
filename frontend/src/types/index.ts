// ─── Conversation ─────────────────────────────────────────────

export interface Conversation {
  id: string
  title: string | null
  created_at: string
  updated_at: string
}

// ─── Message ──────────────────────────────────────────────────

export interface Message {
  id: number
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

// ─── Chat UI ──────────────────────────────────────────────────

export interface ChatMessage {
  id: string | number
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
}

// ─── Dimensions ───────────────────────────────────────────────

export interface Dimension {
  id: string
  name: string
  category: string
  category_name: string | null
  description: string | null
  data_source: string | null
  update_frequency: string | null
  source_explanation: string | null
  level: number | null
  created_at: string | null
  updated_at: string | null
}

export interface DimensionUpdate {
  name?: string
  description?: string
  data_source?: string
  update_frequency?: string
  source_explanation?: string
}

export interface Category {
  key: string
  name: string
  count: number
}

// ─── SSE Events ───────────────────────────────────────────────

export interface SSETokenEvent {
  type: 'token'
  content: string
}

export interface SSEMetadataEvent {
  type: 'metadata'
  conversation_id: string
}

export interface SSEDoneEvent {
  type: 'done'
  content: string
}

export interface SSEErrorEvent {
  type: 'error'
  content: string
}

export type SSEEvent = SSETokenEvent | SSEMetadataEvent | SSEDoneEvent | SSEErrorEvent
