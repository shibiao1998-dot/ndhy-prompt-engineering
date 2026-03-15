import { useState, useEffect, useMemo } from 'react'
import { Collapse, Tag, Button, Tooltip, Spin, message, Progress } from 'antd'
import { CopyOutlined, CheckCircleFilled, WarningFilled } from '@ant-design/icons'
import type { SSEMetadata, Engine, DimensionUsed } from '../types'
import { getEngines, adaptPrompt } from '../services/api'
import styles from './HoodPanel.module.css'

interface Props {
  metadata: SSEMetadata | null
  collapsed: boolean
  onToggle: () => void
}

export default function HoodPanel({ metadata, collapsed, onToggle }: Props) {
  const [engines, setEngines] = useState<Engine[]>([])
  const [selectedEngine, setSelectedEngine] = useState<string | null>(null)
  const [adaptedPrompt, setAdaptedPrompt] = useState<string>('')
  const [adapting, setAdapting] = useState(false)

  useEffect(() => {
    getEngines().then(setEngines).catch(console.error)
  }, [])

  const handleAdapt = async (engineId: string) => {
    if (!metadata?.prompt_snapshot) return
    setSelectedEngine(engineId)
    setAdapting(true)
    try {
      const result = await adaptPrompt(metadata.prompt_snapshot, engineId)
      setAdaptedPrompt(result.adapted_prompt)
    } catch (err) {
      message.error('引擎适配失败')
      console.error(err)
    } finally {
      setAdapting(false)
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(
      () => message.success('已复制到剪贴板'),
      () => message.error('复制失败')
    )
  }

  const groupedDimensions = useMemo(() => {
    if (!metadata?.dimensions_used) return { required: [], recommended: [], optional: [] }
    const dims = metadata.dimensions_used
    return {
      required: dims.filter((d: DimensionUsed) => d.priority === 1),
      recommended: dims.filter((d: DimensionUsed) => d.priority === 2),
      optional: dims.filter((d: DimensionUsed) => d.priority === 3),
    }
  }, [metadata?.dimensions_used])

  const stats = metadata?.coverage_stats

  // Split prompt into positive and constraint sections
  const promptSections = useMemo(() => {
    if (!metadata?.prompt_snapshot) return { positive: '', constraints: '' }
    const text = metadata.prompt_snapshot
    const constraintIdx = text.indexOf('═══ 约束与禁忌段 ═══')
    if (constraintIdx === -1) {
      const altIdx = text.indexOf('## 约束与禁忌')
      if (altIdx === -1) return { positive: text, constraints: '' }
      return {
        positive: text.slice(0, altIdx),
        constraints: text.slice(altIdx),
      }
    }
    return {
      positive: text.slice(0, constraintIdx),
      constraints: text.slice(constraintIdx),
    }
  }, [metadata?.prompt_snapshot])

  if (collapsed) {
    return (
      <div className={styles.collapsedBar} onClick={onToggle}>
        <span className={styles.collapsedLabel}>◀ 引擎盖</span>
      </div>
    )
  }

  if (!metadata) {
    return (
      <div className={styles.panel}>
        <div className={styles.panelHeader}>
          <span className={styles.panelTitle}>🔧 引擎盖</span>
          <Button type="text" size="small" onClick={onToggle}>▶ 收起</Button>
        </div>
        <div className={styles.empty}>等待对话开始…</div>
      </div>
    )
  }

  return (
    <div className={styles.panel}>
      <div className={styles.panelHeader}>
        <span className={styles.panelTitle}>🔧 引擎盖</span>
        <Button type="text" size="small" onClick={onToggle}>▶ 收起</Button>
      </div>

      <div className={styles.scrollArea}>
        {/* Module 1: Coverage Report */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>📊 维度覆盖报告</h3>
          {stats && (
            <div className={styles.coverageBlock}>
              <div className={styles.coverageMain}>
                <Progress
                  type="circle"
                  percent={Math.round(stats.coverage_rate * 100)}
                  size={64}
                  strokeColor="#1B65A9"
                  format={(p) => `${p}%`}
                />
                <div className={styles.coverageText}>
                  <div className={styles.coverageNum}>
                    {stats.covered}/{stats.total} 维度
                  </div>
                  <div className={styles.coverageSub}>覆盖率（按权重）</div>
                </div>
              </div>
              <div className={styles.priorityGrid}>
                <div className={styles.priorityItem}>
                  <span className={styles.priorityDot} style={{ background: '#DC2626' }} />
                  必须 {stats.by_priority.required.covered}/{stats.by_priority.required.total}
                </div>
                <div className={styles.priorityItem}>
                  <span className={styles.priorityDot} style={{ background: '#D97706' }} />
                  建议 {stats.by_priority.recommended.covered}/{stats.by_priority.recommended.total}
                </div>
                <div className={styles.priorityItem}>
                  <span className={styles.priorityDot} style={{ background: '#059669' }} />
                  可选 {stats.by_priority.optional.covered}/{stats.by_priority.optional.total}
                </div>
                {stats.truncated > 0 && (
                  <div className={styles.priorityItem}>
                    <WarningFilled style={{ color: '#D97706', marginRight: 4 }} />
                    被截断 {stats.truncated}
                  </div>
                )}
              </div>
            </div>
          )}
        </section>

        {/* Module 2: Used Dimensions */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>📋 已用维度清单</h3>
          <Collapse
            ghost
            size="small"
            items={[
              {
                key: 'required',
                label: <span style={{ color: '#DC2626', fontWeight: 500 }}>🔴 必须维度 ({groupedDimensions.required.length})</span>,
                children: (
                  <div className={styles.dimList}>
                    {groupedDimensions.required.map((d: DimensionUsed) => (
                      <DimItem key={d.id} dim={d} />
                    ))}
                  </div>
                ),
              },
              {
                key: 'recommended',
                label: <span style={{ color: '#D97706', fontWeight: 500 }}>🟡 建议维度 ({groupedDimensions.recommended.length})</span>,
                children: (
                  <div className={styles.dimList}>
                    {groupedDimensions.recommended.map((d: DimensionUsed) => (
                      <DimItem key={d.id} dim={d} />
                    ))}
                  </div>
                ),
              },
              {
                key: 'optional',
                label: <span style={{ color: '#059669', fontWeight: 500 }}>🟢 可选维度 ({groupedDimensions.optional.length})</span>,
                children: (
                  <div className={styles.dimList}>
                    {groupedDimensions.optional.map((d: DimensionUsed) => (
                      <DimItem key={d.id} dim={d} />
                    ))}
                  </div>
                ),
              },
            ]}
          />
        </section>

        {/* Module 3: Prompt Text */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>📝 提示词原文</h3>
          <Collapse
            ghost
            size="small"
            items={[
              {
                key: 'positive',
                label: '正向信息段',
                children: (
                  <pre className={styles.promptText}>{promptSections.positive}</pre>
                ),
              },
              ...(promptSections.constraints
                ? [{
                    key: 'constraints',
                    label: <span style={{ color: '#991B1B' }}>⛔ 约束与禁忌段</span>,
                    children: (
                      <pre className={`${styles.promptText} ${styles.constraintText}`}>
                        {promptSections.constraints}
                      </pre>
                    ),
                  }]
                : []),
            ]}
          />
        </section>

        {/* Module 4: Engine Adaptation */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>🔄 引擎适配预览</h3>
          <div className={styles.engineGrid}>
            {engines.map((engine) => (
              <Tooltip key={engine.id} title={engine.description}>
                <Tag
                  className={`${styles.engineTag} ${selectedEngine === engine.id ? styles.engineTagActive : ''}`}
                  color={engine.is_active ? 'blue' : undefined}
                  onClick={() => handleAdapt(engine.id)}
                  style={{ cursor: 'pointer' }}
                >
                  {engine.name}
                  {engine.is_active && <CheckCircleFilled style={{ marginLeft: 4, fontSize: 10 }} />}
                </Tag>
              </Tooltip>
            ))}
          </div>
          {adapting && <Spin size="small" style={{ display: 'block', margin: '12px auto' }} />}
          {adaptedPrompt && !adapting && (
            <div className={styles.adaptedBlock}>
              <div className={styles.adaptedHeader}>
                <span>{engines.find(e => e.id === selectedEngine)?.name} 格式</span>
                <Button
                  type="text"
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => handleCopy(adaptedPrompt)}
                >
                  复制
                </Button>
              </div>
              <pre className={styles.promptText}>{adaptedPrompt}</pre>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

function DimItem({ dim }: { dim: DimensionUsed }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className={styles.dimItem} onClick={() => setExpanded(!expanded)}>
      <div className={styles.dimItemHeader}>
        <Tag color="blue" style={{ fontSize: 11, lineHeight: '18px' }}>{dim.id}</Tag>
        <span className={styles.dimItemName}>{dim.name}</span>
        <span className={styles.dimItemCat}>{dim.category_name}</span>
      </div>
      {expanded && dim.description && (
        <div className={styles.dimItemDesc}>{dim.description}</div>
      )}
    </div>
  )
}
