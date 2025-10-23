import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  Database, 
  Clock, 
  TrendingUp, 
  Server, 
  MemoryStick,
  HardDrive,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Zap,
  Cpu
} from 'lucide-react';
import { Spinner } from '../components';
import { useNotifications } from '../store/notificationStore';

/**
 * Interface para as métricas do sistema
 */
interface SystemMetrics {
  timestamp: string;
  system: {
    active_audits: number;
    completed_audits: number;
    total_audits_in_history: number;
  };
  cache: {
    memory: {
      size: number;
      max_size: number;
      hit_ratio: number;
      expired_items: number;
    };
    disk: {
      items: number;
      total_size_mb: number;
      max_size_mb: number;
      usage_percent: number;
      expired_items: number;
    };
    redis_available: boolean;
  };
  async_processor: {
    running: boolean;
    max_workers: number;
    uptime_seconds: number | null;
    queue: {
      pending: number;
      running: number;
      completed: number;
      total_active: number;
      queue_size: number;
    };
    metrics: {
      tasks_processed: number;
      tasks_failed: number;
      tasks_retried: number;
      average_execution_time: number;
      started_at: string | null;
    };
  };
  memory: {
    active_audits_memory: number;
    results_memory: number;
  };
}

/**
 * Componente para cartão de métrica
 */
interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  loading?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit = '',
  icon,
  trend,
  trendValue,
  color = 'blue',
  loading = false
}) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600 text-blue-600',
    green: 'from-green-500 to-green-600 text-green-600',
    yellow: 'from-yellow-500 to-yellow-600 text-yellow-600',
    red: 'from-red-500 to-red-600 text-red-600',
    purple: 'from-purple-500 to-purple-600 text-purple-600'
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />;
      default:
        return <div className="w-4 h-4 bg-gray-400 rounded-full" />;
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-gradient-to-r ${colorClasses[color].split(' ')[0]} ${colorClasses[color].split(' ')[1]}`}>
          <div className="text-white">
            {icon}
          </div>
        </div>
        {trend && trendValue && (
          <div className="flex items-center gap-1 text-sm">
            {getTrendIcon()}
            <span className={trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'}>
              {trendValue}
            </span>
          </div>
        )}
      </div>
      
      <div className="space-y-1">
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
          {title}
        </h3>
        <div className="flex items-baseline gap-2">
          {loading ? (
            <div className="w-16 h-8 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          ) : (
            <>
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {typeof value === 'number' ? value.toLocaleString() : value}
              </span>
              {unit && (
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {unit}
                </span>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * Componente para barra de progresso
 */
interface ProgressBarProps {
  value: number;
  max: number;
  label: string;
  color?: 'blue' | 'green' | 'yellow' | 'red';
}

const ProgressBar: React.FC<ProgressBarProps> = ({ 
  value, 
  max, 
  label, 
  color = 'blue' 
}) => {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500'
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600 dark:text-gray-400">{label}</span>
        <span className="text-gray-900 dark:text-white font-medium">
          {value.toLocaleString()} / {max.toLocaleString()}
        </span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${colorClasses[color]}`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400">
        {percentage.toFixed(1)}% utilizado
      </div>
    </div>
  );
};

/**
 * Página de métricas avançadas do sistema
 */
export const Metrics: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const { showError } = useNotifications();

  /**
   * Carrega as métricas do sistema
   */
  const loadMetrics = async () => {
    try {
      setError(null);
      const response = await fetch('http://localhost:5001/metrics');
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setMetrics(data);
    } catch (err: any) {
      const errorMessage = err.message || 'Erro ao carregar métricas';
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Efeito para carregar métricas iniciais
   */
  useEffect(() => {
    loadMetrics();
  }, []);

  /**
   * Efeito para auto-refresh
   */
  useEffect(() => {
    let interval: number;
    
    if (autoRefresh) {
      interval = setInterval(loadMetrics, 30000); // 30 segundos
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [autoRefresh]);

  /**
   * Formata tempo de uptime
   */
  const formatUptime = (seconds: number | null): string => {
    if (!seconds) return 'N/A';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return `${hours}h ${minutes}m ${secs}s`;
  };

  /**
   * Calcula taxa de sucesso
   */
  const getSuccessRate = (processed: number, failed: number): number => {
    const total = processed + failed;
    return total > 0 ? ((processed / total) * 100) : 100;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Spinner />
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="flex flex-col items-center justify-center min-h-96 space-y-4">
        <AlertTriangle className="w-16 h-16 text-red-500" />
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Erro ao Carregar Métricas
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-center max-w-md">
          {error || 'Não foi possível carregar as métricas do sistema.'}
        </p>
        <button
          onClick={loadMetrics}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Métricas do Sistema
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Monitoramento em tempo real do desempenho e recursos
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="autoRefresh"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="autoRefresh" className="text-sm text-gray-600 dark:text-gray-400">
              Auto-refresh (30s)
            </label>
          </div>
          
          <button
            onClick={loadMetrics}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </button>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Auditorias Ativas"
          value={metrics.system.active_audits}
          icon={<Activity className="w-6 h-6" />}
          color="blue"
        />
        
        <MetricCard
          title="Auditorias Concluídas"
          value={metrics.system.completed_audits}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        
        <MetricCard
          title="Total no Histórico"
          value={metrics.system.total_audits_in_history}
          icon={<Database className="w-6 h-6" />}
          color="purple"
        />
        
        <MetricCard
          title="Processador"
          value={metrics.async_processor.running ? 'Ativo' : 'Inativo'}
          icon={<Cpu className="w-6 h-6" />}
          color={metrics.async_processor.running ? 'green' : 'red'}
        />
      </div>

      {/* Métricas do Processador Assíncrono */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-6">
          <Zap className="w-6 h-6 text-yellow-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Processador Assíncrono
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <MetricCard
            title="Workers Máximos"
            value={metrics.async_processor.max_workers}
            icon={<Server className="w-5 h-5" />}
            color="blue"
          />
          
          <MetricCard
            title="Uptime"
            value={formatUptime(metrics.async_processor.uptime_seconds)}
            icon={<Clock className="w-5 h-5" />}
            color="green"
          />
          
          <MetricCard
            title="Tarefas Processadas"
            value={metrics.async_processor.metrics.tasks_processed}
            icon={<BarChart3 className="w-5 h-5" />}
            color="purple"
          />
          
          <MetricCard
            title="Taxa de Sucesso"
            value={`${getSuccessRate(
              metrics.async_processor.metrics.tasks_processed,
              metrics.async_processor.metrics.tasks_failed
            ).toFixed(1)}%`}
            icon={<TrendingUp className="w-5 h-5" />}
            color="green"
          />
        </div>

        {/* Fila de Processamento */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Fila de Processamento
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {metrics.async_processor.queue.pending}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Pendentes
              </div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {metrics.async_processor.queue.running}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Em Execução
              </div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {metrics.async_processor.queue.completed}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Concluídas
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Métricas de Cache */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-6">
          <HardDrive className="w-6 h-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Sistema de Cache
          </h2>
          {!metrics.cache.redis_available && (
            <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
              Redis Indisponível
            </span>
          )}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Cache em Memória */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
              <MemoryStick className="w-5 h-5" />
              Cache em Memória
            </h3>
            
            <ProgressBar
              value={metrics.cache.memory.size}
              max={metrics.cache.memory.max_size}
              label="Utilização"
              color="blue"
            />
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Hit Ratio:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">
                  {(metrics.cache.memory.hit_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Expirados:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">
                  {metrics.cache.memory.expired_items}
                </span>
              </div>
            </div>
          </div>
          
          {/* Cache em Disco */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
              <HardDrive className="w-5 h-5" />
              Cache em Disco
            </h3>
            
            <ProgressBar
              value={metrics.cache.disk.total_size_mb}
              max={metrics.cache.disk.max_size_mb}
              label="Espaço Utilizado (MB)"
              color="green"
            />
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">Itens:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">
                  {metrics.cache.disk.items}
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">Expirados:</span>
                <span className="ml-2 font-medium text-gray-900 dark:text-white">
                  {metrics.cache.disk.expired_items}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Informações do Sistema */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Server className="w-6 h-6 text-gray-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Informações do Sistema
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              Última Atualização
            </h3>
            <p className="text-gray-900 dark:text-white">
              {new Date(metrics.timestamp).toLocaleString('pt-BR')}
            </p>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
              Uso de Memória
            </h3>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Auditorias Ativas:</span>
                <span>{metrics.memory.active_audits_memory} bytes</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Resultados:</span>
                <span>{metrics.memory.results_memory} bytes</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};