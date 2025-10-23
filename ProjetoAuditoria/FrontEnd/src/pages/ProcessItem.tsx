import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  useItemData, 
  useItemLoading, 
  useItemError, 
  useItemFetchItem, 
  useItemClearError, 
  useItemReset 
} from '../store/itemStore';
import { Spinner } from '../components/Spinner';

/**
 * Página principal para processar itens através da API Flask
 * 
 * Permite ao usuário inserir um ID de item e visualizar o resultado
 * do processamento com tratamento de estados de carregamento e erro
 */
export const ProcessItem: React.FC = () => {
  const [itemId, setItemId] = useState<string>('');
  const navigate = useNavigate();

  // Estados do store
  const data = useItemData();
  const loading = useItemLoading();
  const error = useItemError();
  const fetchItem = useItemFetchItem();
  const clearError = useItemClearError();
  const reset = useItemReset();

  /**
   * Manipula o envio do formulário
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const id = parseInt(itemId, 10);
    
    // Validação do ID
    if (isNaN(id)) {
      alert('Por favor, insira um ID válido (número)');
      return;
    }

    // Limpa erro anterior e busca o item
    clearError();
    await fetchItem(id, navigate);
  };

  /**
   * Limpa o formulário e reseta o estado
   */
  const handleReset = () => {
    setItemId('');
    reset();
  };

  /**
   * Navega para a página de erro quando há erro
   */
  React.useEffect(() => {
    if (error) {
      navigate('/error', { state: { error } });
    }
  }, [error, navigate]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Cabeçalho */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Processador de Itens
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Insira um ID para processar um item através da API Flask
          </p>
        </div>

        {/* Formulário */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label 
                htmlFor="itemId" 
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                ID do Item
              </label>
              <input
                type="number"
                id="itemId"
                value={itemId}
                onChange={(e) => setItemId(e.target.value)}
                placeholder="Digite o ID do item (ex: 123)"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         placeholder-gray-500 dark:placeholder-gray-400"
                disabled={loading}
                required
              />
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={loading || !itemId.trim()}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 
                         text-white font-medium py-2 px-4 rounded-lg transition-colors
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <Spinner size="sm" color="white" />
                    <span>Processando...</span>
                  </div>
                ) : (
                  'Processar Item'
                )}
              </button>

              <button
                type="button"
                onClick={handleReset}
                disabled={loading}
                className="px-6 py-2 border border-gray-300 dark:border-gray-600 
                         text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 
                         dark:hover:bg-gray-700 transition-colors focus:outline-none 
                         focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Limpar
              </button>
            </div>
          </form>
        </div>

        {/* Estado de Carregamento */}
        {loading && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
            <Spinner size="lg" className="mb-4" />
            <p className="text-gray-600 dark:text-gray-400">
              Processando item ID {itemId}...
            </p>
          </div>
        )}

        {/* Resultado do Processamento */}
        {data && !loading && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg shadow-lg p-6">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-green-800 dark:text-green-200 mb-2">
                  Item Processado com Sucesso!
                </h3>
                <div className="space-y-2">
                  <p className="text-sm text-green-700 dark:text-green-300">
                    <span className="font-medium">ID do Item:</span> {data.item_id}
                  </p>
                  <p className="text-sm text-green-700 dark:text-green-300">
                    <span className="font-medium">Resultado:</span>
                  </p>
                  <div className="bg-white dark:bg-gray-800 p-3 rounded border border-green-200 dark:border-green-700">
                    <code className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                      {data.result}
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Estado Vazio */}
        {!data && !loading && !error && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-12 text-center">
            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Nenhum item processado
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Insira um ID no formulário acima para processar um item
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessItem;