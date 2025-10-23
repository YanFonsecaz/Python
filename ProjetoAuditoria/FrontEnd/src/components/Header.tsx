import React from 'react';
import { Search, Bell, User, Sparkles } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  title?: string;
  showSearch?: boolean;
}

/**
 * Componente Header da aplicação com design moderno
 * Contém título, busca, notificações e controles de usuário
 */
export const Header: React.FC<HeaderProps> = ({ 
  title = 'Sistema de Auditoria SEO',
  showSearch = true 
}) => {
  return (
    <header className="glass border-b border-white/20 dark:border-gray-700/50 backdrop-blur-xl">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo e Título */}
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0 p-2 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-500 shadow-lg">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-display font-bold gradient-text">
                {title}
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                Powered by AI
              </p>
            </div>
          </div>

          {/* Barra de Busca */}
          {showSearch && (
            <div className="flex-1 max-w-lg mx-8">
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400 group-focus-within:text-primary-500 transition-colors" />
                </div>
                <input
                  type="text"
                  className="input-glass w-full pl-12 pr-4 py-3 text-sm placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50"
                  placeholder="Buscar auditorias..."
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
                  <kbd className="hidden sm:inline-flex items-center px-2 py-1 text-xs font-medium text-gray-400 bg-gray-100 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                    ⌘K
                  </kbd>
                </div>
              </div>
            </div>
          )}

          {/* Controles do usuário */}
          <div className="flex items-center space-x-3">
            {/* Notificações */}
            <button className="relative p-3 rounded-xl glass text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-all duration-200 hover:scale-105 active:scale-95 group">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 flex h-5 w-5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-error-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-5 w-5 bg-error-500 items-center justify-center">
                  <span className="text-xs font-bold text-white">3</span>
                </span>
              </span>
            </button>

            {/* Toggle de Tema */}
            <ThemeToggle />

            {/* Avatar do usuário */}
            <div className="relative">
              <button className="flex items-center space-x-3 p-2 rounded-xl glass hover:bg-white/30 dark:hover:bg-black/30 transition-all duration-200 hover:scale-105 active:scale-95 group">
                <div className="h-8 w-8 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center shadow-lg">
                  <User className="h-4 w-4 text-white" />
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Admin
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    admin@seo.com
                  </p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};