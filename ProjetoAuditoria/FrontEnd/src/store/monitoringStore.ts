import { create } from 'zustand';
import { ApiService } from '../services/api';
import type {
  MonitoringMetricsResponse,
  MonitoringAlertsResponse,
  MonitoringLogsResponse,
  MonitoringHistoricalResponse,
} from '../services/api';

/**
 * Interface para o estado de monitoramento
 */
interface MonitoringState {
  // Estados de dados
  metrics: MonitoringMetricsResponse | null;
  alerts: MonitoringAlertsResponse | null;
  logs: MonitoringLogsResponse | null;
  historical: MonitoringHistoricalResponse | null;
  realtimeStats: {
    active_audits: number;
    queue_size: number;
    completed_today: number;
    failed_today: number;
    average_duration: number;
  } | null;

  // Estados de carregamento
  loading: {
    metrics: boolean;
    alerts: boolean;
    logs: boolean;
    historical: boolean;
    realtimeStats: boolean;
  };

  // Estados de erro
  error: {
    metrics: string | null;
    alerts: string | null;
    logs: string | null;
    historical: string | null;
    realtimeStats: string | null;
  };

  // Configurações
  autoRefresh: boolean;
  refreshInterval: number;
  selectedTimeframe: '1h' | '6h' | '24h' | '7d' | '30d';

  // Ações
  fetchMetrics: () => Promise<void>;
  fetchAlerts: (includeResolved?: boolean) => Promise<void>;
  fetchLogs: (page?: number, limit?: number, level?: string, module?: string) => Promise<void>;
  fetchHistorical: (timeframe?: '1h' | '6h' | '24h' | '7d' | '30d') => Promise<void>;
  fetchRealtimeStats: () => Promise<void>;
  fetchAllData: () => Promise<void>;
  resolveAlert: (alertId: string) => Promise<void>;
  setAutoRefresh: (enabled: boolean) => void;
  setRefreshInterval: (interval: number) => void;
  setSelectedTimeframe: (timeframe: '1h' | '6h' | '24h' | '7d' | '30d') => void;
  clearErrors: () => void;
  reset: () => void;
}

/**
 * Função utilitária para tratamento de erros
 */
const handleError = (error: any): string => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'Erro desconhecido';
};

/**
 * Store Zustand para gerenciamento de estado de monitoramento
 */
export const useMonitoringStore = create<MonitoringState>((set, get) => ({
  // Estados iniciais
  metrics: null,
  alerts: null,
  logs: null,
  historical: null,
  realtimeStats: null,

  loading: {
    metrics: false,
    alerts: false,
    logs: false,
    historical: false,
    realtimeStats: false,
  },

  error: {
    metrics: null,
    alerts: null,
    logs: null,
    historical: null,
    realtimeStats: null,
  },

  autoRefresh: true,
  refreshInterval: 30000, // 30 segundos
  selectedTimeframe: '24h',

  // Ações
  fetchMetrics: async () => {
    set((state) => ({
      loading: { ...state.loading, metrics: true },
      error: { ...state.error, metrics: null },
    }));

    try {
      const metrics = await ApiService.getMonitoringMetrics();
      set((state) => ({
        metrics,
        loading: { ...state.loading, metrics: false },
      }));
    } catch (error) {
      set((state) => ({
        loading: { ...state.loading, metrics: false },
        error: { ...state.error, metrics: handleError(error) },
      }));
    }
  },

  fetchAlerts: async (includeResolved = false) => {
    set((state) => ({
      loading: { ...state.loading, alerts: true },
      error: { ...state.error, alerts: null },
    }));

    try {
      const alerts = await ApiService.getMonitoringAlerts(includeResolved);
      set((state) => ({
        alerts,
        loading: { ...state.loading, alerts: false },
      }));
    } catch (error) {
      set((state) => ({
        loading: { ...state.loading, alerts: false },
        error: { ...state.error, alerts: handleError(error) },
      }));
    }
  },

  fetchLogs: async (page = 1, limit = 50, level?: string, module?: string) => {
    set((state) => ({
      loading: { ...state.loading, logs: true },
      error: { ...state.error, logs: null },
    }));

    try {
      const logs = await ApiService.getMonitoringLogs(page, limit, level, module);
      set((state) => ({
        logs,
        loading: { ...state.loading, logs: false },
      }));
    } catch (error) {
      set((state) => ({
        loading: { ...state.loading, logs: false },
        error: { ...state.error, logs: handleError(error) },
      }));
    }
  },

  fetchHistorical: async (timeframe?: '1h' | '6h' | '24h' | '7d' | '30d') => {
    const selectedTimeframe = timeframe || get().selectedTimeframe;
    
    set((state) => ({
      loading: { ...state.loading, historical: true },
      error: { ...state.error, historical: null },
      selectedTimeframe,
    }));

    try {
      const historical = await ApiService.getMonitoringHistorical(selectedTimeframe);
      set((state) => ({
        historical,
        loading: { ...state.loading, historical: false },
      }));
    } catch (error) {
      set((state) => ({
        loading: { ...state.loading, historical: false },
        error: { ...state.error, historical: handleError(error) },
      }));
    }
  },

  fetchRealtimeStats: async () => {
    set((state) => ({
      loading: { ...state.loading, realtimeStats: true },
      error: { ...state.error, realtimeStats: null },
    }));

    try {
      const realtimeStats = await ApiService.getRealtimeAuditStats();
      set((state) => ({
        realtimeStats,
        loading: { ...state.loading, realtimeStats: false },
      }));
    } catch (error) {
      set((state) => ({
        loading: { ...state.loading, realtimeStats: false },
        error: { ...state.error, realtimeStats: handleError(error) },
      }));
    }
  },

  fetchAllData: async () => {
    const { fetchMetrics, fetchAlerts, fetchLogs, fetchHistorical, fetchRealtimeStats } = get();
    
    await Promise.allSettled([
      fetchMetrics(),
      fetchAlerts(),
      fetchLogs(),
      fetchHistorical(),
      fetchRealtimeStats(),
    ]);
  },

  resolveAlert: async (alertId: string) => {
    try {
      await ApiService.resolveAlert(alertId);
      // Recarregar alertas após resolver
      await get().fetchAlerts();
    } catch (error) {
      set((state) => ({
        error: { ...state.error, alerts: handleError(error) },
      }));
    }
  },

  setAutoRefresh: (enabled: boolean) => {
    set({ autoRefresh: enabled });
  },

  setRefreshInterval: (interval: number) => {
    set({ refreshInterval: interval });
  },

  setSelectedTimeframe: (timeframe: '1h' | '6h' | '24h' | '7d' | '30d') => {
    set({ selectedTimeframe: timeframe });
  },

  clearErrors: () => {
    set({
      error: {
        metrics: null,
        alerts: null,
        logs: null,
        historical: null,
        realtimeStats: null,
      },
    });
  },

  reset: () => {
    set({
      metrics: null,
      alerts: null,
      logs: null,
      historical: null,
      realtimeStats: null,
      loading: {
        metrics: false,
        alerts: false,
        logs: false,
        historical: false,
        realtimeStats: false,
      },
      error: {
        metrics: null,
        alerts: null,
        logs: null,
        historical: null,
        realtimeStats: null,
      },
      autoRefresh: true,
      refreshInterval: 30000,
      selectedTimeframe: '24h',
    });
  },
}));