import { useCallback, useRef } from 'react'
import type { SSEMetadata } from '../types'

interface SSECallbacks {
  onMetadata: (metadata: SSEMetadata) => void
  onToken: (content: string) => void
  onDone: () => void
  onError: (error: Error) => void
}

export function useSSEParser() {
  const abortRef = useRef<AbortController | null>(null)

  const parseSSE = useCallback(async (response: Response, callbacks: SSECallbacks) => {
    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed || !trimmed.startsWith('data: ')) continue

          const jsonStr = trimmed.slice(6)
          if (jsonStr === '[DONE]') {
            callbacks.onDone()
            return
          }

          try {
            const data = JSON.parse(jsonStr)
            if (data.type === 'metadata') {
              callbacks.onMetadata(data.metadata)
            } else if (data.type === 'token') {
              callbacks.onToken(data.content)
            } else if (data.type === 'done') {
              callbacks.onDone()
              return
            } else if (data.type === 'error') {
              callbacks.onError(new Error(data.message || 'Stream error'))
              return
            }
          } catch {
            // skip malformed JSON lines
          }
        }
      }
      // Process remaining buffer
      if (buffer.trim()) {
        const trimmed = buffer.trim()
        if (trimmed.startsWith('data: ')) {
          const jsonStr = trimmed.slice(6)
          try {
            const data = JSON.parse(jsonStr)
            if (data.type === 'done') {
              callbacks.onDone()
            } else if (data.type === 'token') {
              callbacks.onToken(data.content)
              callbacks.onDone()
            }
          } catch {
            // skip
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        callbacks.onError(err as Error)
      }
    }
  }, [])

  const abort = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return { parseSSE, abort, abortRef }
}
