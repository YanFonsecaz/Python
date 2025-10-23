import axios from 'axios';
import type { Audit, AuditResult, AuditStatus, AuditType } from '../types';

// Configuração da API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para logging de requisições (temporariamente desabilitado para debug)
// api.interceptors.request.use(
//   (config) => {
//     console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
//     return config;
//   },
//   (error) => {
//     console.error('API Request Error:', error);
//     return Promise.reject(error);
//   }
// );

// Interceptor para tratamento de respostas
api.interceptors.response.use(
  (response) => {
    // console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export interface StartAuditRequest {
  url: string;
  audit_type?: AuditType;
  generate_documentation?: boolean;
  include_screenshots?: boolean;
}

export interface AuditStatusResponse {
  audit_id: string;
  status: AuditStatus;
  progress: number;
  current_step: string;
  start_time: string;
  estimated_completion?: string;
  error?: string;
}

export interface AuditListResponse {
  audits: Audit[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface StatsResponse {
  total_audits: number;
  completed_audits: number;
  failed_audits: number;
  average_score: number;
  recent_audits: Audit[];
}

export interface AdminMetricsResponse {
  system: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    uptime: number;
  };
  application: {
    active_audits: number;
    queue_size: number;
    cache_size: number;
    total_requests: number;
  };
  performance: {
    avg_response_time: number;
    requests_per_minute: number;
    error_rate: number;
  };
}

export interface AdminHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  checks: {
    database: boolean;
    cache: boolean;
    processor: boolean;
    storage: boolean;
  };
  details?: {
    [key: string]: any;
  };
}

export interface AdminPerformanceResponse {
  response_times: {
    avg: number;
    min: number;
    max: number;
    p95: number;
    p99: number;
  };
  throughput: {
    requests_per_second: number;
    requests_per_minute: number;
  };
  errors: {
    total: number;
    rate: number;
    by_type: { [key: string]: number };
  };
}

export interface AdminProcessorResponse {
  status: 'running' | 'stopped' | 'error';
  queue_size: number;
  active_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  uptime: number;
}

export interface AdminSystemResponse {
  version: string;
  environment: string;
  uptime: number;
  memory: {
    total: number;
    used: number;
    available: number;
  };
  cpu: {
    usage: number;
    cores: number;
  };
  disk: {
    total: number;
    used: number;
    available: number;
  };
}

// Interfaces para monitoramento detalhado
export interface MonitoringMetricsResponse {
  timestamp: string;
  system_metrics: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_io: {
      bytes_sent: number;
      bytes_received: number;
    };
    load_average: number[];
  };
  application_metrics: {
    active_connections: number;
    request_queue_size: number;
    cache_hit_rate: number;
    database_connections: number;
    response_time_avg: number;
    error_rate: number;
  };
  audit_metrics: {
    audits_in_progress: number;
    audits_completed_today: number;
    audits_failed_today: number;
    average_audit_duration: number;
    queue_length: number;
  };
}

export interface MonitoringAlertsResponse {
  alerts: Array<{
    id: string;
    type: 'warning' | 'error' | 'info';
    message: string;
    timestamp: string;
    resolved: boolean;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }>;
  total_active: number;
  total_resolved: number;
}

export interface MonitoringLogsResponse {
  logs: Array<{
    timestamp: string;
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
    message: string;
    module: string;
    audit_id?: string;
  }>;
  total: number;
  page: number;
  limit: number;
}

export interface MonitoringHistoricalResponse {
  timeframe: string;
  data_points: Array<{
    timestamp: string;
    cpu_usage: number;
    memory_usage: number;
    active_audits: number;
    response_time: number;
    error_count: number;
  }>;
}

export class ApiService {
  
  /**
   * Inicia uma nova auditoria
   */
  static async startAudit(data: StartAuditRequest): Promise<{ audit_id: string }> {
    const response = await api.post('/audit/start', data);
    return response.data;
  }

  /**
   * Inicia uma nova auditoria com upload de arquivo CSV do Screaming Frog
   */
  static async startAuditWithFile(
    file: File, 
    options: Omit<StartAuditRequest, 'url'>
  ): Promise<{ audit_id: string }> {
    const formData = new FormData();
    formData.append('screaming_frog_file', file);
    
    // Adiciona as opções como campos do formulário
    if (options.audit_type) {
      formData.append('audit_type', options.audit_type);
    }
    if (options.generate_documentation !== undefined) {
      formData.append('generate_documentation', options.generate_documentation.toString());
    }
    if (options.include_screenshots !== undefined) {
      formData.append('include_screenshots', options.include_screenshots.toString());
    }

    const response = await api.post('/audit/start', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
  
  /**
   * Obtém o status de uma auditoria
   */
  static async getAuditStatus(auditId: string): Promise<AuditStatusResponse> {
    const response = await api.get(`/audit/status/${auditId}`);
    return response.data;
  }
  
  /**
   * Obtém o resultado de uma auditoria
   */
  static async getAuditResult(auditId: string): Promise<AuditResult> {
    const response = await api.get(`/audit/result/${auditId}`);
    return response.data;
  }
  
  /**
   * Lista auditorias com filtros e paginação
   */
  static async listAudits(page = 1, limit = 10, status?: AuditStatus, type?: AuditType): Promise<AuditListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    
    if (status) params.append('status', status);
    if (type) params.append('type', type);
    
    const response = await api.get(`/audit/list?${params}`);
    return response.data;
  }
  
  /**
   * Obtém estatísticas gerais
   */
  static async getStats(): Promise<StatsResponse> {
    try {
      const response = await api.get('/audit/stats');
      return response.data;
    } catch (error) {
      console.error('Erro ao obter estatísticas:', error);
      // Retorna dados mock em caso de erro
      return {
        total_audits: 0,
        completed_audits: 0,
        failed_audits: 0,
        average_score: 0,
        recent_audits: []
      };
    }
  }
  
  /**
   * Obtém relatório consolidado de múltiplas auditorias
   */
  static async getConsolidatedReport(params?: {
    start_date?: string;
    end_date?: string;
    status?: AuditStatus;
    audit_type?: AuditType;
    limit?: number;
    offset?: number;
  }): Promise<any> {
    try {
      const queryParams = new URLSearchParams();
      
      if (params?.start_date) queryParams.append('start_date', params.start_date);
      if (params?.end_date) queryParams.append('end_date', params.end_date);
      if (params?.status) queryParams.append('status', params.status);
      if (params?.audit_type) queryParams.append('audit_type', params.audit_type);
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      
      const url = `/audit/reports/consolidated${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Erro ao obter relatório consolidado:', error);
      throw error;
    }
  }
  
  /**
   * Faz download do relatório de uma auditoria
   */
  static async downloadReport(auditId: string, format: 'json' | 'docx' | 'pdf' = 'json'): Promise<Blob> {
    let endpoint: string;
    
    switch (format) {
      case 'docx':
        endpoint = `/audit/export/${auditId}`;
        break;
      case 'pdf':
        endpoint = `/audit/report/${auditId}`;
        break;
      default:
        endpoint = `/audit/result/${auditId}`;
        break;
    }
    
    const response = await api.get(endpoint, {
      responseType: format === 'json' ? 'json' : 'blob',
    });

    return format === 'json' ? new Blob([JSON.stringify(response.data)], { type: 'application/json' }) : response.data;
  }
  
  /**
   * Cancela uma auditoria
   */
  static async cancelAudit(auditId: string): Promise<{ audit_id: string; status: string; message: string }> {
    const response = await api.post(`/audit/cancel/${auditId}`);
    return response.data;
  }
  
  /**
   * Deleta uma auditoria
   */
  static async deleteAudit(auditId: string): Promise<{ message: string }> {
    // Assumindo que existe um endpoint de delete (pode não existir na API atual)
    try {
      const response = await api.delete(`/audit/${auditId}`);
      return response.data;
    } catch (error) {
      throw new Error('Funcionalidade de exclusão não disponível');
    }
  }
  
  /**
   * Obtém a documentação de uma auditoria
   */
  static async getAuditDocumentation(auditId: string): Promise<any> {
    const response = await api.get(`/audit/documentation/${auditId}`);
    return response.data;
  }

  /**
   * Faz download da documentação de uma auditoria
   */
  static async downloadAuditDocumentation(auditId: string, format: 'docx' | 'pdf' = 'docx'): Promise<Blob> {
    const response = await api.get(`/audit/documentation/${auditId}/download`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Obtém estatísticas do cache do sistema
   */
  static async getCacheStats(): Promise<any> {
    const response = await api.get('/admin/cache/stats');
    return response.data;
  }

  /**
   * Limpa o cache do sistema
   */
  static async clearCache(): Promise<{ message: string }> {
    const response = await api.delete('/admin/cache/clear');
    return response.data;
  }

  /**
   * Reseta as métricas de performance do sistema
   */
  static async resetPerformanceMetrics(): Promise<{ message: string }> {
    try {
      const response = await api.post('/admin/performance/reset');
      return response.data;
    } catch (error) {
      console.error('Erro ao resetar métricas de performance:', error);
      throw error;
    }
  }

  /**
   * Inicia o processador de auditorias
   */
  static async startAuditProcessor(): Promise<{ message: string }> {
    try {
      const response = await api.post('/admin/processor/start');
      return response.data;
    } catch (error) {
      console.error('Erro ao iniciar processador de auditorias:', error);
      throw error;
    }
  }

  /**
   * Obtém o relatório específico de uma auditoria
   */
  static async getAuditReport(auditId: string): Promise<any> {
    try {
      const response = await api.get(`/audit/report/${auditId}`);
      return response.data;
    } catch (error) {
      console.error(`Erro ao obter relatório da auditoria ${auditId}:`, error);
      throw error;
    }
  }

  /**
   * Exporta uma auditoria em formato específico
   */
  static async exportAudit(auditId: string, format: 'json' | 'docx' | 'pdf' = 'json'): Promise<Blob> {
    try {
      const response = await api.get(`/audit/export/${auditId}`, {
        params: { format },
        responseType: format === 'json' ? 'json' : 'blob',
      });

      if (format === 'json') {
        return new Blob([JSON.stringify(response.data)], { type: 'application/json' });
      }
      
      return response.data;
    } catch (error) {
      console.error(`Erro ao exportar auditoria ${auditId} no formato ${format}:`, error);
      throw error;
    }
  }

  /**
   * Verifica o status de saúde da aplicação
   */
  static async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  }

  // ===== MÉTODOS ADMINISTRATIVOS =====

  /**
   * Obtém métricas gerais do sistema
   */
  static async getMetrics(): Promise<AdminMetricsResponse> {
    const response = await api.get('/metrics');
    return response.data;
  }

  /**
   * Obtém métricas detalhadas do Prometheus
   */
  static async getPrometheusMetrics(): Promise<string> {
    const response = await api.get('/metrics/prometheus', {
      headers: { 'Accept': 'text/plain' }
    });
    return response.data;
  }

  /**
   * Verifica o status de saúde detalhado do sistema
   */
  static async getAdminHealth(): Promise<AdminHealthResponse> {
    const response = await api.get('/admin/health');
    return response.data;
  }

  /**
   * Obtém métricas de performance do sistema
   */
  static async getPerformanceMetrics(): Promise<AdminPerformanceResponse> {
    const response = await api.get('/admin/performance');
    return response.data;
  }

  /**
   * Obtém status do processador de auditorias
   */
  static async getProcessorStatus(): Promise<AdminProcessorResponse> {
    const response = await api.get('/admin/processor');
    return response.data;
  }

  /**
   * Obtém informações do sistema
   */
  static async getSystemInfo(): Promise<AdminSystemResponse> {
    const response = await api.get('/admin/system');
    return response.data;
  }

  /**
   * Reinicia o processador de auditorias
   */
  static async restartProcessor(): Promise<{ message: string }> {
    const response = await api.post('/admin/processor/restart');
    return response.data;
  }

  /**
   * Para o processador de auditorias
   */
  static async stopProcessor(): Promise<{ message: string }> {
    const response = await api.post('/admin/processor/stop');
    return response.data;
  }

  /**
   * Inicia o processador de auditorias
   */
  static async startProcessor(): Promise<{ message: string }> {
    const response = await api.post('/admin/processor/start');
    return response.data;
  }

  // Métodos para monitoramento detalhado

  /**
   * Obtém métricas detalhadas de monitoramento
   */
  static async getMonitoringMetrics(): Promise<MonitoringMetricsResponse> {
    const response = await api.get('/monitoring/metrics');
    return response.data;
  }

  /**
   * Obtém alertas do sistema
   */
  static async getMonitoringAlerts(includeResolved = false): Promise<MonitoringAlertsResponse> {
    const response = await api.get(`/monitoring/alerts?include_resolved=${includeResolved}`);
    return response.data;
  }

  /**
   * Obtém logs do sistema
   */
  static async getMonitoringLogs(
    page = 1,
    limit = 50,
    level?: string,
    module?: string
  ): Promise<MonitoringLogsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    
    if (level) params.append('level', level);
    if (module) params.append('module', module);
    
    const response = await api.get(`/monitoring/logs?${params}`);
    return response.data;
  }

  /**
   * Obtém dados históricos de monitoramento
   */
  static async getMonitoringHistorical(
    timeframe: '1h' | '6h' | '24h' | '7d' | '30d' = '24h'
  ): Promise<MonitoringHistoricalResponse> {
    const response = await api.get(`/monitoring/historical?timeframe=${timeframe}`);
    return response.data;
  }

  /**
   * Resolve um alerta
   */
  static async resolveAlert(alertId: string): Promise<{ message: string }> {
    const response = await api.post(`/monitoring/alerts/${alertId}/resolve`);
    return response.data;
  }

  /**
   * Obtém estatísticas em tempo real das auditorias
   */
  static async getRealtimeAuditStats(): Promise<{
    active_audits: number;
    queue_size: number;
    completed_today: number;
    failed_today: number;
    average_duration: number;
  }> {
    const response = await api.get('/audit/realtime-stats');
    return response.data;
  }
}

export default ApiService;