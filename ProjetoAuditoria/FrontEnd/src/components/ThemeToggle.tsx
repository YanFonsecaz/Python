import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useThemeStore } from '../store/themeStore';

/**
 * Componente para alternar entre tema claro e escuro
 */
export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <button
      onClick={toggleTheme}
      className="relative p-3 rounded-xl glass-light hover:glass-medium transition-all duration-300 transform hover:scale-105 group border border-glass-border shadow-md hover:shadow-glow"
      title={theme === 'light' ? 'Ativar modo escuro' : 'Ativar modo claro'}
    >
      <div className="relative">
        {theme === 'light' ? (
          <Moon className="w-5 h-5 text-primary-600 dark:text-primary-400 transition-all duration-300 group-hover:rotate-12" />
        ) : (
          <Sun className="w-5 h-5 text-accent-500 dark:text-accent-400 transition-all duration-300 group-hover:rotate-180" />
        )}
        
        {/* Efeito de brilho */}
        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-400/20 to-accent-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm"></div>
      </div>
    </button>
  );
};