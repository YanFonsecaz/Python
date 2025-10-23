import { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Bell, 
  Palette, 
  Server, 
  Check, 
  X, 
  Download,
  Trash2,
  AlertCircle
} from 'lucide-react';
import { useThemeStore } from '../store/themeStore';
import { useNotificationStore } from '../store/notificationStore';
import { ApiService } from '../services/api';

/**
 * Interface para os dados de configurações
 */
interface SettingsData {
  theme: 'light' | 'dark';
  notifications: {
    auditComplete: boolean;
    auditFailed: boolean;
    systemUpdates: boolean;
    emailNotifications: boolean;
  };
  preferences: {
    autoRefresh: boolean;
    refreshInterval: number;
    defaultAuditType: 'complete' | 'basic' | 'technical';
    maxConcurrentAudits: number;
  };
  api: {
    baseUrl: string;
    timeout: number;
  };
}

/**
 * Página de configurações da aplicação
 */
export function Settings() {
  const { theme, setTheme } = useThemeStore();
  const { addNotification } = useNotificationStore();
  const [isLoading, setIsLoading] = useState(false);

  const [settings, setSettings] = useState<SettingsData>({
    theme: theme,
    notifications: {
      auditComplete: true,
      auditFailed: true,
      systemUpdates: false,
      emailNotifications: false,
    },
    preferences: {
      autoRefresh: true,
      refreshInterval: 30,
      defaultAuditType: 'complete',
      maxConcurrentAudits: 3,
    },
    api: {
      baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
      timeout: 30000,
    },
  });

  const [cacheStats, setCacheStats] = useState<any>(null);

  /**
   * Carrega as configurações salvas e estatísticas do sistema
   */
  useEffect(() => {
    const savedSettings = localStorage.getItem('auditSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error('Erro ao carregar configurações:', error);
      }
    }
    loadCacheStats();
  }, []);

  /**
   * Carrega estatísticas do cache do sistema
   */
  const loadCacheStats = async () => {
    try {
      const stats = await ApiService.getCacheStats();
      setCacheStats(stats);
    } catch (error) {
      console.error('Erro ao carregar estatísticas do cache:', error);
    }
  };

  /**
   * Atualiza uma configuração específica
   */
  const updateSettings = (section: keyof SettingsData, field: string, value: any) => {
    setSettings(prev => {
      const newSettings = { ...prev };
      if (section === 'theme') {
        newSettings.theme = value;
      } else {
        (newSettings[section] as any)[field] = value;
      }
      return newSettings;
    });
  };

  /**
   * Salva as configurações
   */
  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Aplica o tema
      setTheme(settings.theme);
      
      // Salva no localStorage
      localStorage.setItem('auditSettings', JSON.stringify(settings));
      
      // Simula salvamento das configurações
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addNotification({
        type: 'success',
        title: 'Configurações Salvas',
        message: 'Suas configurações foram salvas com sucesso.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Erro ao Salvar',
        message: 'Ocorreu um erro ao salvar as configurações.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Limpa o cache do sistema
   */
  const handleClearCache = async () => {
    if (!confirm('Tem certeza que deseja limpar o cache? Esta ação não pode ser desfeita.')) {
      return;
    }

    setIsLoading(true);
    try {
      await ApiService.clearCache();
      await loadCacheStats();
      addNotification({
        type: 'success',
        title: 'Cache Limpo',
        message: 'Cache do sistema foi limpo com sucesso!'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Erro ao limpar cache do sistema'
      });
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Exporta dados do sistema
   */
  const handleExportData = async () => {
    setIsLoading(true);
    try {
      const data = {
        settings,
        exportDate: new Date().toISOString(),
        version: '1.0.0'
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-settings-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      addNotification({
        type: 'success',
        title: 'Dados Exportados',
        message: 'Configurações exportadas com sucesso!'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Erro ao exportar dados'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  /**
   * Reseta as configurações para os valores padrão
   */
  const handleReset = () => {
    setSettings({
      theme: 'light',
      notifications: {
        auditComplete: true,
        auditFailed: true,
        systemUpdates: false,
        emailNotifications: false,
      },
      preferences: {
        autoRefresh: true,
        refreshInterval: 30,
        defaultAuditType: 'complete',
        maxConcurrentAudits: 3,
      },
      api: {
        baseUrl: 'http://localhost:5001',
        timeout: 30000,
      },
    });
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <SettingsIcon className="h-8 w-8" />
          Configurações
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Personalize sua experiência com a plataforma de auditoria
        </p>
      </div>

      <div className="space-y-8">
        {/* Tema */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <Palette className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Aparência
            </h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tema
              </label>
              <select
                value={settings.theme}
                onChange={(e) => updateSettings('theme', '', e.target.value as 'light' | 'dark')}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="light">Claro</option>
                <option value="dark">Escuro</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notificações */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="h-6 w-6 text-green-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Notificações
            </h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auditoria Concluída
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Receber notificação quando uma auditoria for concluída
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.auditComplete}
                onChange={(e) => updateSettings('notifications', 'auditComplete', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auditoria Falhada
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Receber notificação quando uma auditoria falhar
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.auditFailed}
                onChange={(e) => updateSettings('notifications', 'auditFailed', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Atualizações do Sistema
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Receber notificações sobre atualizações do sistema
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.systemUpdates}
                onChange={(e) => updateSettings('notifications', 'systemUpdates', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Notificações por Email
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Receber notificações por email
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.notifications.emailNotifications}
                onChange={(e) => updateSettings('notifications', 'emailNotifications', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
          </div>
        </div>

        {/* Preferências */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <SettingsIcon className="h-6 w-6 text-purple-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Preferências
            </h2>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Atualização Automática
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Atualizar automaticamente o status das auditorias
                </p>
              </div>
              <input
                type="checkbox"
                checked={settings.preferences.autoRefresh}
                onChange={(e) => updateSettings('preferences', 'autoRefresh', e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Intervalo de Atualização (segundos)
              </label>
              <input
                type="number"
                min="5"
                max="300"
                value={settings.preferences.refreshInterval}
                onChange={(e) => updateSettings('preferences', 'refreshInterval', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tipo de Auditoria Padrão
              </label>
              <select
                value={settings.preferences.defaultAuditType}
                onChange={(e) => updateSettings('preferences', 'defaultAuditType', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="complete">Completa</option>
                <option value="basic">Básica</option>
                <option value="technical">Técnica</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Máximo de Auditorias Simultâneas
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={settings.preferences.maxConcurrentAudits}
                onChange={(e) => updateSettings('preferences', 'maxConcurrentAudits', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
        </div>

        {/* API */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <Server className="h-6 w-6 text-orange-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Configurações da API
            </h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                URL Base da API
              </label>
              <input
                type="url"
                value={settings.api.baseUrl}
                onChange={(e) => updateSettings('api', 'baseUrl', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="http://localhost:5001"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Timeout (ms)
              </label>
              <input
                type="number"
                min="1000"
                max="120000"
                value={settings.api.timeout}
                onChange={(e) => updateSettings('api', 'timeout', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
        </div>

        {/* Sistema */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <AlertCircle className="h-6 w-6 text-red-600" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Sistema
            </h2>
          </div>
          
          <div className="space-y-4">
            {cacheStats && (
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Estatísticas do Cache
                </h3>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Entradas:</span>
                    <span className="ml-2 font-medium text-gray-900 dark:text-white">
                      {cacheStats.entries || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Tamanho:</span>
                    <span className="ml-2 font-medium text-gray-900 dark:text-white">
                      {formatBytes(cacheStats.size || 0)}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={handleClearCache}
                disabled={isLoading}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white rounded-md transition-colors flex items-center justify-center gap-2"
              >
                <Trash2 className="h-4 w-4" />
                Limpar Cache
              </button>
              <button
                onClick={handleExportData}
                disabled={isLoading}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-md transition-colors flex items-center justify-center gap-2"
              >
                <Download className="h-4 w-4" />
                Exportar Dados
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Botões de Ação */}
      <div className="flex justify-end gap-4 mt-8">
        <button
          onClick={handleReset}
          className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md transition-colors flex items-center gap-2"
        >
          <X className="h-4 w-4" />
          Resetar
        </button>
        
        <button
          onClick={handleSave}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md transition-colors flex items-center gap-2"
        >
          <Check className="h-4 w-4" />
          {isLoading ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </div>
  );
}