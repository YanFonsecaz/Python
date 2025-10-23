import { create } from 'zustand';
import type { 
  Audit, 
  AuditResult, 
  AuditFilters, 
  PaginationParams,
  DashboardStats 
} from '../types';

interface AuditState {
  // Estado das auditorias
  audits: Audit[];
  currentAudit: Audit | null;
  auditResult: AuditResult | null;
  dashboardStats: DashboardStats | null;
  
  // Estados de loading
  loading: boolean;
  loadingStats: boolean;
  loadingResult: boolean;
  
  // Estados de erro
  error: string | null;
  
  // Filtros e paginação
  filters: AuditFilters;
  pagination: PaginationParams;
  totalAudits: number;
  
  // Actions
  setAudits: (audits: Audit[]) => void;
  addAudit: (audit: Audit) => void;
  updateAudit: (auditId: string, updates: Partial<Audit>) => void;
  setCurrentAudit: (audit: Audit | null) => void;
  setAuditResult: (result: AuditResult | null) => void;
  setDashboardStats: (stats: DashboardStats | null) => void;
  
  // Loading states
  setLoading: (loading: boolean) => void;
  setLoadingStats: (loading: boolean) => void;
  setLoadingResult: (loading: boolean) => void;
  
  // Error handling
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Filters and pagination
  setFilters: (filters: Partial<AuditFilters>) => void;
  setPagination: (pagination: Partial<PaginationParams>) => void;
  setTotalAudits: (total: number) => void;
  
  // Utility actions
  reset: () => void;
  getAuditById: (id: string) => Audit | undefined;
}

const initialState = {
  audits: [],
  currentAudit: null,
  auditResult: null,
  dashboardStats: null,
  loading: false,
  loadingStats: false,
  loadingResult: false,
  error: null,
  filters: {},
  pagination: { page: 1, limit: 10 },
  totalAudits: 0,
};

/**
 * Store principal para gerenciamento de auditorias
 * Centraliza todo o estado relacionado às auditorias SEO
 */
export const useAuditStore = create<AuditState>((set, get) => ({
  ...initialState,
  
  /**
   * Define a lista completa de auditorias
   */
  setAudits: (audits: Audit[]) => {
    set({ audits });
  },
  
  /**
   * Adiciona uma nova auditoria à lista
   */
  addAudit: (audit: Audit) => {
    set((state) => ({
      audits: [audit, ...state.audits],
    }));
  },
  
  /**
   * Atualiza uma auditoria específica
   */
  updateAudit: (auditId: string, updates: Partial<Audit>) => {
    set((state) => ({
      audits: state.audits.map((audit) =>
        audit.id === auditId ? { ...audit, ...updates } : audit
      ),
      currentAudit: 
        state.currentAudit?.id === auditId 
          ? { ...state.currentAudit, ...updates }
          : state.currentAudit,
    }));
  },
  
  /**
   * Define a auditoria atual sendo visualizada
   */
  setCurrentAudit: (audit: Audit | null) => {
    set({ currentAudit: audit });
  },
  
  /**
   * Define o resultado da auditoria atual
   */
  setAuditResult: (result: AuditResult | null) => {
    set({ auditResult: result });
  },
  
  /**
   * Define as estatísticas do dashboard
   */
  setDashboardStats: (stats: DashboardStats | null) => {
    set({ dashboardStats: stats });
  },
  
  /**
   * Define o estado de loading geral
   */
  setLoading: (loading: boolean) => {
    set({ loading });
  },
  
  /**
   * Define o estado de loading das estatísticas
   */
  setLoadingStats: (loading: boolean) => {
    set({ loadingStats: loading });
  },
  
  /**
   * Define o estado de loading dos resultados
   */
  setLoadingResult: (loading: boolean) => {
    set({ loadingResult: loading });
  },
  
  /**
   * Define uma mensagem de erro
   */
  setError: (error: string | null) => {
    set({ error });
  },
  
  /**
   * Limpa a mensagem de erro
   */
  clearError: () => {
    set({ error: null });
  },
  
  /**
   * Atualiza os filtros de busca
   */
  setFilters: (newFilters: Partial<AuditFilters>) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }));
  },
  
  /**
   * Atualiza os parâmetros de paginação
   */
  setPagination: (newPagination: Partial<PaginationParams>) => {
    set((state) => ({
      pagination: { ...state.pagination, ...newPagination },
    }));
  },
  
  /**
   * Define o total de auditorias (para paginação)
   */
  setTotalAudits: (total: number) => {
    set({ totalAudits: total });
  },
  
  /**
   * Reseta o store para o estado inicial
   */
  reset: () => {
    set(initialState);
  },
  
  /**
   * Busca uma auditoria pelo ID
   */
  getAuditById: (id: string) => {
    return get().audits.find((audit) => audit.id === id);
  },
}));