// API Response Types
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

// User Types
export interface User {
  id: string
  email: string
  role: 'user' | 'admin'
  status: 'active' | 'inactive'
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
  remember_me?: boolean
}

export interface RegisterRequest {
  email: string
  password: string
  confirm_password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// Chat Types
export type SessionMode = 'laws_public' | 'laws_internal'
export type SessionStatus = 'active' | 'closed'
export type MessageSender = 'user' | 'assistant' | 'system'

export interface Session {
  id: string
  mode: SessionMode
  status: SessionStatus
  title?: string
  message_count: number
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  session_id: string
  sender: MessageSender
  content: string
  tokens: number
  metadata: Record<string, any>
  created_at: string
}

export interface ChatHistoryResponse {
  session: Session
  messages: Message[]
  total_messages: number
}

export interface SessionsListResponse {
  sessions: Session[]
  total_sessions: number
  active_sessions: number
}

export interface StreamingMessage {
  type: 'token' | 'complete' | 'error'
  content?: string
  message_id?: string
  metadata?: Record<string, any>
}

// Admin Types
export interface AdminStats {
  total_users: number
  active_users: number
  total_sessions: number
  active_sessions: number
  total_messages: number
  messages_today: number
  seven_day_activity: Array<{
    date: string
    users: number
    messages: number
  }>
  storage_stats: Record<string, any>
}

export interface AdminLog {
  id: string
  admin_email: string
  action: string
  params: Record<string, any>
  result: Record<string, any>
  success: boolean
  execution_time?: number
  created_at: string
}

export interface CrawlLawsRequest {
  law_types: string[]
  force_update?: boolean
}

export interface UploadLawsRequest {
  file_name: string
  file_type: string
  description?: string
  category?: string
}

export interface AdminAgentCommand {
  command: string
  context?: Record<string, any>
}

export interface AdminAgentResponse {
  response: string
  action_taken?: string
  data?: Record<string, any>
  success: boolean
}

// UI State Types
export interface UIState {
  isLoading: boolean
  error: string | null
  theme: 'light' | 'dark'
  sidebarOpen: boolean
}

// Form Types
export interface FormFieldError {
  message: string
}

export interface FormErrors {
  [key: string]: FormFieldError
}
