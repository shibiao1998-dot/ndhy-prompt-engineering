import { useState, useEffect, useCallback } from 'react'
import { getCategories, getDimensions, updateDimension, deleteDimension } from '../services/api'
import type { Dimension, DimensionUpdate, Category } from '../types'
import styles from './Dimensions.module.css'

// M class level names
const M_LEVEL_NAMES: Record<number, string> = {
  1: 'Level 1: 生理需求',
  2: 'Level 2: 安全需求',
  3: 'Level 3: 社交需求',
  4: 'Level 4: 尊重需求',
  5: 'Level 5: 自我实现',
}

export default function Dimensions() {
  const [categories, setCategories] = useState<Category[]>([])
  const [activeCategory, setActiveCategory] = useState<string>('')
  const [dimensions, setDimensions] = useState<Dimension[]>([])
  const [loading, setLoading] = useState(true)

  // Edit modal state
  const [editingDim, setEditingDim] = useState<Dimension | null>(null)
  const [editForm, setEditForm] = useState<DimensionUpdate>({})
  const [saving, setSaving] = useState(false)

  // Delete confirm state
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  // Load categories on mount
  useEffect(() => {
    getCategories()
      .then((cats) => {
        setCategories(cats)
        if (cats.length > 0) setActiveCategory(cats[0].key)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  // Load dimensions when category changes
  useEffect(() => {
    if (!activeCategory) return
    setLoading(true)
    getDimensions(activeCategory)
      .then(setDimensions)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [activeCategory])

  // ─── Edit handlers ──────────────────────────────────────────
  const openEdit = useCallback((dim: Dimension) => {
    setEditingDim(dim)
    setEditForm({
      name: dim.name,
      description: dim.description || '',
      data_source: dim.data_source || '',
      update_frequency: dim.update_frequency || '',
      source_explanation: dim.source_explanation || '',
    })
  }, [])

  const handleSave = useCallback(async () => {
    if (!editingDim) return
    setSaving(true)
    try {
      const updated = await updateDimension(editingDim.id, editForm)
      setDimensions((prev) => prev.map((d) => (d.id === updated.id ? updated : d)))
      setEditingDim(null)
    } catch (err) {
      console.error('Save failed:', err)
      alert('保存失败，请重试')
    } finally {
      setSaving(false)
    }
  }, [editingDim, editForm])

  // ─── Delete handlers ────────────────────────────────────────
  const handleDelete = useCallback(async () => {
    if (!deletingId) return
    setDeleting(true)
    try {
      await deleteDimension(deletingId)
      setDimensions((prev) => prev.filter((d) => d.id !== deletingId))
      setCategories((prev) =>
        prev.map((c) =>
          c.key === activeCategory ? { ...c, count: c.count - 1 } : c
        )
      )
      setDeletingId(null)
    } catch (err) {
      console.error('Delete failed:', err)
      alert('删除失败，请重试')
    } finally {
      setDeleting(false)
    }
  }, [deletingId, activeCategory])

  // ─── Render dimension cards grouped by level (for M class) ────────────
  const renderDimensions = () => {
    if (loading) {
      return <div className={styles.loadingHint}>加载中...</div>
    }
    if (dimensions.length === 0) {
      return <div className={styles.emptyHint}>该类别下暂无维度</div>
    }

    // For M class, group by level
    if (activeCategory === 'M') {
      const groupedByLevel = dimensions.reduce((acc, dim) => {
        const level = dim.level || 1
        if (!acc[level]) acc[level] = []
        acc[level].push(dim)
        return acc
      }, {} as Record<number, Dimension[]>)

      return (
        <>
          {Object.keys(groupedByLevel).sort().map((levelKey) => {
            const level = parseInt(levelKey)
            const levelDims = groupedByLevel[level]
            return (
              <div key={level} className={styles.levelGroup}>
                <div className={styles.levelHeader}>
                  <h3 className={styles.levelTitle}>{M_LEVEL_NAMES[level]}</h3>
                  <div className={styles.levelDivider} />
                </div>
                <div className={styles.grid}>
                  {levelDims.map((dim) => (
                    <div key={dim.id} className={styles.card}>
                      {/* Action buttons */}
                      <div className={styles.cardActions}>
                        {/* Edit button */}
                        <button className={styles.editBtn} onClick={(e) => { e.stopPropagation(); openEdit(dim) }} title="编辑">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                        </button>
                        {/* Delete button */}
                        <button className={styles.deleteBtn} onClick={(e) => { e.stopPropagation(); setDeletingId(dim.id) }} title="删除">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                        </button>
                      </div>

                      {/* Card content */}
                      <div className={styles.cardHeader}>
                        <span className={styles.cardId}>{dim.id}</span>
                        <h3 className={styles.cardTitle}>{dim.name}</h3>
                      </div>

                      <div className={styles.cardBody}>
                        {dim.description && (
                          <div className={styles.cardField}>
                            <span className={styles.fieldLabel}>定义</span>
                            <p className={styles.fieldContent}>{truncate(dim.description, 200)}</p>
                          </div>
                        )}
                        {dim.data_source && (
                          <div className={styles.cardField}>
                            <span className={styles.fieldLabel}>数据来源</span>
                            <p className={styles.fieldContent}>{truncate(dim.data_source, 120)}</p>
                          </div>
                        )}
                        {dim.update_frequency && (
                          <div className={styles.cardField}>
                            <span className={styles.fieldLabel}>更新机制</span>
                            <p className={styles.fieldContent}>{dim.update_frequency}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </>
      )
    }

    // For other categories, render flat grid
    return (
      <div className={styles.grid}>
        {dimensions.map((dim) => (
          <div key={dim.id} className={styles.card}>
            {/* Action buttons */}
            <div className={styles.cardActions}>
              {/* Edit button */}
              <button className={styles.editBtn} onClick={(e) => { e.stopPropagation(); openEdit(dim) }} title="编辑">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
              {/* Delete button */}
              <button className={styles.deleteBtn} onClick={(e) => { e.stopPropagation(); setDeletingId(dim.id) }} title="删除">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
              </button>
            </div>

            {/* Card content */}
            <div className={styles.cardHeader}>
              <span className={styles.cardId}>{dim.id}</span>
              <h3 className={styles.cardTitle}>{dim.name}</h3>
            </div>

            <div className={styles.cardBody}>
              {dim.description && (
                <div className={styles.cardField}>
                  <span className={styles.fieldLabel}>定义</span>
                  <p className={styles.fieldContent}>{truncate(dim.description, 200)}</p>
                </div>
              )}
              {dim.data_source && (
                <div className={styles.cardField}>
                  <span className={styles.fieldLabel}>数据来源</span>
                  <p className={styles.fieldContent}>{truncate(dim.data_source, 120)}</p>
                </div>
              )}
              {dim.update_frequency && (
                <div className={styles.cardField}>
                  <span className={styles.fieldLabel}>更新机制</span>
                  <p className={styles.fieldContent}>{dim.update_frequency}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  // ─── Render ─────────────────────────────────────────────────
  return (
    <div className={styles.container}>
      {/* Page header */}
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>维度管理</h1>
        <p className={styles.pageSubtitle}>
          管理 {categories.reduce((s, c) => s + c.count, 0)} 个维度，覆盖 {categories.length} 个大类
        </p>
      </div>

      {/* Category tabs */}
      <div className={styles.tabBar}>
        {categories.map((cat) => (
          <button
            key={cat.key}
            className={`${styles.tab} ${activeCategory === cat.key ? styles.tabActive : ''}`}
            onClick={() => setActiveCategory(cat.key)}
          >
            <span className={styles.tabKey}>{cat.key}</span>
            <span className={styles.tabName}>{cat.name}</span>
            <span className={styles.tabCount}>{cat.count}</span>
          </button>
        ))}
      </div>

      {/* Dimension cards grid */}
      {renderDimensions()}

      {/* ─── Edit Modal ──────────────────────────────────────── */}
      {editingDim && (
        <div className={styles.overlay} onClick={() => !saving && setEditingDim(null)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>编辑维度 {editingDim.id}</h2>
              <button className={styles.modalClose} onClick={() => setEditingDim(null)}>✕</button>
            </div>
            <div className={styles.modalBody}>
              <label className={styles.formLabel}>
                维度名称
                <input
                  className={styles.formInput}
                  value={editForm.name || ''}
                  onChange={(e) => setEditForm((p) => ({ ...p, name: e.target.value }))}
                />
              </label>
              <label className={styles.formLabel}>
                定义
                <textarea
                  className={styles.formTextarea}
                  rows={6}
                  value={editForm.description || ''}
                  onChange={(e) => setEditForm((p) => ({ ...p, description: e.target.value }))}
                />
              </label>
              <label className={styles.formLabel}>
                数据来源
                <textarea
                  className={styles.formTextarea}
                  rows={3}
                  value={editForm.data_source || ''}
                  onChange={(e) => setEditForm((p) => ({ ...p, data_source: e.target.value }))}
                />
              </label>
              <label className={styles.formLabel}>
                更新机制
                <input
                  className={styles.formInput}
                  value={editForm.update_frequency || ''}
                  onChange={(e) => setEditForm((p) => ({ ...p, update_frequency: e.target.value }))}
                />
              </label>
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setEditingDim(null)} disabled={saving}>
                取消
              </button>
              <button className={styles.saveBtn} onClick={handleSave} disabled={saving}>
                {saving ? '保存中...' : '保存'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─── Delete Confirm Modal ────────────────────────────── */}
      {deletingId && (
        <div className={styles.overlay} onClick={() => !deleting && setDeletingId(null)}>
          <div className={styles.confirmModal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.confirmIcon}>⚠️</div>
            <h3 className={styles.confirmTitle}>确认删除</h3>
            <p className={styles.confirmText}>
              确定要删除维度 <strong>{deletingId}</strong> 吗？此操作不可撤销。
            </p>
            <div className={styles.confirmActions}>
              <button className={styles.cancelBtn} onClick={() => setDeletingId(null)} disabled={deleting}>
                取消
              </button>
              <button className={styles.dangerBtn} onClick={handleDelete} disabled={deleting}>
                {deleting ? '删除中...' : '确认删除'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function truncate(text: string, max: number): string {
  if (text.length <= max) return text
  return text.slice(0, max) + '...'
}
