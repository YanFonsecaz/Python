import axios, { AxiosError, type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios';

/**
 * Interface para a resposta de sucesso da API
 */
export interface ItemResponse {
  item_id: number;
  result: string;
}

/**
 * Interface para a resposta de erro da API
 */
export interface ErrorResponse {
  error: string;
}

/**
 * Interface para adicionar metadata ao config do Axios
 */
interface RequestConfigWithMetadata extends InternalAxiosRequestConfig {
  metadata?: {
    startTime: Date;
  };
}

/**
 * Configuração da instância do Axios para comunicação com a API Flask
 * Otimizada para melhor performance e tratamento de erros
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 15000, // Aumentado para 15s para operações mais complexas
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // Configurações adicionais para melhor performance
  validateStatus: (status) => status >= 200 && status < 300,
  maxRedirects: 3,
});

/**
 * Interceptor para adicionar headers de requisição e logging
 */
api.interceptors.request.use(
  (config: RequestConfigWithMetadata) => {
    // Adiciona timestamp para tracking de performance
    config.metadata = { startTime: new Date() };
    
    // Log apenas em modo de desenvolvimento
    if (import.meta.env.VITE_DEV_MODE === 'true') {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Interceptor para tratamento de respostas com retry automático
 */
api.interceptors.response.use(
  (response) => {
    // Calcula tempo de resposta para monitoramento
    const endTime = new Date();
    const config = response.config as RequestConfigWithMetadata;
    const startTime = config.metadata?.startTime;
    const duration = startTime ? endTime.getTime() - startTime.getTime() : 0;
    
    if (import.meta.env.VITE_DEV_MODE === 'true') {
      console.log(`✅ API Response: ${response.status} ${response.config.url} (${duration}ms)`);
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Log detalhado do erro
    console.error('❌ API Response Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method,
    });
    
    // Retry automático para erros de rede (não para erros 4xx)
    if (
      !originalRequest._retry &&
      (!error.response || error.response.status >= 500) &&
      originalRequest
    ) {
      originalRequest._retry = true;
      
      // Aguarda 1 segundo antes de tentar novamente
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('🔄 Retrying request...');
      return api(originalRequest);
    }
    
    return Promise.reject(error);
  }
);

/**
 * Processa um item específico através da API Flask
 * @param itemId - ID do item a ser processado
 * @returns Promise com os dados processados do item
 * @throws Error em caso de falha na requisição
 */
export const processItem = async (itemId: number): Promise<ItemResponse> => {
  try {
    // Validação básica do input
    if (!itemId || itemId <= 0) {
      throw new Error('ID do item deve ser um número positivo');
    }

    const response = await api.get<ItemResponse>(`/process/${itemId}`);
    
    // Validação da resposta
    if (!response.data || typeof response.data.item_id === 'undefined') {
      throw new Error('Resposta inválida da API');
    }

    return response.data;
  } catch (error) {
    // Re-throw com contexto adicional
    if (axios.isAxiosError(error)) {
      const errorMessage = error.response?.data?.error || 
                          `Erro na comunicação com a API: ${error.message}`;
      throw new Error(errorMessage);
    }
    
    throw error;
  }
};

/**
 * Verifica a saúde da API Flask
 * @returns Promise<boolean> - true se a API estiver funcionando
 */
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health', { timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    console.warn('⚠️ API Health Check Failed:', error);
    return false;
  }
};

/**
 * Obtém informações sobre a versão da API
 * @returns Promise com informações da versão
 */
export const getApiVersion = async (): Promise<{ version: string; status: string }> => {
  try {
    const response = await api.get('/version');
    return response.data;
  } catch (error) {
    console.warn('⚠️ Failed to get API version:', error);
    return { version: 'unknown', status: 'unavailable' };
  }
};

export default api;