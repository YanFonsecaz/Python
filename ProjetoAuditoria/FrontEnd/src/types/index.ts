// Tipos para auditoria
export interface Audit {
  id: string;
  url: string;
  status: AuditStatus;
  progress: number;
  created_at: string;
  completed_at?: string;
  audit_type: AuditType;
  generate_documentation: boolean;
  include_screenshots: boolean;
  current_step?: string;
  error_message?: string;
}

export type AuditStatus = 
  | 'pending' 
  | 'starting' 
  | 'running'
  | 'in_progress' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

export type AuditType = 'complete' | 'basic' | 'technical';

// Tipos para resultados da auditoria
export interface AuditResult {
  audit_id: string;
  url: string;
  timestamp: string;
  seo_analysis: SEOAnalysis;
  technical_analysis: TechnicalAnalysis;
  performance_metrics: PerformanceMetrics;
  performance_analysis?: any;
  mobile_analysis?: any;
  security_analysis?: any;
  accessibility_analysis?: any;
  recommendations: Recommendation[];
  score: number;
  overall_score?: number;
  screenshots?: boolean;
  generated_docs?: boolean;
}

export interface SEOAnalysis {
  title: {
    content: string;
    length: number;
    is_optimized: boolean;
  };
  meta_description: {
    content: string;
    length: number;
    is_optimized: boolean;
  };
  headings: {
    h1_count: number;
    h2_count: number;
    h3_count: number;
    structure_score: number;
  };
  images: {
    total_images: number;
    images_without_alt: number;
    optimization_score: number;
  };
  links: {
    internal_links: number;
    external_links: number;
    broken_links: number;
  };
}

export interface TechnicalAnalysis {
  page_speed: {
    load_time: number;
    score: number;
  };
  mobile_friendly: {
    is_mobile_friendly: boolean;
    score: number;
  };
  ssl_certificate: {
    is_valid: boolean;
    expires_at?: string;
  };
  robots_txt: {
    exists: boolean;
    is_valid: boolean;
  };
  sitemap: {
    exists: boolean;
    url?: string;
  };
}

export interface PerformanceMetrics {
  first_contentful_paint: number;
  largest_contentful_paint: number;
  cumulative_layout_shift: number;
  first_input_delay: number;
  total_blocking_time: number;
}

export interface Recommendation {
  id: string;
  category: 'seo' | 'technical' | 'performance' | 'accessibility';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;
  effort: string;
}

// Tipos para API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface StartAuditRequest {
  url: string;
  audit_type: AuditType;
  generate_documentation: boolean;
  include_screenshots: boolean;
}

export interface StartAuditResponse {
  audit_id: string;
  message: string;
}

// Tipos para notificações
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'progress';
  title: string;
  message: string;
  duration?: number;
  timestamp: number;
  read?: boolean;
  auditId?: string;
  progress?: number;
  autoClose?: boolean;
}

// Tipos para tema
export type Theme = 'light' | 'dark';

// Tipos para dashboard
export interface DashboardStats {
  total_audits: number;
  completed_audits: number;
  running_audits: number;
  failed_audits: number;
  audits_today: number;
  critical_issues: number;
  average_score: number;
  recent_audits: Audit[];
}

// Tipos para filtros
export interface AuditFilters {
  status?: AuditStatus;
  audit_type?: AuditType;
  date_from?: string;
  date_to?: string;
  url_contains?: string;
}

// Tipos para paginação
export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}