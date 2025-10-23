import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

/**
 * Interface para o estado passado via navegação
 */
interface LocationState {
  error?: string;
}

/**
 * Página de erro dedicada para exibir erros da aplicação
 * 
 * Recebe mensagens de erro via state da navegação e oferece
 * opções para voltar ao início ou tentar novamente
 */
export const ErrorPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Extrai a mensagem de erro do state da navegação
  const state = location.state as LocationState;
  const errorMessage = state?.error || 'Ocorreu um erro inesperado';

  /**
   * Navega de volta para a página inicial
   */
  const handleGoHome = () => {
    navigate('/process-item');
  };

  /**
   * Volta para a página anterior
   */
  const handleGoBack = () => {
    navigate(-1);
  };

  /**
   * Recarrega a página atual
   */
  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Ícone de erro */}
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-red-100 dark:bg-red-900/20">
            <AlertTriangle className="h-10 w-10 text-red-600 dark:text-red-400" />
          </div>
          
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Ops! Algo deu errado
          </h2>
          
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Encontramos um problema ao processar sua solicitação
          </p>
        </div>

        {/* Mensagem de erro */}
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Detalhes do erro:
              </h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                <p>{errorMessage}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Ações */}
        <div className="space-y-4">
          <button
            onClick={handleGoHome}
            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <span className="absolute left-0 inset-y-0 flex items-center pl-3">
              <Home className="h-5 w-5 text-blue-500 group-hover:text-blue-400" />
            </span>
            Voltar ao Início
          </button>

          <div className="flex space-x-3">
            <button
              onClick={handleGoBack}
              className="flex-1 flex justify-center items-center py-2 px-4 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
            >
              Voltar
            </button>

            <button
              onClick={handleRetry}
              className="flex-1 flex justify-center items-center py-2 px-4 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Tentar Novamente
            </button>
          </div>
        </div>

        {/* Informações adicionais */}
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Se o problema persistir, entre em contato com o suporte técnico
          </p>
        </div>
      </div>
    </div>
  );
};

export default ErrorPage;