import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showSearch?: boolean;
}

/**
 * Componente Layout principal da aplicação
 * Combina Header, Sidebar e área de conteúdo com design moderno
 */
export const Layout: React.FC<LayoutProps> = ({ 
  children, 
  title,
  showSearch = true 
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-30 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-100/20 via-transparent to-secondary-100/20" />
      </div>
      
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
      />

      {/* Layout principal */}
      <div className="flex-1 lg:ml-64">
        {/* Botão do menu mobile */}
        <button
          type="button"
          className="lg:hidden fixed top-4 left-4 z-40 p-3 rounded-xl glass text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-200 hover:scale-105 active:scale-95 shadow-lg bg-white/90 dark:bg-gray-800/90 backdrop-blur-md"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          <span className="sr-only">Abrir sidebar</span>
          {sidebarOpen ? (
            <X className="h-5 w-5" />
          ) : (
            <Menu className="h-5 w-5" />
          )}
        </button>

        {/* Header */}
        <div className="sticky top-0 z-30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50">
          <Header title={title} showSearch={showSearch} />
        </div>

        {/* Conteúdo Principal */}
        <main className="relative z-10 min-h-screen">
          <div className="py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="animate-fade-in">
                {children}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};