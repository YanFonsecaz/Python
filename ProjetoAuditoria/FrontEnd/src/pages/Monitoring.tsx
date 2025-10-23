import React, { useEffect, useState } from 'react';
import { useMonitoringStore } from '../store/monitoringStore';
import { Spinner } from '../components/Spinner';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  HardDrive,
  MemoryStick,
  Network,
  RefreshCw,
  TrendingUp,
  Users,
  Zap,
  XCircle,
  Info,
  AlertCircle,
} from 'lucide-react';

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
  unit,
  icon,
  trend,
  trendValue,
  color = 'blue',
  loading = false,
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    green: 'bg-green-50 border-green-200 text-green-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    red: 'bg-red-50 border-red-200 text-red-800',
    purple: 'bg-purple-50 border-purple-200 text-purple-800',
  };

  const iconColorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    red: 'text-red-600',
    purple: 'text-purple-600',
  };

  return (
    <div className={`p-6 rounded-lg border-2 ${colorClasses[color]} transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg bg-white ${iconColorClasses[color]}`}>
            {icon}
          </div>
          <div>
            <p className="text-sm font-medium opacity-75">{title}</p>
            {loading ? (
              <div className="flex items-center space-x-2">
                <Spinner size="sm" />
                <span className="text-sm">Carregando...</span>
              </div>
            ) : (
              <p className="text-2xl font-bold">
                {value}
                {unit && <span className="text-lg font-normal ml-1">{unit}</span>}
              </p>
            )}
          </div>
        </div>
        {trend && trendValue && !loading && (
          <div className={`flex items-center space-x-1 text-sm ${
            trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
          }`}>
            <TrendingUp className={`w-4 h-4 ${trend === 'down' ? 'rotate-180' : ''}`} />
            <span>{trendValue}</span>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Componente para alerta
 */
interface AlertItemProps {
  alert: {
    id: string;
    type: 'warning' | 'error' | 'info';
    message: string;
    timestamp: string;
    resolved: boolean;
    severity: 'low' | 'medium' | 'high' | 'critical';
  };
  onResolve: (id: string) => void;
}

const AlertItem: React.FC<AlertItemProps> = ({ alert, onResolve }) => {
  const getAlertIcon = () => {
    switch (alert.type) {
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'info':
        return <Info className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getSeverityColor = () => {
    switch (alert.severity) {
      case 'critical':
        return 'border-l-red-500 bg-red-50';
      case 'high':
        return 'border-l-orange-500 bg-orange-50';
      case 'medium':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-l-blue-500 bg-blue-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  return (
    <div className={`p-4 border-l-4 rounded-r-lg ${getSeverityColor()} ${alert.resolved ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          {getAlertIcon()}
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">{alert.message}</p>
            <p className="text-xs text-gray-500 mt-1">
              {new Date(alert.timestamp).toLocaleString('pt-BR')} • {alert.severity.toUpperCase()}
            </p>
          </div>
        </div>
        {!alert.resolved && (
          <button
            onClick={() => onResolve(alert.id)}
            className="ml-4 px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
          >
            Resolver
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * Componente principal de Monitoramento
 */
export const Monitoring: React.FC = () => {
  const {
    metrics,
    alerts,
    logs,
    historical,
    realtimeStats,
    loading,
    error,
    autoRefresh,
    refreshInterval,
    selectedTimeframe,
    fetchAllData,
    fetchHistorical,
    resolveAlert,
    setAutoRefresh,
    setRefreshInterval,
    setSelectedTimeframe,
    clearErrors,
  } = useMonitoringStore();

  const [refreshTimer, setRefreshTimer] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'alerts' | 'logs' | 'historical'>('overview');

  /**
   * Efeito para carregar dados iniciais
   */
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  /**
   * Efeito para auto-refresh
   */
  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const timer = window.setInterval(() => {
        fetchAllData();
      }, refreshInterval);
      setRefreshTimer(timer);

      return () => {
        if (timer) {
          clearInterval(timer);
        }
      };
    } else if (refreshTimer) {
      clearInterval(refreshTimer);
      setRefreshTimer(null);
    }
  }, [autoRefresh, refreshInterval, fetchAllData]);

  /**
   * Cleanup do timer
   */
  useEffect(() => {
    return () => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
      }
    };
  }, [refreshTimer]);

  /**
   * Handler para mudança de timeframe
   */
  const handleTimeframeChange = (timeframe: '1h' | '6h' | '24h' | '7d' | '30d') => {
    setSelectedTimeframe(timeframe);
    fetchHistorical(timeframe);
  };

  /**
   * Handler para resolver alerta
   */
  const handleResolveAlert = async (alertId: string) => {
    await resolveAlert(alertId);
  };

  /**
   * Renderização de erros
   */
  const renderError = () => {
    const hasErrors = Object.values(error).some(err => err !== null);
    if (!hasErrors) return null;

    return (
      <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <XCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700 font-medium">Erros de carregamento detectados</span>
          </div>
          <button
            onClick={clearErrors}
            className="text-red-600 hover:text-red-800 text-sm underline"
          >
            Limpar erros
          </button>
        </div>
        <div className="mt-2 text-sm text-red-600">
          {Object.entries(error).map(([key, err]) => 
            err && <div key={key}>{key}: {err}</div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Monitoramento e Métricas</h1>
          <p className="text-gray-600 mt-1">Acompanhe o desempenho e saúde do sistema em tempo real</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Controles de refresh */}
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span>Auto-refresh</span>
            </label>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              disabled={!autoRefresh}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value={10000}>10s</option>
              <option value={30000}>30s</option>
              <option value={60000}>1min</option>
              <option value={300000}>5min</option>
            </select>
          </div>
          
          <button
            onClick={fetchAllData}
            disabled={loading.metrics || loading.alerts}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${(loading.metrics || loading.alerts) ? 'animate-spin' : ''}`} />
            <span>Atualizar</span>
          </button>
        </div>
      </div>

      {/* Erros */}
      {renderError()}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Visão Geral', icon: Activity },
            { id: 'alerts', label: 'Alertas', icon: AlertTriangle },
            { id: 'logs', label: 'Logs', icon: Database },
            { id: 'historical', label: 'Histórico', icon: TrendingUp },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
              {id === 'alerts' && alerts && alerts.total_active > 0 && (
                <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                  {alerts.total_active}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Conteúdo das tabs */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Métricas do Sistema */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Métricas do Sistema</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="CPU"
                value={metrics?.system_metrics?.cpu_usage?.toFixed(1) || '0'}
                unit="%"
                icon={<Cpu className="w-5 h-5" />}
                color={(metrics?.system_metrics?.cpu_usage || 0) > 80 ? 'red' : (metrics?.system_metrics?.cpu_usage || 0) > 60 ? 'yellow' : 'green'}
                loading={loading.metrics}
              />
              <MetricCard
                title="Memória"
                value={metrics?.system_metrics?.memory_usage?.toFixed(1) || '0'}
                unit="%"
                icon={<MemoryStick className="w-5 h-5" />}
                color={(metrics?.system_metrics?.memory_usage || 0) > 80 ? 'red' : (metrics?.system_metrics?.memory_usage || 0) > 60 ? 'yellow' : 'green'}
                loading={loading.metrics}
              />
              <MetricCard
                title="Disco"
                value={metrics?.system_metrics?.disk_usage?.toFixed(1) || '0'}
                unit="%"
                icon={<HardDrive className="w-5 h-5" />}
                color={(metrics?.system_metrics?.disk_usage || 0) > 80 ? 'red' : (metrics?.system_metrics?.disk_usage || 0) > 60 ? 'yellow' : 'green'}
                loading={loading.metrics}
              />
              <MetricCard
                title="Load Average"
                value={metrics?.system_metrics?.load_average?.[0]?.toFixed(2) || '0'}
                icon={<Activity className="w-5 h-5" />}
                color="blue"
                loading={loading.metrics}
              />
            </div>
          </div>

          {/* Métricas da Aplicação */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Métricas da Aplicação</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Conexões Ativas"
                value={metrics?.application_metrics.active_connections || 0}
                icon={<Users className="w-5 h-5" />}
                color="blue"
                loading={loading.metrics}
              />
              <MetricCard
                title="Fila de Requisições"
                value={metrics?.application_metrics?.request_queue_size || 0}
                icon={<Clock className="w-5 h-5" />}
                color={(metrics?.application_metrics?.request_queue_size || 0) > 10 ? 'yellow' : 'green'}
                loading={loading.metrics}
              />
              <MetricCard
                title="Cache Hit Rate"
                value={metrics?.application_metrics?.cache_hit_rate?.toFixed(1) || '0'}
                unit="%"
                icon={<Zap className="w-5 h-5" />}
                color={(metrics?.application_metrics?.cache_hit_rate || 0) > 80 ? 'green' : (metrics?.application_metrics?.cache_hit_rate || 0) > 60 ? 'yellow' : 'red'}
                loading={loading.metrics}
              />
              <MetricCard
                title="Tempo de Resposta"
                value={metrics?.application_metrics?.response_time_avg?.toFixed(0) || '0'}
                unit="ms"
                icon={<Network className="w-5 h-5" />}
                color={(metrics?.application_metrics?.response_time_avg || 0) > 1000 ? 'red' : (metrics?.application_metrics?.response_time_avg || 0) > 500 ? 'yellow' : 'green'}
                loading={loading.metrics}
              />
            </div>
          </div>

          {/* Métricas de Auditoria */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Métricas de Auditoria</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Auditorias Ativas"
                value={realtimeStats?.active_audits || 0}
                icon={<Activity className="w-5 h-5" />}
                color="purple"
                loading={loading.realtimeStats}
              />
              <MetricCard
                title="Fila de Auditorias"
                value={realtimeStats?.queue_size || 0}
                icon={<Clock className="w-5 h-5" />}
                color={(realtimeStats?.queue_size || 0) > 5 ? 'yellow' : 'green'}
                loading={loading.realtimeStats}
              />
              <MetricCard
                title="Concluídas Hoje"
                value={realtimeStats?.completed_today || 0}
                icon={<CheckCircle className="w-5 h-5" />}
                color="green"
                loading={loading.realtimeStats}
              />
              <MetricCard
                title="Duração Média"
                value={realtimeStats?.average_duration?.toFixed(0) || '0'}
                unit="min"
                icon={<Clock className="w-5 h-5" />}
                color="blue"
                loading={loading.realtimeStats}
              />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Alertas do Sistema</h2>
            <div className="text-sm text-gray-600">
              {alerts && (
                <>
                  {alerts.total_active} ativos • {alerts.total_resolved} resolvidos
                </>
              )}
            </div>
          </div>
          
          {loading.alerts ? (
            <div className="flex items-center justify-center py-8">
              <Spinner />
              <span className="ml-2">Carregando alertas...</span>
            </div>
          ) : alerts && alerts.alerts.length > 0 ? (
            <div className="space-y-3">
              {alerts.alerts.map((alert) => (
                <AlertItem
                  key={alert.id}
                  alert={alert}
                  onResolve={handleResolveAlert}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
              <p>Nenhum alerta ativo no momento</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Logs do Sistema</h2>
          
          {loading.logs ? (
            <div className="flex items-center justify-center py-8">
              <Spinner />
              <span className="ml-2">Carregando logs...</span>
            </div>
          ) : logs && logs.logs.length > 0 ? (
            <div className="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
              <div className="space-y-1 font-mono text-sm">
                {logs.logs.map((log, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <span className="text-gray-400 text-xs whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleTimeString('pt-BR')}
                    </span>
                    <span className={`text-xs font-bold ${
                      log.level === 'ERROR' ? 'text-red-400' :
                      log.level === 'WARNING' ? 'text-yellow-400' :
                      log.level === 'INFO' ? 'text-blue-400' :
                      'text-gray-400'
                    }`}>
                      {log.level}
                    </span>
                    <span className="text-gray-300 flex-1">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Database className="w-12 h-12 mx-auto mb-4" />
              <p>Nenhum log disponível</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'historical' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Dados Históricos</h2>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Período:</span>
              <select
                value={selectedTimeframe}
                onChange={(e) => handleTimeframeChange(e.target.value as any)}
                className="border border-gray-300 rounded px-3 py-1 text-sm"
              >
                <option value="1h">Última hora</option>
                <option value="6h">Últimas 6 horas</option>
                <option value="24h">Últimas 24 horas</option>
                <option value="7d">Últimos 7 dias</option>
                <option value="30d">Últimos 30 dias</option>
              </select>
            </div>
          </div>
          
          {loading.historical ? (
            <div className="flex items-center justify-center py-8">
              <Spinner />
              <span className="ml-2">Carregando dados históricos...</span>
            </div>
          ) : historical && historical.data_points.length > 0 ? (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <p className="text-center text-gray-600">
                Gráficos históricos serão implementados em uma versão futura.
              </p>
              <div className="mt-4 text-sm text-gray-500">
                <p>Dados disponíveis: {historical.data_points.length} pontos</p>
                <p>Período: {historical.timeframe}</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <TrendingUp className="w-12 h-12 mx-auto mb-4" />
              <p>Nenhum dado histórico disponível</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};