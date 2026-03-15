import type {
  Dimension,
  DimensionStats,
  Conversation,
  Message,
  Engine,
  ReviewPayload,
} from '../types'

const BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API Error ${res.status}: ${error}`)
  }
  return res.json()
}

// Dimensions
export async function getDimensions(category?: string): Promise<Dimension[]> {
  const params = category ? `?category=${encodeURIComponent(category)}` : ''
  return request<Dimension[]>(`/dimensions${params}`)
}

export async function getDimension(id: string): Promise<Dimension> {
  return request<Dimension>(`/dimensions/${id}`)
}

export async function createDimension(data: Partial<Dimension>): Promise<Dimension> {
  return request<Dimension>('/dimensions', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateDimension(id: string, data: Partial<Dimension>): Promise<Dimension> {
  return request<Dimension>(`/dimensions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteDimension(id: string): Promise<void> {
  await request<unknown>(`/dimensions/${id}`, { method: 'DELETE' })
}

export async function reviewDimension(id: string, payload: ReviewPayload): Promise<Dimension> {
  return request<Dimension>(`/dimensions/${id}/review`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// Stats
export async function getDimensionStats(): Promise<DimensionStats> {
  return request<DimensionStats>('/stats/dimensions')
}

// Conversations
export async function createConversation(title?: string): Promise<Conversation> {
  return request<Conversation>('/conversations', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
}

export async function getConversationHistory(conversationId: string): Promise<Message[]> {
  return request<Message[]>(`/chat/${conversationId}/history`)
}

// Engines
export async function getEngines(): Promise<Engine[]> {
  return request<Engine[]>('/engines')
}

// Prompt
export async function adaptPrompt(promptText: string, engineId: string): Promise<{ adapted_prompt: string; engine: Engine }> {
  return request<{ adapted_prompt: string; engine: Engine }>('/prompt/adapt', {
    method: 'POST',
    body: JSON.stringify({ prompt_text: promptText, engine_id: engineId }),
  })
}

// SSE Chat - returns a ReadableStream reader
export async function sendChatMessage(
  conversationId: string,
  message: string,
): Promise<Response> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, message }),
  })
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`Chat API Error ${res.status}: ${error}`)
  }
  return res
}
