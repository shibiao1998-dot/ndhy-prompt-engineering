import { useState, useEffect, useCallback } from 'react'
import {
  Card, Tag, Button, Collapse, Drawer, Form, Input, Select,
  Modal, Progress, Spin, message, Space, Badge,
} from 'antd'
import {
  PlusOutlined, EditOutlined, CheckCircleOutlined,
  DeleteOutlined, ExclamationCircleOutlined,
} from '@ant-design/icons'
import type { Dimension, DimensionStats, ReviewPayload } from '../types'
import {
  getDimensions, getDimensionStats, updateDimension,
  createDimension, deleteDimension, reviewDimension,
} from '../services/api'
import styles from './DimensionManager.module.css'

const CATEGORY_COLORS: Record<string, string> = {
  A: '#1B65A9', B: '#0891B2', C: '#7C3AED', D: '#C2410C',
  E: '#059669', F: '#D97706', G: '#DC2626', H: '#4F46E5',
  I: '#0D9488', J: '#9333EA', K: '#EA580C', L: '#2563EB',
}

const DIRECTION_MAP = {
  positive: { label: '正向', color: '#059669', emoji: '🟢' },
  negative: { label: '反向', color: '#DC2626', emoji: '🔴' },
  mixed: { label: '混合', color: '#2563EB', emoji: '🔵' },
}

const STATUS_MAP = {
  approved: { label: '已审核', emoji: '✅' },
  pending: { label: '待审核', emoji: '🟡' },
  rejected: { label: '已驳回', emoji: '❌' },
}

export default function DimensionManager() {
  const [dimensions, setDimensions] = useState<Dimension[]>([])
  const [stats, setStats] = useState<DimensionStats | null>(null)
  const [loading, setLoading] = useState(true)

  // Edit drawer
  const [editDrawerOpen, setEditDrawerOpen] = useState(false)
  const [editingDim, setEditingDim] = useState<Dimension | null>(null)
  const [editForm] = Form.useForm()

  // Review modal
  const [reviewModalOpen, setReviewModalOpen] = useState(false)
  const [reviewingDim, setReviewingDim] = useState<Dimension | null>(null)
  const [reviewComment, setReviewComment] = useState('')

  // Add modal
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [addForm] = Form.useForm()

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [dims, st] = await Promise.all([getDimensions(), getDimensionStats()])
      setDimensions(dims)
      setStats(st)
    } catch (err) {
      console.error(err)
      message.error('加载维度数据失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  // Group dimensions by category
  const groupedDimensions = dimensions.reduce<Record<string, Dimension[]>>((acc, dim) => {
    if (!acc[dim.category]) acc[dim.category] = []
    acc[dim.category].push(dim)
    return acc
  }, {})

  // Edit
  const openEdit = (dim: Dimension) => {
    setEditingDim(dim)
    editForm.setFieldsValue({
      description: dim.description || '',
      direction: dim.direction,
    })
    setEditDrawerOpen(true)
  }

  const handleEditSubmit = async () => {
    if (!editingDim) return
    try {
      const values = await editForm.validateFields()
      await updateDimension(editingDim.id, values)
      message.success('已提交，进入待审核状态')
      setEditDrawerOpen(false)
      loadData()
    } catch (err) {
      console.error(err)
    }
  }

  // Review
  const openReview = (dim: Dimension) => {
    setReviewingDim(dim)
    setReviewComment('')
    setReviewModalOpen(true)
  }

  const handleReview = async (action: 'approve' | 'reject') => {
    if (!reviewingDim) return
    try {
      const payload: ReviewPayload = { action, reviewer: '管理员', comment: reviewComment }
      await reviewDimension(reviewingDim.id, payload)
      message.success(action === 'approve' ? '审核通过' : '已驳回')
      setReviewModalOpen(false)
      loadData()
    } catch (err) {
      console.error(err)
      message.error('审核操作失败')
    }
  }

  // Add
  const handleAdd = async () => {
    try {
      const values = await addForm.validateFields()
      await createDimension(values)
      message.success('维度创建成功')
      setAddModalOpen(false)
      addForm.resetFields()
      loadData()
    } catch (err) {
      console.error(err)
    }
  }

  // Delete
  const handleDelete = (dim: Dimension) => {
    Modal.confirm({
      title: `确认删除维度 ${dim.id}？`,
      icon: <ExclamationCircleOutlined />,
      content: `将删除维度"${dim.name}"，此操作不可撤销。`,
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteDimension(dim.id)
          message.success('维度已删除')
          loadData()
        } catch (err) {
          console.error(err)
          message.error('删除失败')
        }
      },
    })
  }

  if (loading) {
    return <div className={styles.loading}><Spin size="large" /></div>
  }

  return (
    <div className={styles.page}>
      {/* Dashboard */}
      {stats && (
        <div className={styles.dashboard}>
          <div className={styles.dashboardHeader}>
            <h2 className={styles.dashboardTitle}>📊 维度知识库全景</h2>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddModalOpen(true)}>
              新增维度
            </Button>
          </div>

          <div className={styles.statsRow}>
            <div className={styles.statCard}>
              <div className={styles.statNum}>{stats.total_dimensions}</div>
              <div className={styles.statLabel}>总维度数</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statNum}>{stats.filled_dimensions}</div>
              <div className={styles.statLabel}>已填充</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statNum}>{stats.unfilled_dimensions}</div>
              <div className={styles.statLabel}>待填充</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statNum} style={{ color: '#1B65A9' }}>
                {(stats.overall_fill_rate * 100).toFixed(1)}%
              </div>
              <div className={styles.statLabel}>填充率</div>
            </div>
          </div>

          <div className={styles.categoryGrid}>
            {stats.by_category.map((cat) => (
              <div key={cat.category} className={styles.categoryBar}>
                <div className={styles.categoryInfo}>
                  <Tag color={CATEGORY_COLORS[cat.category]}>{cat.category}</Tag>
                  <span className={styles.categoryName}>{cat.category_name}</span>
                  <span className={styles.categoryCount}>{cat.filled}/{cat.total}</span>
                </div>
                <Progress
                  percent={Math.round(cat.fill_rate * 100)}
                  strokeColor={CATEGORY_COLORS[cat.category]}
                  size="small"
                  format={(p) => `${p}%`}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dimension list */}
      <div className={styles.dimensionList}>
        <Collapse
          defaultActiveKey={Object.keys(groupedDimensions)}
          items={Object.entries(groupedDimensions)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([category, dims]) => ({
              key: category,
              label: (
                <div className={styles.collapseLabel}>
                  <Tag color={CATEGORY_COLORS[category]}>{category}</Tag>
                  <span className={styles.collapseLabelText}>
                    {dims[0]?.category_name}
                  </span>
                  <Badge
                    count={dims.filter((d) => d.review_status === 'pending').length}
                    style={{ marginLeft: 8 }}
                  />
                  <span className={styles.collapseLabelCount}>{dims.length} 个维度</span>
                </div>
              ),
              children: (
                <div className={styles.dimCards}>
                  {dims.map((dim) => (
                    <DimensionCard
                      key={dim.id}
                      dim={dim}
                      onEdit={openEdit}
                      onReview={openReview}
                      onDelete={handleDelete}
                    />
                  ))}
                </div>
              ),
            }))}
        />
      </div>

      {/* Edit Drawer */}
      <Drawer
        title={editingDim ? `编辑维度 ${editingDim.id} · ${editingDim.name}` : '编辑维度'}
        open={editDrawerOpen}
        onClose={() => setEditDrawerOpen(false)}
        width={480}
        extra={
          <Button type="primary" onClick={handleEditSubmit}>
            提交审核
          </Button>
        }
      >
        <Form form={editForm} layout="vertical">
          <Form.Item label="维度描述" name="description" rules={[{ required: true, message: '请输入维度描述' }]}>
            <Input.TextArea rows={8} placeholder="请输入维度描述内容…" />
          </Form.Item>
          <Form.Item label="信息方向" name="direction">
            <Select
              options={[
                { value: 'positive', label: '🟢 正向（要什么）' },
                { value: 'negative', label: '🔴 反向（不要什么）' },
                { value: 'mixed', label: '🔵 混合' },
              ]}
            />
          </Form.Item>
        </Form>
        {editingDim && (
          <div className={styles.editMeta}>
            <p><strong>类别：</strong>{editingDim.category} · {editingDim.category_name}</p>
            <p><strong>数据来源：</strong>{editingDim.data_source || '未填写'}</p>
            <p><strong>更新频率：</strong>{editingDim.update_frequency || '未设置'}</p>
          </div>
        )}
      </Drawer>

      {/* Review Modal */}
      <Modal
        title={reviewingDim ? `审核维度 ${reviewingDim.id} · ${reviewingDim.name}` : '审核维度'}
        open={reviewModalOpen}
        onCancel={() => setReviewModalOpen(false)}
        footer={
          <Space>
            <Button onClick={() => setReviewModalOpen(false)}>取消</Button>
            <Button danger onClick={() => handleReview('reject')}>驳回</Button>
            <Button type="primary" onClick={() => handleReview('approve')}>通过</Button>
          </Space>
        }
        width={600}
      >
        {reviewingDim && (
          <div className={styles.reviewContent}>
            <div className={styles.reviewSection}>
              <h4>当前描述</h4>
              <div className={styles.reviewText}>{reviewingDim.description || '（无）'}</div>
            </div>
            <div className={styles.reviewSection}>
              <h4>待审核描述</h4>
              <div className={`${styles.reviewText} ${styles.reviewTextNew}`}>
                {reviewingDim.pending_description || '（无变更）'}
              </div>
            </div>
            <Input.TextArea
              placeholder="审核意见（可选）"
              value={reviewComment}
              onChange={(e) => setReviewComment(e.target.value)}
              rows={3}
              style={{ marginTop: 16 }}
            />
          </div>
        )}
      </Modal>

      {/* Add Modal */}
      <Modal
        title="新增维度"
        open={addModalOpen}
        onCancel={() => { setAddModalOpen(false); addForm.resetFields() }}
        onOk={handleAdd}
        okText="创建"
        width={520}
      >
        <Form form={addForm} layout="vertical">
          <Form.Item label="维度 ID" name="id" rules={[{ required: true, message: '请输入维度 ID（如 A01）' }]}>
            <Input placeholder="如 A01, B03…" />
          </Form.Item>
          <Form.Item label="名称" name="name" rules={[{ required: true, message: '请输入维度名称' }]}>
            <Input placeholder="维度名称" />
          </Form.Item>
          <Form.Item label="类别" name="category" rules={[{ required: true, message: '请选择类别' }]}>
            <Select
              placeholder="选择所属类别"
              options={stats?.by_category.map((c) => ({ value: c.category, label: `${c.category} · ${c.category_name}` })) || []}
            />
          </Form.Item>
          <Form.Item label="描述" name="description" rules={[{ required: true, message: '请输入描述' }]}>
            <Input.TextArea rows={4} placeholder="维度描述内容…" />
          </Form.Item>
          <Form.Item label="数据来源" name="data_source">
            <Input placeholder="来自哪个会议/文档/调研" />
          </Form.Item>
          <Form.Item label="信息方向" name="direction" initialValue="positive">
            <Select
              options={[
                { value: 'positive', label: '🟢 正向（要什么）' },
                { value: 'negative', label: '🔴 反向（不要什么）' },
                { value: 'mixed', label: '🔵 混合' },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

// Sub-component: DimensionCard
function DimensionCard({
  dim,
  onEdit,
  onReview,
  onDelete,
}: {
  dim: Dimension
  onEdit: (d: Dimension) => void
  onReview: (d: Dimension) => void
  onDelete: (d: Dimension) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const dir = DIRECTION_MAP[dim.direction] || DIRECTION_MAP.positive
  const status = STATUS_MAP[dim.review_status] || STATUS_MAP.approved

  return (
    <Card
      size="small"
      className={`${styles.dimCard} ${dim.review_status === 'pending' ? styles.dimCardPending : ''}`}
      hoverable
      onClick={() => setExpanded(!expanded)}
    >
      <div className={styles.dimCardHeader}>
        <Tag color="#1B65A9" style={{ fontSize: 11 }}>{dim.id}</Tag>
        <span className={styles.dimCardName}>{dim.name}</span>
        <span className={styles.dimCardStatus}>{status.emoji}</span>
        <span className={styles.dimCardDir}>{dir.emoji}</span>
      </div>

      {expanded && (
        <div className={styles.dimCardDetail} onClick={(e) => e.stopPropagation()}>
          <p className={styles.dimCardDesc}>{dim.description || '暂无描述'}</p>
          <div className={styles.dimCardMeta}>
            <span>数据来源：{dim.data_source || '未填写'}</span>
            <span>更新频率：{dim.update_frequency || '未设置'}</span>
            {dim.last_updated_at && <span>最后更新：{new Date(dim.last_updated_at).toLocaleDateString()}</span>}
          </div>
          <div className={styles.dimCardActions}>
            <Button size="small" icon={<EditOutlined />} onClick={() => onEdit(dim)}>编辑</Button>
            {dim.review_status === 'pending' && (
              <Button size="small" type="primary" icon={<CheckCircleOutlined />} onClick={() => onReview(dim)}>审核</Button>
            )}
            <Button size="small" danger icon={<DeleteOutlined />} onClick={() => onDelete(dim)}>删除</Button>
          </div>
        </div>
      )}
    </Card>
  )
}
