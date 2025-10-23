import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  Database, 
  Clock, 
  TrendingUp, 
  MemoryStick,
  HardDrive,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Cpu,
  Download,
  Eye
} from 'lucide-react';
import { useAdminStore } from '../store/adminStore';
import { Spinner } from '../components';
import { useNotifications } from '../store/notificationStore';

/**
 * Interface para métricas parseadas do Prometheus
 */
interface ParsedPrometheusMetrics {
  activeAudits: number;
  completedAudits: number;
  cacheHits: number;
  cacheMisses: number;
  queueSize: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  responseTime: number;
  errorRate: number;
  uptime: number;
  timestamp: string;
}

/**
 * Componente para cartão de métrica Prometheus
 */
interface PrometheusMetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  loading?: boolean;
  description?: string;
}

const PrometheusMetricCard: React.FC<PrometheusMetricCardProps> = ({
  title,
  value,
  unit = '',
  icon,
  trend,
  trendValue,
  color = 'blue',
  loading = false,
  description
}) => {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600 text-blue-600',
    green: 'from-green-500 to-green-600 text-green-600',
    yellow: 'from-yellow-500 to-yellow-600 text-yellow-600',
    red: 'from-red-500 to-red-600 text-red-600',
    purple: 'from-purple-500 to-purple-600 text-purple-600'
  };

  const bgClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20',
    green: 'bg-green-50 dark:bg-green-900/20',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20',
    red: 'bg-red-50 dark:bg-red-900/20',
    purple: 'bg-purple-50 dark:bg-purple-900/20'
  };

  const trendIcons = {
    up: <TrendingUp className="w-4 h-4 text-green-500" />,
    down: <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />,
    stable: <Activity className="w-4 h-4 text-gray-500" />
  };

  return (
    <div className={`${bgClasses[color]} rounded-lg p-6 border border-gray-200 dark:border-gray-700`}>
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-gradient-to-r ${colorClasses[color]} text-white`}>
          {icon}
        </div>
        {trend && trendValue && (
          <div className="flex items-center space-x-1">
            {trendIcons[trend]}
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {trendValue}
            </span>
          </div>
        )}
      </div>
      
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
          {title}
        </h3>
        
        {loading ? (
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900 dark:border-white"></div>
            <span className="text-sm text-gray-500">Carregando...</span>
          </div>
        ) : (
          <div className="flex items-baseline space-x-1">
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </span>
            {unit && (
              <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {unit}
              </span>
            )}
          </div>
        )}
        
        {description && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {description}
          </p>
        )}
      </div>
    </div>
  );
};

/**
 * Componente para gráfico de barras simples
 */
interface SimpleBarChartProps {
  data: Array<{ label: string; value: number; color?: string }>;
  title: string;
  maxValue?: number;
}

const SimpleBarChart: React.FC<SimpleBarChartProps> = ({ data, title, maxValue }) => {
  const max = maxValue || Math.max(...data.map(d => d.value));
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {title}
      </h3>
      
      <div className="space-y-4">
        {data.map((item, index) => (
          <div key={index} className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {item.label}
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {item.value.toLocaleString()}
              </span>
            </div>
            
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${item.color || 'bg-blue-500'}`}
                style={{ width: `${(item.value / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Parser para métricas do Prometheus
 */
const parsePrometheusMetrics = (rawMetrics: string): ParsedPrometheusMetrics => {
  const lines = rawMetrics.split('\n');
  const metrics: any = {};
  
  lines.forEach(line => {
    if (line.startsWith('#') || !line.trim()) return;
    
    const [metricName, value] = line.split(' ');
    if (metricName && value) {
      metrics[metricName] = parseFloat(value) || 0;
    }
  });
  
  return {
    activeAudits: metrics['seo_audit_active_audits'] || 0,
    completedAudits: metrics['seo_audit_completed_audits'] || 0,
    cacheHits: metrics['seo_audit_cache_hits'] || 0,
    cacheMisses: metrics['seo_audit_cache_misses'] || 0,
    queueSize: metrics['seo_audit_queue_size'] || 0,
    cpuUsage: metrics['seo_audit_cpu_percent'] || 0,
    memoryUsage: metrics['seo_audit_memory_percent'] || 0,
    diskUsage: metrics['seo_audit_disk_usage_percent'] || 0,
    responseTime: metrics['seo_audit_avg_response_time'] || 0,
    errorRate: metrics['seo_audit_error_rate'] || 0,
    uptime: metrics['seo_audit_uptime_seconds'] || 0,
    timestamp: new Date().toISOString()
  };
};

/**
 * Página de Dashboard de Métricas Prometheus
 */
export const PrometheusMetrics: React.FC = () => {
  const { 
    prometheusMetrics, 
    loading, 
    error, 
    fetchPrometheusMetrics 
  } = useAdminStore();
  
  const [parsedMetrics, setParsedMetrics] = useState<ParsedPrometheusMetrics | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30); // segundos
  const { showError, showSuccess } = useNotifications();

  /**
   * Carrega as métricas do Prometheus
   */
  const loadMetrics = async () => {
    try {
      await fetchPrometheusMetrics();
    } catch (err: any) {
      showError('Erro ao carregar métricas do Prometheus');
    }
  };

  /**
   * Efeito para carregar métricas iniciais
   */
  useEffect(() => {
    loadMetrics();
  }, []);

  /**
   * Efeito para parsear métricas quando recebidas
   */
  useEffect(() => {
    if (prometheusMetrics) {
      try {
        const parsed = parsePrometheusMetrics(prometheusMetrics);
        setParsedMetrics(parsed);
      } catch (err) {
        showError('Erro ao processar métricas do Prometheus');
      }
    }
  }, [prometheusMetrics]);

  /**
   * Efeito para auto-refresh
   */
  useEffect(() => {
    let interval: number;
    
    if (autoRefresh) {
      interval = setInterval(loadMetrics, refreshInterval * 1000);
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [autoRefresh, refreshInterval]);

  /**
   * Formata tempo de uptime
   */
  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return `${hours}h ${minutes}m ${secs}s`;
  };

  /**
   * Calcula taxa de hit do cache
   */
  const getCacheHitRate = (hits: number, misses: number): number => {
    const total = hits + misses;
    return total > 0 ? ((hits / total) * 100) : 0;
  };

  /**
   * Exporta métricas como JSON
   */
  const exportMetrics = () => {
    if (!parsedMetrics) return;
    
    const dataStr = JSON.stringify(parsedMetrics, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `prometheus-metrics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    showSuccess('Métricas exportadas com sucesso');
  };

  if (loading.prometheus) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Spinner />
      </div>
    );
  }

  if (error || !parsedMetrics) {
    return (
      <div className="flex flex-col items-center justify-center min-h-96 space-y-4">
        <AlertTriangle className="w-16 h-16 text-red-500" />
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Erro ao Carregar Métricas Prometheus
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-center max-w-md">
          {error || 'Não foi possível carregar as métricas do Prometheus.'}
        </p>
        <button
          onClick={loadMetrics}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard Prometheus
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Métricas detalhadas do sistema em formato Prometheus
          </p>
        </div>
        
        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          {/* Controles de refresh */}
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-gray-700 dark:text-gray-300">Auto-refresh</span>
            </label>
            
            {autoRefresh && (
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value={15}>15s</option>
                <option value={30}>30s</option>
                <option value={60}>1min</option>
                <option value={300}>5min</option>
              </select>
            )}
          </div>
          
          {/* Botões de ação */}
          <button
            onClick={loadMetrics}
            disabled={loading.prometheus}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading.prometheus ? 'animate-spin' : ''}`} />
            <span>Atualizar</span>
          </button>
          
          <button
            onClick={exportMetrics}
            className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Exportar</span>
          </button>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <PrometheusMetricCard
          title="Auditorias Ativas"
          value={parsedMetrics.activeAudits}
          icon={<Activity className="w-6 h-6" />}
          color="blue"
          description="Auditorias em execução"
        />
        
        <PrometheusMetricCard
          title="Auditorias Completadas"
          value={parsedMetrics.completedAudits}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
          description="Total de auditorias finalizadas"
        />
        
        <PrometheusMetricCard
          title="Taxa de Hit do Cache"
          value={getCacheHitRate(parsedMetrics.cacheHits, parsedMetrics.cacheMisses).toFixed(1)}
          unit="%"
          icon={<Database className="w-6 h-6" />}
          color="purple"
          description="Eficiência do sistema de cache"
        />
        
        <PrometheusMetricCard
          title="Tempo de Resposta"
          value={parsedMetrics.responseTime.toFixed(0)}
          unit="ms"
          icon={<Clock className="w-6 h-6" />}
          color="yellow"
          description="Tempo médio de resposta"
        />
      </div>

      {/* Métricas de Sistema */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <PrometheusMetricCard
          title="Uso de CPU"
          value={parsedMetrics.cpuUsage.toFixed(1)}
          unit="%"
          icon={<Cpu className="w-6 h-6" />}
          color={parsedMetrics.cpuUsage > 80 ? 'red' : parsedMetrics.cpuUsage > 60 ? 'yellow' : 'green'}
          description="Utilização do processador"
        />
        
        <PrometheusMetricCard
          title="Uso de Memória"
          value={parsedMetrics.memoryUsage.toFixed(1)}
          unit="%"
          icon={<MemoryStick className="w-6 h-6" />}
          color={parsedMetrics.memoryUsage > 80 ? 'red' : parsedMetrics.memoryUsage > 60 ? 'yellow' : 'green'}
          description="Utilização da memória RAM"
        />
        
        <PrometheusMetricCard
          title="Uso de Disco"
          value={parsedMetrics.diskUsage.toFixed(1)}
          unit="%"
          icon={<HardDrive className="w-6 h-6" />}
          color={parsedMetrics.diskUsage > 80 ? 'red' : parsedMetrics.diskUsage > 60 ? 'yellow' : 'green'}
          description="Utilização do armazenamento"
        />
      </div>

      {/* Gráficos e Estatísticas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SimpleBarChart
          title="Estatísticas de Cache"
          data={[
            { label: 'Cache Hits', value: parsedMetrics.cacheHits, color: 'bg-green-500' },
            { label: 'Cache Misses', value: parsedMetrics.cacheMisses, color: 'bg-red-500' }
          ]}
        />
        
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Informações do Sistema
          </h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Uptime
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {formatUptime(parsedMetrics.uptime)}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Taxa de Erro
              </span>
              <span className={`text-sm font-bold ${
                parsedMetrics.errorRate > 5 ? 'text-red-500' : 
                parsedMetrics.errorRate > 1 ? 'text-yellow-500' : 'text-green-500'
              }`}>
                {parsedMetrics.errorRate.toFixed(2)}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Tamanho da Fila
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {parsedMetrics.queueSize}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Última Atualização
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {new Date(parsedMetrics.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Métricas Raw (para debug) */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Métricas Raw (Prometheus)
          </h3>
          <button
            onClick={() => {
              navigator.clipboard.writeText(prometheusMetrics || '');
              showSuccess('Métricas copiadas para a área de transferência');
            }}
            className="flex items-center space-x-2 px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <Eye className="w-4 h-4" />
            <span>Copiar</span>
          </button>
        </div>
        
        <pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-xs overflow-x-auto text-gray-800 dark:text-gray-200 max-h-64 overflow-y-auto">
          {prometheusMetrics}
        </pre>
      </div>
    </div>
  );
};