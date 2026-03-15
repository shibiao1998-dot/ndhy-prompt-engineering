import { useEffect, useState } from 'react'
import { Spin, Tag } from 'antd'
import { DatabaseOutlined } from '@ant-design/icons'
import { getDimensionStats } from '../services/api'
import type { DimensionStats } from '../types'
import styles from './DimensionOverview.module.css'

const CATEGORY_COLORS: Record<string, string> = {
  A: '#1B65A9', B: '#0891B2', C: '#7C3AED', D: '#C2410C',
  E: '#059669', F: '#D97706', G: '#DC2626', H: '#4F46E5',
  I: '#0D9488', J: '#9333EA', K: '#EA580C', L: '#2563EB',
}

export default function DimensionOverview() {
  const [stats, setStats] = useState<DimensionStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDimensionStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className={styles.wrapper}>
        <Spin size="large" />
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <DatabaseOutlined className={styles.icon} />
        <div>
          <h2 className={styles.title}>知识维度库概览</h2>
          <p className={styles.subtitle}>
            <span className={styles.statNum}>{stats.total_dimensions}</span> 个维度 · 
            <span className={styles.statNum}> {stats.total_categories}</span> 个类别 · 
            <span className={styles.statNum}> {(stats.overall_fill_rate * 100).toFixed(0)}%</span> 已填充
          </p>
        </div>
      </div>
      <div className={styles.categories}>
        {stats.by_category.map((cat) => (
          <div key={cat.category} className={styles.catCard}>
            <div className={styles.catHeader}>
              <Tag
                color={CATEGORY_COLORS[cat.category] || '#666'}
                style={{ marginRight: 8, fontSize: 12, lineHeight: '22px' }}
              >
                {cat.category}
              </Tag>
              <span className={styles.catName}>{cat.category_name}</span>
            </div>
            <div className={styles.catBar}>
              <div
                className={styles.catBarFill}
                style={{
                  width: `${cat.fill_rate * 100}%`,
                  backgroundColor: CATEGORY_COLORS[cat.category] || '#666',
                }}
              />
            </div>
            <div className={styles.catStat}>
              {cat.filled}/{cat.total}
              <span className={styles.catRate}> {(cat.fill_rate * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
