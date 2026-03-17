import { useState, useCallback, useEffect, useRef } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useSSEParser } from '../hooks/useSSEParser'
import { sendChatMessage, getConversationHistory } from '../services/api'
import type { ChatMessage } from '../types'
import styles from './Chat.module.css'

export default function Chat() {
  const { id: conversationId } = useParams<{ id: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [statusText, setStatusText] = useState<string | null>(null)
  const initializedRef = useRef(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { parseSSE } = useSSEParser()

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  // Focus input after sending
  useEffect(() => {
    if (!sending && inputRef.current) {
      inputRef.current.focus()
    }
  }, [sending])

  // Core: stream AI response for a given text, adding only the assistant bubble
  const streamAIResponse = useCallback(async (text: string, skipUserMsg: boolean) => {
    if (!text.trim() || !conversationId || sending) return

    setSending(true)

    // Only add user message bubble if this is a fresh send (not a retry)
    if (!skipUserMsg) {
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: text.trim(),
      }
      setMessages((prev) => [...prev, userMsg])
    }

    // Add placeholder assistant message
    const assistantId = `assistant-${Date.now()}`
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      isStreaming: true,
    }
    setMessages((prev) => [...prev, assistantMsg])

    try {
      const response = await sendChatMessage(conversationId, text.trim())

      await parseSSE(response, {
        onToken: (content: string) => {
          setStatusText(null) // Clear status once tokens start flowing
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: m.content + content }
                : m
            )
          )
        },
        onDone: () => {
          setStatusText(null)
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, isStreaming: false }
                : m
            )
          )
        },
        onError: (error: Error) => {
          console.error('SSE Error:', error)
          setStatusText(null)
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: m.content + '\n\n⚠️ 连接中断：' + error.message, isStreaming: false }
                : m
            )
          )
        },
        onStatus: (content: string) => {
          setStatusText(content)
        },
      })
    } catch (err) {
      console.error('Send error:', err)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: '⚠️ 发送失败，请重试', isStreaming: false }
            : m
        )
      )
    } finally {
      setSending(false)
    }
  }, [conversationId, sending, parseSSE])

  // Public send: adds user bubble + streams AI response
  const doSend = useCallback(async (text: string) => {
    return streamAIResponse(text, false)
  }, [streamAIResponse])

  // Initialize: load history or send initial query (useRef to survive StrictMode remount)
  useEffect(() => {
    if (!conversationId || initializedRef.current) return
    initializedRef.current = true

    const state = location.state as { initialQuery?: string } | null

    if (state?.initialQuery) {
      // New conversation — send the initial query immediately
      doSend(state.initialQuery)
      // Clear location state so refresh doesn't re-send
      window.history.replaceState({}, '')
    } else {
      // Returning to existing conversation — load history
      getConversationHistory(conversationId)
        .then((data) => {
          if (data.messages && data.messages.length > 0) {
            const loaded = data.messages.map((m) => ({
              id: m.id,
              role: m.role as 'user' | 'assistant',
              content: m.content,
            }))
            setMessages(loaded)

            // If last message is from user (no AI reply yet — e.g. page was
            // refreshed while AI was still streaming), re-trigger AI response
            // without duplicating the user message
            const last = loaded[loaded.length - 1]
            if (last.role === 'user') {
              streamAIResponse(last.content, true)
            }
          }
        })
        .catch(console.error)
    }
  }, [conversationId, location.state, doSend])

  const handleSend = useCallback(() => {
    if (!inputValue.trim() || sending) return
    const text = inputValue
    setInputValue('')
    doSend(text)
  }, [inputValue, sending, doSend])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={styles.container}>
      {/* Messages area */}
      <div className={styles.messages} ref={scrollRef}>
        {messages.length === 0 && !sending && (
          <div className={styles.emptyHint}>
            <span className={styles.emptyIcon}>💬</span>
            <p>对话即将开始...</p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.messageRow} ${msg.role === 'user' ? styles.userRow : styles.assistantRow}`}
          >
            {msg.role === 'assistant' && (
              <div className={styles.avatarCol}>
                <div className={styles.aiAvatar}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                  </svg>
                </div>
                <span className={styles.avatarLabel}>AI 设计师</span>
              </div>
            )}

            <div className={`${styles.bubble} ${msg.role === 'user' ? styles.userBubble : styles.aiBubble}`}>
              {msg.role === 'assistant' ? (
                <div className={styles.markdown}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content || (msg.isStreaming ? '' : '(空回复)')}
                  </ReactMarkdown>
                  {msg.isStreaming && <span className={styles.cursor}>▊</span>}
                </div>
              ) : (
                <div className={styles.userText}>{msg.content}</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input area */}
      <div className={styles.inputArea}>
        <div className={styles.inputBox}>
          <textarea
            ref={inputRef}
            className={styles.textarea}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={sending ? (statusText || 'AI 设计师正在思考...') : '继续输入你的需求，对结果进行优化...'}
            rows={1}
            disabled={sending}
          />
          <button
            className={`${styles.sendBtn} ${(!inputValue.trim() || sending) ? styles.sendBtnDisabled : ''}`}
            onClick={handleSend}
            disabled={!inputValue.trim() || sending}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <div className={styles.inputHint}>
          <button className={styles.newChatBtn} onClick={() => navigate('/')}>
            + 新对话
          </button>
          <span>AI 设计师 · 由 AIhub 提供对话能力</span>
        </div>
      </div>
    </div>
  )
}
