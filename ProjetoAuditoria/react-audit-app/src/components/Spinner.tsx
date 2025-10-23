import React from 'react';

/**
 * Componente Spinner para indicar estado de carregamento
 * Utiliza Tailwind CSS para estilização
 */
export const Spinner: React.FC = () => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      <span className="ml-3 text-gray-600">Carregando...</span>
    </div>
  );
};