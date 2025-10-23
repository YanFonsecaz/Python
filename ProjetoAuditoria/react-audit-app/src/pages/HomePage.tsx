import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useItemStore } from '../store/itemStore';
import { Spinner } from '../components/Spinner';

/**
 * Página principal da aplicação
 * Contém formulário para buscar itens por ID e exibe os resultados
 */
export const HomePage: React.FC = () => {
  const [id, setId] = useState('');
  const navigate = useNavigate();
  const { data, loading, fetchItem } = useItemStore();

  /**
   * Manipula o envio do formulário
   * @param e - Evento do formulário
   */
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const itemId = parseInt(id, 10);
    
    if (!isNaN(itemId) && itemId > 0) {
      fetchItem(itemId, navigate);
    } else {
      alert('Por favor, digite um ID válido (número positivo)');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            Processador de Itens
          </h1>
          
          {/* Formulário de busca */}
          <form onSubmit={handleSearch} className="mb-8">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label htmlFor="itemId" className="block text-sm font-medium text-gray-700 mb-2">
                  ID do Item
                </label>
                <input
                  id="itemId"
                  type="number"
                  value={id}
                  onChange={(e) => setId(e.target.value)}
                  placeholder="Digite o ID do item"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  required
                />
              </div>
              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={loading || !id.trim()}
                  className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Buscando...' : 'Buscar'}
                </button>
              </div>
            </div>
          </form>

          {/* Estado de carregamento */}
          {loading && <Spinner />}

          {/* Resultado da busca */}
          {data && !loading && (
            <div className="bg-green-50 border border-green-200 rounded-md p-6">
              <h2 className="text-lg font-semibold text-green-800 mb-3">
                Resultado do Processamento
              </h2>
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">ID do Item:</span> {data.item_id}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Resultado:</span>
                </p>
                <div className="bg-white p-4 rounded border border-green-200">
                  <p className="text-gray-800">{data.result}</p>
                </div>
              </div>
            </div>
          )}

          {/* Mensagem quando não há dados */}
          {!data && !loading && id && (
            <div className="text-center text-gray-500 py-8">
              <p>Digite um ID e clique em "Buscar" para processar um item.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};