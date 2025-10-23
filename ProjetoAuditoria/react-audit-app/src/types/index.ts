// Tipos para a resposta da API
export interface ApiResponse {
  item_id: number;
  result: string;
}

// Tipos para erro da API
export interface ApiError {
  error: string;
}

// Estado do item no store
export interface ItemState {
  data: ApiResponse | null;
  loading: boolean;
  error: string | null;
  fetchItem: (itemId: number, navigate: (path: string) => void) => Promise<void>;
  clearError: () => void;
}