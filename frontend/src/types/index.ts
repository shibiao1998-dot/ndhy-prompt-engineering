// Dimension types
export interface Dimension {
  id: string
  name: string
  category: string
  category_name: string
  description: string | null
  pending_description: string | null
  data_source: string | null
  update_frequency: string | null
  direction: 'positive' | 'negative' | 'mixed'
  priority: number
  last_updated_at: string | null
  review_status: 'approved' | 'pending' | 'rejected'
  reviewer: string | null
  reviewed_at: string | null
  created_at: string
}

// Stats types
export interface CategoryStat {
  category: string
  category_name: string
  total: number
  filled: number
  fill_rate: number
}

export interface DimensionStats {
  total_dimensions: number
  total_categories: number
  filled_dimensions: number
  unfilled_dimensions: number
  overall_fill_rate: number
  by_category: CategoryStat[]
}

// Conversation types
export interface Conversation {
  id: string
  title: string | null
  task_type: string | null
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  dimensions_used: string | null
  prompt_snapshot: string | null
  coverage_stats: string | null
  created_at: string
}

// SSE event types
export interface SSEMetadata {
  conversation_id: string
  dimensions_used: DimensionUsed[]
  coverage_stats: CoverageStats
  prompt_snapshot: string
}

export interface DimensionUsed {
  id: string
  name: string
  category: string
  category_name: string
  priority: number
  direction: string
  description?: string
}

export interface CoverageStats {
  total: number
  covered: number
  coverage_rate: number
  by_priority: {
    required: { covered: number; total: number }
    recommended: { covered: number; total: number }
    optional: { covered: number; total: number }
  }
  truncated: number
}

// Engine types
export interface Engine {
  id: string
  name: string
  type: string
  format: string
  max_chars: number
  is_active: boolean
  description: string
}

// Chat message for UI
export interface ChatMessage {
  id: string | number
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
  metadata?: SSEMetadata
}

// Review types
export interface ReviewPayload {
  action: 'approve' | 'reject'
  reviewer: string
  comment?: string
}
