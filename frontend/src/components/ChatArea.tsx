import { useRef, useEffect } from 'react'
import { Input, Button, Spin } from 'antd'
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../types'
import styles from './ChatArea.module.css'

interface Props {
  messages: ChatMessage[]
  inputValue: string
  onInputChange: (val: string) => void
  onSend: () => void
  sending: boolean
}

export default function ChatArea({ messages, inputValue, onInputChange, onSend, sending }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!sending && inputValue.trim()) {
        onSend()
      }
    }
  }

  return (
    <div className={styles.chatArea}>
      <div className={styles.messages} ref={scrollRef}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.messageRow} ${msg.role === 'user' ? styles.userRow : styles.assistantRow}`}
          >
            <div className={`${styles.avatar} ${msg.role === 'user' ? styles.userAvatar : styles.aiAvatar}`}>
              {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
            </div>
            <div className={`${styles.bubble} ${msg.role === 'user' ? styles.userBubble : styles.aiBubble}`}>
              {msg.role === 'assistant' ? (
                <div className="markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                  {msg.isStreaming && <span className={styles.cursor}>▊</span>}
                </div>
              ) : (
                <div>{msg.content}</div>
              )}
            </div>
          </div>
        ))}
        {sending && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
          <div className={`${styles.messageRow} ${styles.assistantRow}`}>
            <div className={`${styles.avatar} ${styles.aiAvatar}`}>
              <RobotOutlined />
            </div>
            <div className={`${styles.bubble} ${styles.aiBubble}`}>
              <Spin size="small" />
              <span style={{ marginLeft: 8, color: 'var(--gray-400)' }}>正在思考…</span>
            </div>
          </div>
        )}
      </div>
      <div className={styles.inputArea}>
        <Input.TextArea
          ref={inputRef as never}
          className={styles.textInput}
          value={inputValue}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="继续追问或反馈…"
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={sending}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={onSend}
          loading={sending}
          disabled={!inputValue.trim() || sending}
          className={styles.sendBtn}
        >
          发送
        </Button>
      </div>
    </div>
  )
}
