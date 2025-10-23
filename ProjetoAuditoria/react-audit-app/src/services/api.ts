import axios from 'axios';
import type { ApiResponse, ApiError } from '../types';

// Configuração da instância do Axios
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5001',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptador de resposta para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Erro com resposta do servidor
      const apiError: ApiError = error.response.data;
      throw new Error(apiError.error || 'Erro desconhecido do servidor');
    } else if (error.request) {
      // Erro de rede
      throw new Error('Erro de conexão com o servidor');
    } else {
      // Outros erros
      throw new Error('Erro inesperado');
    }
  }
);

// Classe de serviços da API
export class ApiService {
  /**
   * Busca dados de um item pelo ID
   * @param itemId - ID do item a ser processado
   * @returns Promise com os dados do item processado
   */
  static async processItem(itemId: number): Promise<ApiResponse> {
    try {
      const response = await api.get<ApiResponse>(`/process/${itemId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}