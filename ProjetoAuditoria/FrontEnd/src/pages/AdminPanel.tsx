import React, { useEffect, useState } from 'react';
import { 
  CpuChipIcon, 
  ServerIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  PlayIcon,
  StopIcon,
  TrashIcon,
  ClockIcon,
  DocumentChartBarIcon
} from '@heroicons/react/24/outline';
import { useAdminStore } from '../store/adminStore';

/**
 * Componente de card para métricas do sistema
 */
interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  loading?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon, color, loading }) => {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-200 dark:border-green-800',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800',
    red: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-800',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-800'
  };

  return (
    <div className={`p-6 rounded-lg border ${colorClasses[color]} transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{title}</p>
          {loading ? (
            <div className="mt-2 h-8 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
          ) : (
            <p className="text-2xl font-bold mt-1">{value}</p>
          )}
        </div>
        <div className="p-3 rounded-full bg-white dark:bg-gray-800 shadow-sm">
          {icon}
        </div>
      </div>
    </div>
  );
};

/**
 * Componente de status de saúde
 */
interface HealthStatusProps {
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: {
    database: boolean;
    cache: boolean;
    processor: boolean;
    storage: boolean;
  };
  loading?: boolean;
}

const HealthStatus: React.FC<HealthStatusProps> = ({ status, checks, loading }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 dark:text-green-400';
      case 'degraded': return 'text-yellow-600 dark:text-yellow-400';
      case 'unhealthy': return 'text-red-600 dark:text-red-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircleIcon className="w-6 h-6" />;
      case 'degraded': return <ExclamationTriangleIcon className="w-6 h-6" />;
      case 'unhealthy': return <XCircleIcon className="w-6 h-6" />;
      default: return <ClockIcon className="w-6 h-6" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-4 h-4 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center space-x-3 mb-4">
        <div className={getStatusColor(status)}>
          {getStatusIcon(status)}
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Status do Sistema: <span className={getStatusColor(status)}>{status.toUpperCase()}</span>
        </h3>
      </div>
      
      <div className="space-y-3">
        {Object.entries(checks).map(([service, isHealthy]) => (
          <div key={service} className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">
              {service === 'database' ? 'Banco de Dados' : 
               service === 'cache' ? 'Cache' :
               service === 'processor' ? 'Processador' : 'Armazenamento'}
            </span>
            <div className={`flex items-center space-x-2 ${isHealthy ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {isHealthy ? (
                <CheckCircleIcon className="w-4 h-4" />
              ) : (
                <XCircleIcon className="w-4 h-4" />
              )}
              <span className="text-sm font-medium">
                {isHealthy ? 'OK' : 'Erro'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Componente principal do Painel Administrativo
 */
export const AdminPanel: React.FC = () => {
  const {
    metrics,
    health,
    processor,
    system,
    cacheStats,
    loading,
    error,
    fetchAllData,
    clearCache,
    restartProcessor,
    stopProcessor,
    startProcessor,
    clearError
  } = useAdminStore();

  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<number | null>(null);

  /**
   * Carrega todos os dados ao montar o componente
   */
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  /**
   * Gerencia o auto-refresh dos dados
   */
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchAllData();
      }, 30000); // Atualiza a cada 30 segundos
      setRefreshInterval(interval);
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [autoRefresh, fetchAllData]);

  /**
   * Formata bytes para formato legível
   */
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  /**
   * Formata tempo de uptime
   */
  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Cabeçalho */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Painel Administrativo
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Monitore e gerencie o sistema de auditoria SEO
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          <label className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
            />
            <span>Auto-refresh (30s)</span>
          </label>
          
          <button
            onClick={fetchAllData}
            disabled={Object.values(loading).some(Boolean)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <ArrowPathIcon className={`w-4 h-4 mr-2 ${Object.values(loading).some(Boolean) ? 'animate-spin' : ''}`} />
            Atualizar
          </button>
        </div>
      </div>

      {/* Alerta de erro */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <XCircleIcon className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Erro no sistema
              </h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                <p>{error}</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={clearError}
                  className="text-sm bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-200 px-3 py-1 rounded-md hover:bg-red-200 dark:hover:bg-red-900/60"
                >
                  Dispensar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cards de métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="CPU"
          value={metrics ? `${metrics.system.cpu_usage.toFixed(1)}%` : '-'}
          icon={<CpuChipIcon className="w-6 h-6" />}
          color={metrics && metrics.system.cpu_usage > 80 ? 'red' : metrics && metrics.system.cpu_usage > 60 ? 'yellow' : 'green'}
          loading={loading.metrics}
        />
        
        <MetricCard
          title="Memória"
          value={metrics ? `${metrics.system.memory_usage.toFixed(1)}%` : '-'}
          icon={<ServerIcon className="w-6 h-6" />}
          color={metrics && metrics.system.memory_usage > 80 ? 'red' : metrics && metrics.system.memory_usage > 60 ? 'yellow' : 'green'}
          loading={loading.metrics}
        />
        
        <MetricCard
          title="Auditorias Ativas"
          value={metrics ? metrics.application.active_audits : '-'}
          icon={<DocumentChartBarIcon className="w-6 h-6" />}
          color="blue"
          loading={loading.metrics}
        />
        
        <MetricCard
          title="Fila de Processamento"
          value={metrics ? metrics.application.queue_size : '-'}
          icon={<ChartBarIcon className="w-6 h-6" />}
          color={metrics && metrics.application.queue_size > 10 ? 'yellow' : 'green'}
          loading={loading.metrics}
        />
      </div>

      {/* Status de saúde e informações do sistema */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HealthStatus
          status={health?.status || 'unhealthy'}
          checks={health?.checks || { database: false, cache: false, processor: false, storage: false }}
          loading={loading.health}
        />
        
        {/* Informações do sistema */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Informações do Sistema
          </h3>
          
          {loading.system ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="flex justify-between">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
                </div>
              ))}
            </div>
          ) : system ? (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Versão:</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{system.version}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Ambiente:</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{system.environment}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Uptime:</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{formatUptime(system.uptime)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Memória Total:</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{formatBytes(system.memory.total)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">CPU Cores:</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{system.cpu.cores}</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">Dados não disponíveis</p>
          )}
        </div>
      </div>

      {/* Controles do processador */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Controle do Processador
          </h3>
          
          {processor && (
            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              processor.status === 'running' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' :
              processor.status === 'stopped' ? 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400' :
              'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
            }`}>
              {processor.status === 'running' ? 'Executando' : 
               processor.status === 'stopped' ? 'Parado' : 'Erro'}
            </div>
          )}
        </div>
        
        {loading.processor ? (
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full mb-4"></div>
            <div className="flex space-x-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
              ))}
            </div>
          </div>
        ) : processor ? (
          <div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">Fila</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{processor.queue_size}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">Ativas</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{processor.active_tasks}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">Concluídas</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{processor.completed_tasks}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">Falharam</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{processor.failed_tasks}</p>
              </div>
            </div>
            
            <div className="flex flex-wrap gap-3">
              <button
                onClick={startProcessor}
                disabled={loading.actions || processor.status === 'running'}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                <PlayIcon className="w-4 h-4 mr-2" />
                Iniciar
              </button>
              
              <button
                onClick={stopProcessor}
                disabled={loading.actions || processor.status === 'stopped'}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
              >
                <StopIcon className="w-4 h-4 mr-2" />
                Parar
              </button>
              
              <button
                onClick={restartProcessor}
                disabled={loading.actions}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <ArrowPathIcon className="w-4 h-4 mr-2" />
                Reiniciar
              </button>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400">Dados do processador não disponíveis</p>
        )}
      </div>

      {/* Controles de cache */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Gerenciamento de Cache
          </h3>
          
          <button
            onClick={clearCache}
            disabled={loading.actions}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
          >
            <TrashIcon className="w-4 h-4 mr-2" />
            Limpar Cache
          </button>
        </div>
        
        {loading.cache ? (
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          </div>
        ) : cacheStats ? (
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p>Estatísticas do cache carregadas com sucesso</p>
          </div>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400">Estatísticas do cache não disponíveis</p>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;