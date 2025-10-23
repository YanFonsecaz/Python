import { create } from 'zustand';
import { processItem } from '../services/itemService';
import type { ItemResponse } from '../services/itemService';

/**
 * Interface para o estado do item
 */
interface ItemState {
  // Estado dos dados
  data: ItemResponse | null;
  
  // Estado de carregamento
  loading: boolean;
  
  // Estado de erro
  error: string | null;
  
  // Ações
  fetchItem: (itemId: number, navigate: (path: string, options?: { state?: any }) => void) => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

/**
 * Store Zustand para gerenciamento de estado global da aplicação
 * 
 * Gerencia o estado dos dados, carregamento e erros relacionados
 * ao processamento de itens através da API Flask
 */
export const useItemStore = create<ItemState>((set) => ({
  // Estado inicial
  data: null,
  loading: false,
  error: null,

  /**
   * Busca um item através da API
   * 
   * @param itemId - ID do item a ser processado
   * @param navigate - Função de navegação
   */
  fetchItem: async (itemId: number, navigate: (path: string, options?: { state?: any }) => void) => {
    set({ loading: true, error: null });
    try {
      const response = await processItem(itemId);
      set({ data: response, loading: false });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Ocorreu um erro inesperado.';
      set({ error: errorMessage, loading: false });
      navigate('/error', { state: { error: errorMessage } });
    }
  },

  /**
   * Limpa o estado de erro
   */
  clearError: () => {
    set({ error: null });
  },

  /**
   * Reseta o estado para os valores iniciais
   */
  reset: () => {
    set({ data: null, loading: false, error: null });
  },
}));

// Seletores otimizados para evitar re-renders desnecessários
export const useItemData = () => useItemStore((state) => state.data);
export const useItemLoading = () => useItemStore((state) => state.loading);
export const useItemError = () => useItemStore((state) => state.error);
export const useItemFetchItem = () => useItemStore((state) => state.fetchItem);
export const useItemClearError = () => useItemStore((state) => state.clearError);
export const useItemReset = () => useItemStore((state) => state.reset);