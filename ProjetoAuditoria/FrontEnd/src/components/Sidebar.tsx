import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Plus, 
  Activity, 
  FileText, 
  History, 
  Settings,
  BarChart3,
  BookOpen,
  Shield,
  Monitor,
  TrendingUp,
  Cog
} from 'lucide-react';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

/**
 * Componente Sidebar com navegação principal
 */
export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/',
      icon: Home,
    },
    {
      name: 'Nova Auditoria',
      href: '/audit/new',
      icon: Plus,
    },
    {
      name: 'Auditorias Ativas',
      href: '/audit/active',
      icon: Activity,
    },
    {
      name: 'Processar Item',
      href: '/process-item',
      icon: Cog,
    },
    {
      name: 'Resultados',
      href: '/audit/results',
      icon: BarChart3,
    },
    {
      name: 'Histórico',
      href: '/audit/history',
      icon: History,
    },
    {
      name: 'Relatórios',
      href: '/reports',
      icon: FileText,
    },
  ];

  const secondaryItems = [
    {
      name: 'Métricas',
      href: '/metrics',
      icon: TrendingUp,
    },
    {
      name: 'Documentação',
      href: '/audit/documentation',
      icon: BookOpen,
    },
    {
      name: 'Painel Admin',
      href: '/admin',
      icon: Shield,
    },
    {
      name: 'Monitoramento',
      href: '/monitoring',
      icon: Monitor,
    },
    {
      name: 'Configurações',
      href: '/settings',
      icon: Settings,
    },
  ];

  return (
    <>
      {/* Overlay para mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-20 bg-black/60 backdrop-blur-sm lg:hidden animate-fade-in"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-30 w-64 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-r border-gray-200/50 dark:border-gray-700/50 shadow-xl transform transition-all duration-500 ease-out lg:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 bg-gradient-to-r from-primary-600 via-primary-500 to-accent-500 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-primary-600/20 to-accent-500/20 animate-pulse"></div>
            <h2 className="text-xl font-bold text-white relative z-10 font-poppins tracking-wide">
              SEO Audit
            </h2>
          </div>

          {/* Navegação Principal */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            <div className="space-y-1">
              {navigationItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-300 transform hover:scale-105 ${
                      isActive
                        ? 'bg-gradient-to-r from-primary-500/20 to-accent-500/20 text-primary-600 dark:text-primary-400 shadow-lg border border-primary-200/30 dark:border-primary-700/30'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-100 hover:shadow-md border border-transparent hover:border-gray-200/30 dark:hover:border-gray-600/30'
                    }`
                  }
                  onClick={() => onClose?.()}
                >
                  <item.icon className={`mr-3 h-5 w-5 transition-all duration-300 ${
                    'group-hover:scale-110'
                  }`} />
                  <span className="font-inter">{item.name}</span>
                </NavLink>
              ))}
            </div>

            {/* Separador */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200 dark:border-gray-700"></div>
              </div>
              <div className="relative flex justify-center">
                <div className="w-2 h-2 bg-gradient-to-r from-primary-400 to-accent-400 rounded-full"></div>
              </div>
            </div>

            {/* Navegação Secundária */}
            <div className="space-y-1">
              {secondaryItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-300 transform hover:scale-105 ${
                      isActive
                        ? 'bg-gradient-to-r from-primary-500/20 to-accent-500/20 text-primary-600 dark:text-primary-400 shadow-lg border border-primary-200/30 dark:border-primary-700/30'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100/50 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-100 hover:shadow-md border border-transparent hover:border-gray-200/30 dark:hover:border-gray-600/30'
                    }`
                  }
                  onClick={() => onClose?.()}
                >
                  <item.icon className={`mr-3 h-5 w-5 transition-all duration-300 ${
                    'group-hover:scale-110'
                  }`} />
                  <span className="font-inter">{item.name}</span>
                </NavLink>
              ))}
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
            <div className="text-xs text-gray-500 dark:text-gray-400 text-center font-mono bg-gray-100/50 dark:bg-gray-700/50 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600">
              v{import.meta.env.VITE_APP_VERSION || '1.0.0'}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};