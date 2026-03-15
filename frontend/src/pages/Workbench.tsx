import { useState, useCallback, useEffect } from 'react'
import { Input, Button, Tag } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import ChatArea from '../components/ChatArea'
import HoodPanel from '../components/HoodPanel'
import { useSSEParser } from '../hooks/useSSEParser'
import { createConversation, sendChatMessage, getDimensionStats } from '../services/api'
import type { ChatMessage, SSEMetadata, DimensionStats } from '../types'
import styles from './Workbench.module.css'

const CATEGORY_COLORS: Record<string, string> = {
  A: '#1B65A9', B: '#0891B2', C: '#7C3AED', D: '#C2410C',
  E: '#059669', F: '#D97706', G: '#DC2626', H: '#4F46E5',
  I: '#0D9488', J: '#9333EA', K: '#EA580C', L: '#2563EB',
}

export default function Workbench() {
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [metadata, setMetadata] = useState<SSEMetadata | null>(null)
  const [hoodCollapsed, setHoodCollapsed] = useState(false)
  const [stats, setStats] = useState<DimensionStats | null>(null)
  const { parseSSE } = useSSEParser()

  useEffect(() => {
    getDimensionStats().then(setStats).catch(console.error)
  }, [])

  const isConversationActive = conversationId !== null

  const handleSend = useCallback(async () => {
    const text = inputValue.trim()
    if (!text || sending) return

    setInputValue('')
    setSending(true)

    try {
      let convId = conversationId
      if (!convId) {
        const conv = await createConversation(text.slice(0, 50))
        convId = conv.id
        setConversationId(convId)
      }

      // Add user message
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: text,
      }
      setMessages((prev) => [...prev, userMsg])

      // Add placeholder assistant message
      const assistantId = `assistant-${Date.now()}`
      const assistantMsg: ChatMessage = {
        id: assistantId,
        role: 'assistant',
        content: '',
        isStreaming: true,
      }
      setMessages((prev) => [...prev, assistantMsg])

      // Send and parse SSE
      const response = await sendChatMessage(convId, text)

      await parseSSE(response, {
        onMetadata: (meta: SSEMetadata) => {
          setMetadata(meta)
        },
        onToken: (content: string) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: m.content + content }
                : m
            )
          )
        },
        onDone: () => {
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
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: m.content + '\n\n⚠️ 连接中断，请重试', isStreaming: false }
                : m
            )
          )
        },
      })
    } catch (err) {
      console.error('Send error:', err)
    } finally {
      setSending(false)
    }
  }, [inputValue, sending, conversationId, parseSSE])

  const handleInitialSend = useCallback(() => {
    handleSend()
  }, [handleSend])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!sending && inputValue.trim()) {
        handleInitialSend()
      }
    }
  }

  if (!isConversationActive) {
    return (
      <div className={styles.emptyState}>
        {/* 左侧主区域 */}
        <div className={styles.mainArea}>
          {/* 居中标题 */}
          <div className={styles.heroSection}>
            <h1 className={styles.heroTitle}>你需要设计什么？</h1>
            <p className={styles.heroSubtitle}>AI 将调用 {stats?.total_dimensions || 99} 个知识维度，为你产出专业设计方案</p>
          </div>

          {/* 底部输入栏 */}
          <div className={styles.inputDock}>
            <div className={styles.inputBar}>
              <Input.TextArea
                className={styles.inputField}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="描述你的设计任务..."
                autoSize={{ minRows: 1, maxRows: 4 }}
                variant="borderless"
              />
              <Button
                type="primary"
                shape="circle"
                icon={<SendOutlined />}
                onClick={handleInitialSend}
                loading={sending}
                disabled={!inputValue.trim()}
                className={styles.sendBtn}
              />
            </div>
          </div>
        </div>

        {/* 右侧维度竖条 */}
        <div className={styles.dimensionSidebar}>
          <div className={styles.sidebarTitle}>知识维度</div>
          {stats && (
            <div className={styles.sidebarStats}>
              <span className={styles.sidebarStatNum}>{stats.total_dimensions}</span> 维度 · <span className={styles.sidebarStatNum}>{(stats.overall_fill_rate * 100).toFixed(0)}%</span>
            </div>
          )}
          {stats?.by_category.map((cat, i) => (
            <div
              key={cat.category}
              className={styles.dimCard}
              style={{ animationDelay: `${i * 0.04}s` }}
            >
              <div className={styles.dimCardHeader}>
                <Tag color={CATEGORY_COLORS[cat.category] || '#666'} style={{ margin: 0, fontSize: 10, lineHeight: '18px', padding: '0 4px' }}>
                  {cat.category}
                </Tag>
                <span className={styles.dimCardName}>{cat.category_name}</span>
              </div>
              <div className={styles.dimCardBar}>
                <div
                  className={styles.dimCardBarFill}
                  style={{
                    width: `${cat.fill_rate * 100}%`,
                    backgroundColor: CATEGORY_COLORS[cat.category] || '#666',
                  }}
                />
              </div>
              <div className={styles.dimCardStat}>
                {cat.filled}/{cat.total}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className={styles.conversationLayout}>
      <div className={styles.chatPanel}>
        <ChatArea
          messages={messages}
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSend={handleSend}
          sending={sending}
        />
      </div>
      <HoodPanel
        metadata={metadata}
        collapsed={hoodCollapsed}
        onToggle={() => setHoodCollapsed((c) => !c)}
      />
    </div>
  )
}
