import type { Conversation, Message, Dimension, DimensionUpdate, Category } from '../types'

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

// ─── Conversations ────────────────────────────────────────────

export async function createConversation(title?: string): Promise<Conversation> {
  return request<Conversation>('/conversations', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
}

export async function getConversationHistory(conversationId: string): Promise<{
  conversation: Conversation
  messages: Message[]
}> {
  return request(`/chat/${conversationId}/history`)
}

// ─── Chat SSE ─────────────────────────────────────────────────

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

// ─── Dimensions ──────────────────────────────────────────────

export async function getCategories(): Promise<Category[]> {
  return request<Category[]>('/dimensions/categories')
}

export async function getDimensions(category?: string): Promise<Dimension[]> {
  const url = category ? `/dimensions?category=${encodeURIComponent(category)}` : '/dimensions'
  return request<Dimension[]>(url)
}

export async function getDimension(id: string): Promise<Dimension> {
  return request<Dimension>(`/dimensions/${id}`)
}

export async function updateDimension(id: string, data: DimensionUpdate): Promise<Dimension> {
  return request<Dimension>(`/dimensions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteDimension(id: string): Promise<{ message: string }> {
  return request<{ message: string }>(`/dimensions/${id}`, { method: 'DELETE' })
}
