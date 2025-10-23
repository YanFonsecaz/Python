import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useItemStore } from '../store/itemStore';

/**
 * Página de erro da aplicação
 * Exibe mensagens de erro e opções para tentar novamente ou voltar ao início
 */
export const ErrorPage: React.FC = () => {
  const navigate = useNavigate();
  const { error, clearError } = useItemStore();

  /**
   * Navega de volta para a página inicial e limpa o erro
   */
  const handleGoHome = () => {
    clearError();
    navigate('/');
  };

  /**
   * Tenta novamente limpando o erro e voltando para a página inicial
   */
  const handleTryAgain = () => {
    clearError();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-8">
      <div className="max-w-md mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          {/* Ícone de erro */}
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
            <svg
              className="h-8 w-8 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>

          {/* Título */}
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Ops! Algo deu errado
          </h1>

          {/* Mensagem de erro */}
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800 text-sm">
              {error || 'Ocorreu um erro inesperado. Tente novamente.'}
            </p>
          </div>

          {/* Botões de ação */}
          <div className="space-y-3">
            <button
              onClick={handleTryAgain}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Tentar Novamente
            </button>
            
            <button
              onClick={handleGoHome}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              Voltar ao Início
            </button>
          </div>

          {/* Informações adicionais */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Se o problema persistir, verifique se a API está funcionando corretamente.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};