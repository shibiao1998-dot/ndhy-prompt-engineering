import { useState, useEffect, useCallback } from 'react'
import { getCategories, getDimensions, updateDimension, deleteDimension, triggerDimensionWorkflow } from '../services/api'
import type { Dimension, DimensionUpdate, Category } from '../types'
import styles from './Dimensions.module.css'

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

  // Workflow update state — allow up to 5 concurrent updates
  const [updatingIds, setUpdatingIds] = useState<Set<string>>(new Set())

  // Source explanation viewer state
  const [viewingSourceDim, setViewingSourceDim] = useState<Dimension | null>(null)

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
      quality_role: dim.quality_role || '',
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

  // ─── Workflow update handler (max 5 concurrent) ────────────
  const handleWorkflowUpdate = useCallback(async (dim: Dimension) => {
    if (updatingIds.has(dim.id)) return // already updating this one
    if (updatingIds.size >= 5) {
      alert(`最多同时更新 5 个维度（当前 ${updatingIds.size}/5），请等待其他更新完成后再试`)
      return
    }

    // Build dimension_input by concatenating 4 fields
    const parts = [
      `【维度名称】${dim.name}`,
      `【定义】${dim.description || '暂无'}`,
      `【质量作用】${dim.quality_role || '暂无'}`,
      `【数据来源】${dim.data_source || '暂无'}`,
    ]
    const dimensionInput = parts.join('\n')

    setUpdatingIds((prev) => new Set(prev).add(dim.id))
    try {
      const updated = await triggerDimensionWorkflow(dim.id, dimensionInput)
      setDimensions((prev) => prev.map((d) => (d.id === updated.id ? updated : d)))
    } catch (err) {
      console.error('Workflow update failed:', err)
      const msg = err instanceof Error ? err.message : '请重试'
      alert(`更新失败: ${msg}`)
    } finally {
      setUpdatingIds((prev) => {
        const next = new Set(prev)
        next.delete(dim.id)
        return next
      })
    }
  }, [updatingIds])

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
      <div className={styles.grid}>
        {loading ? (
          <div className={styles.loadingHint}>加载中...</div>
        ) : dimensions.length === 0 ? (
          <div className={styles.emptyHint}>该类别下暂无维度</div>
        ) : (
          dimensions.map((dim) => (
            <div key={dim.id} className={styles.card}>
              {/* Hover action buttons */}
              <div className={styles.cardActions}>
                {/* Update via workflow button */}
                <button
                  className={`${styles.updateBtn} ${updatingIds.has(dim.id) ? styles.updating : ''}`}
                  onClick={(e) => { e.stopPropagation(); handleWorkflowUpdate(dim) }}
                  title="通过 Workflow 更新"
                  disabled={updatingIds.has(dim.id)}
                >
                  {updatingIds.has(dim.id) ? (
                    <svg className={styles.spinIcon} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 12a9 9 0 11-6.219-8.56"/>
                    </svg>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="23 4 23 10 17 10"/>
                      <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/>
                    </svg>
                  )}
                </button>
                {/* View source explanation button — always visible */}
                <button
                  className={`${styles.viewSourceBtn} ${!dim.source_explanation ? styles.btnDisabledStyle : ''}`}
                  onClick={(e) => {
                    e.stopPropagation()
                    if (dim.source_explanation) {
                      setViewingSourceDim(dim)
                    } else {
                      alert('暂无原始数据，请先点击更新按钮通过 Workflow 获取')
                    }
                  }}
                  title={dim.source_explanation ? '查看原始数据' : '暂无原始数据'}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
                {/* Edit button */}
                <button className={styles.editBtn} onClick={(e) => { e.stopPropagation(); openEdit(dim) }} title="编辑">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                {/* Delete button */}
                <button className={styles.deleteBtn} onClick={(e) => { e.stopPropagation(); setDeletingId(dim.id) }} title="删除">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
              </div>

              {/* Updating overlay */}
              {updatingIds.has(dim.id) && (
                <div className={styles.cardUpdating}>
                  <div className={styles.updatingSpinner} />
                  <span>Workflow 更新中...</span>
                </div>
              )}

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
                {dim.quality_role && (
                  <div className={styles.cardField}>
                    <span className={styles.fieldLabel}>质量作用</span>
                    <p className={styles.fieldContent}>{dim.quality_role}</p>
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
          ))
        )}
      </div>

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
                质量作用
                <input
                  className={styles.formInput}
                  value={editForm.quality_role || ''}
                  onChange={(e) => setEditForm((p) => ({ ...p, quality_role: e.target.value }))}
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
              {/* Source explanation section */}
              <div className={styles.sourceExplanationSection}>
                <label className={styles.formLabel}>
                  <span className={styles.sourceExplanationLabel}>
                    数据来源原始数据
                    <span className={styles.sourceExplanationHint}>（Workflow 返回的详细来源说明，支持修改）</span>
                  </span>
                  <textarea
                    className={`${styles.formTextarea} ${styles.sourceExplanationTextarea}`}
                    rows={6}
                    value={editForm.source_explanation || ''}
                    placeholder="暂无原始数据，点击卡片上的更新按钮通过 Workflow 获取"
                    onChange={(e) => setEditForm((p) => ({ ...p, source_explanation: e.target.value }))}
                  />
                </label>
              </div>
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

      {/* ─── View Source Explanation Modal ─────────────────────── */}
      {viewingSourceDim && (
        <div className={styles.overlay} onClick={() => setViewingSourceDim(null)}>
          <div className={styles.sourceModal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2>
                <span className={styles.sourceModalId}>{viewingSourceDim.id}</span>
                {viewingSourceDim.name} — 数据来源原始数据
              </h2>
              <button className={styles.modalClose} onClick={() => setViewingSourceDim(null)}>✕</button>
            </div>
            <div className={styles.sourceModalBody}>
              {viewingSourceDim.source_explanation ? (
                <div className={styles.sourceContent}>
                  {viewingSourceDim.source_explanation}
                </div>
              ) : (
                <div className={styles.sourceEmpty}>
                  暂无原始数据，请先点击卡片上的更新按钮通过 Workflow 获取
                </div>
              )}
            </div>
            <div className={styles.modalFooter}>
              <button className={styles.cancelBtn} onClick={() => setViewingSourceDim(null)}>
                关闭
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
