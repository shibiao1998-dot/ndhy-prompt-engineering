import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { createConversation } from '../services/api'
import styles from './Home.module.css'

const SUGGESTIONS = [
  '帮我设计一个AI智能客服系统的提示词',
  '为数据分析报告生成器设计系统指令',
  '设计一个代码审查助手的提示词框架',
  '创建一个多轮对话式教学助手提示词',
]

export default function Home() {
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = useCallback(async (text?: string) => {
    const query = (text || inputValue).trim()
    if (!query || loading) return

    setLoading(true)
    try {
      const conv = await createConversation(query.slice(0, 50))
      // Navigate to chat page with the initial query
      navigate(`/chat/${conv.id}`, { state: { initialQuery: query } })
    } catch (err) {
      console.error('Failed to create conversation:', err)
      setLoading(false)
    }
  }, [inputValue, loading, navigate])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className={styles.container}>
      {/* Ambient glow */}
      <div className={styles.ambientGlow} />

      {/* Hero */}
      <div className={styles.hero}>
        <div className={styles.badge}>AI 设计师</div>
        <h1 className={styles.title}>描述你的需求</h1>
        <p className={styles.subtitle}>
          AI 设计师将为你量身定制专业方案，支持多轮对话持续优化
        </p>
      </div>

      {/* Input area */}
      <div className={styles.inputWrapper}>
        <div className={styles.inputBox}>
          <textarea
            className={styles.textarea}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="描述你的设计任务，例如：帮我设计一个智能客服系统的提示词..."
            rows={3}
            disabled={loading}
          />
          <div className={styles.inputFooter}>
            <span className={styles.hint}>按 Enter 发送，Shift + Enter 换行</span>
            <button
              className={`${styles.submitBtn} ${(!inputValue.trim() || loading) ? styles.submitBtnDisabled : ''}`}
              onClick={() => handleSubmit()}
              disabled={!inputValue.trim() || loading}
            >
              {loading ? (
                <span className={styles.loadingDots}>
                  <span>●</span><span>●</span><span>●</span>
                </span>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                  开始对话
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Suggestions */}
      <div className={styles.suggestions}>
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            className={styles.suggestionChip}
            onClick={() => {
              setInputValue(s)
              handleSubmit(s)
            }}
            disabled={loading}
          >
            <span className={styles.suggestionIcon}>✦</span>
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
