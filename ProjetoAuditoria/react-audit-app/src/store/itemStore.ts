import { create } from 'zustand';
import { ApiService } from '../services/api';
import type { ItemState } from '../types';

/**
 * Store Zustand para gerenciamento do estado dos itens
 * Contém dados, estado de carregamento, erros e ações
 */
export const useItemStore = create<ItemState>((set) => ({
  // Estado inicial
  data: null,
  loading: false,
  error: null,

  /**
   * Busca dados de um item pelo ID
   * @param itemId - ID do item a ser processado
   * @param navigate - Função de navegação do React Router
   */
  fetchItem: async (itemId: number, navigate: (path: string) => void) => {
    // Inicia o carregamento e limpa erros anteriores
    set({ loading: true, error: null });
    
    try {
      // Chama a API para processar o item
      const data = await ApiService.processItem(itemId);
      
      // Atualiza o estado com os dados recebidos
      set({ data, loading: false });
    } catch (error) {
      // Em caso de erro, atualiza o estado e navega para página de erro
      const errorMessage = error instanceof Error ? error.message : 'Ocorreu um erro inesperado.';
      set({ error: errorMessage, loading: false });
      navigate('/error');
    }
  },

  /**
   * Limpa o estado de erro
   */
  clearError: () => {
    set({ error: null });
  },
}));