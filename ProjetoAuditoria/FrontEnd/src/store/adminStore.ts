import { create } from 'zustand';
import { ApiService } from '../services/api';
import type { 
  AdminMetricsResponse, 
  AdminHealthResponse, 
  AdminPerformanceResponse, 
  AdminProcessorResponse, 
  AdminSystemResponse 
} from '../services/api';

interface AdminState {
  // Estados de dados
  metrics: AdminMetricsResponse | null;
  health: AdminHealthResponse | null;
  performance: AdminPerformanceResponse | null;
  processor: AdminProcessorResponse | null;
  system: AdminSystemResponse | null;
  prometheusMetrics: string | null;
  cacheStats: any | null;

  // Estados de carregamento
  loading: {
    metrics: boolean;
    health: boolean;
    performance: boolean;
    processor: boolean;
    system: boolean;
    prometheus: boolean;
    cache: boolean;
    actions: boolean;
  };

  // Estados de erro
  error: string | null;

  // Ações para buscar dados
  fetchMetrics: () => Promise<void>;
  fetchHealth: () => Promise<void>;
  fetchPerformance: () => Promise<void>;
  fetchProcessor: () => Promise<void>;
  fetchSystem: () => Promise<void>;
  fetchPrometheusMetrics: () => Promise<void>;
  fetchCacheStats: () => Promise<void>;
  fetchAllData: () => Promise<void>;

  // Ações administrativas
  clearCache: () => Promise<void>;
  restartProcessor: () => Promise<void>;
  stopProcessor: () => Promise<void>;
  startProcessor: () => Promise<void>;

  // Utilitários
  clearError: () => void;
  setError: (error: string) => void;
}

/**
 * Store Zustand para gerenciamento do estado administrativo
 * Centraliza todas as operações relacionadas ao painel administrativo
 */
export const useAdminStore = create<AdminState>((set, get) => ({
  // Estados iniciais
  metrics: null,
  health: null,
  performance: null,
  processor: null,
  system: null,
  prometheusMetrics: null,
  cacheStats: null,

  loading: {
    metrics: false,
    health: false,
    performance: false,
    processor: false,
    system: false,
    prometheus: false,
    cache: false,
    actions: false,
  },

  error: null,

  // Ações para buscar dados
  fetchMetrics: async () => {
    set((state) => ({ 
      loading: { ...state.loading, metrics: true },
      error: null 
    }));
    
    try {
      const metrics = await ApiService.getMetrics();
      set((state) => ({ 
        metrics,
        loading: { ...state.loading, metrics: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao buscar métricas',
        loading: { ...state.loading, metrics: false }
      }));
    }
  },

  fetchHealth: async () => {
    set((state) => ({ 
      loading: { ...state.loading, health: true },
      error: null 
    }));
    
    try {
      const health = await ApiService.getAdminHealth();
      set((state) => ({ 
        health,
        loading: { ...state.loading, health: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao buscar status de saúde',
        loading: { ...state.loading, health: false }
      }));
    }
  },

  fetchPerformance: async () => {
    set((state) => ({ 
      loading: { ...state.loading, performance: true },
      error: null 
    }));
    
    try {
      const performance = await ApiService.getPerformanceMetrics();
      set((state) => ({ 
        performance,
        loading: { ...state.loading, performance: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao buscar métricas de performance',
        loading: { ...state.loading, performance: false }
      }));
    }
  },

  fetchProcessor: async () => {
    set((state) => ({ 
      loading: { ...state.loading, processor: true },
      error: null 
    }));
    
    try {
      const processor = await ApiService.getProcessorStatus();
      set((state) => ({ 
        processor,
        loading: { ...state.loading, processor: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao buscar status do processador',
        loading: { ...state.loading, processor: false }
      }));
    }
  },

  fetchSystem: async () => {
    set((state) => ({ 
      loading: { ...state.loading, system: true },
      error: null 
    }));
    
    try {
      const system = await ApiService.getSystemInfo();
      set((state) => ({ 
        system,
        loading: { ...state.loading, system: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao buscar informações do sistema',
        loading: { ...state.loading, system: false }
      }));
    }
  },

  fetchPrometheusMetrics: async () => {
    set((state) => ({ 
      loading: { ...state.loading, prometheus: true },
      error: null 
    }));
    
    try {
      const prometheusMetrics = await ApiService.getPrometheusMetrics();
      set((state) => ({ 
        prometheusMetrics,
        loading: { ...state.loading, prometheus: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao buscar métricas do Prometheus',
        loading: { ...state.loading, prometheus: false }
      }));
    }
  },

  fetchCacheStats: async () => {
    set((state) => ({ 
      loading: { ...state.loading, cache: true },
      error: null 
    }));
    
    try {
      const cacheStats = await ApiService.getCacheStats();
      set((state) => ({ 
        cacheStats,
        loading: { ...state.loading, cache: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao buscar estatísticas do cache',
        loading: { ...state.loading, cache: false }
      }));
    }
  },

  /**
   * Busca todos os dados administrativos de uma vez
   */
  fetchAllData: async () => {
    const { 
      fetchMetrics, 
      fetchHealth, 
      fetchPerformance, 
      fetchProcessor, 
      fetchSystem, 
      fetchCacheStats 
    } = get();

    await Promise.allSettled([
      fetchMetrics(),
      fetchHealth(),
      fetchPerformance(),
      fetchProcessor(),
      fetchSystem(),
      fetchCacheStats(),
    ]);
  },

  // Ações administrativas
  clearCache: async () => {
    set((state) => ({ 
      loading: { ...state.loading, actions: true },
      error: null 
    }));
    
    try {
      await ApiService.clearCache();
      // Recarrega as estatísticas do cache após limpar
      await get().fetchCacheStats();
      set((state) => ({ 
        loading: { ...state.loading, actions: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao limpar cache',
        loading: { ...state.loading, actions: false }
      }));
    }
  },

  restartProcessor: async () => {
    set((state) => ({ 
      loading: { ...state.loading, actions: true },
      error: null 
    }));
    
    try {
      await ApiService.restartProcessor();
      // Recarrega o status do processador após reiniciar
      await get().fetchProcessor();
      set((state) => ({ 
        loading: { ...state.loading, actions: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao reiniciar processador',
        loading: { ...state.loading, actions: false }
      }));
    }
  },

  stopProcessor: async () => {
    set((state) => ({ 
      loading: { ...state.loading, actions: true },
      error: null 
    }));
    
    try {
      await ApiService.stopProcessor();
      // Recarrega o status do processador após parar
      await get().fetchProcessor();
      set((state) => ({ 
        loading: { ...state.loading, actions: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao parar processador',
        loading: { ...state.loading, actions: false }
      }));
    }
  },

  startProcessor: async () => {
    set((state) => ({ 
      loading: { ...state.loading, actions: true },
      error: null 
    }));
    
    try {
      await ApiService.startProcessor();
      // Recarrega o status do processador após iniciar
      await get().fetchProcessor();
      set((state) => ({ 
        loading: { ...state.loading, actions: false }
      }));
    } catch (error: any) {
      set((state) => ({ 
        error: error.message || 'Erro ao iniciar processador',
        loading: { ...state.loading, actions: false }
      }));
    }
  },

  // Utilitários
  clearError: () => set({ error: null }),
  
  setError: (error: string) => set({ error }),
}));

export default useAdminStore;