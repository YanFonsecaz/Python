import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  Activity,
  Plus,
  FileText,
  Eye,
  Globe,
  Calendar
} from 'lucide-react';
import type { DashboardStats, Audit } from '../types';
import { useAuditStore } from '../store/auditStore';
import { useNotificationStore } from '../store/notificationStore';
import { ApiService } from '../services/api';
import { Spinner } from '../components';

export function Dashboard() {
  const { setAudits, setLoading, loading } = useAuditStore();
  const { addNotification } = useNotificationStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentAudits, setRecentAudits] = useState<Audit[]>([]);

  // Carrega dados do dashboard
  useEffect(() => {
    loadDashboardData();
  }, []);

  /**
   * Carrega estatísticas e auditorias recentes
   */
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Carrega estatísticas
      const statsResponse = await ApiService.getStats();
      
      // Converte StatsResponse para DashboardStats
      const dashboardStats: DashboardStats = {
        total_audits: statsResponse.total_audits,
        completed_audits: statsResponse.completed_audits,
        running_audits: 0, // Não disponível na API atual
        failed_audits: statsResponse.failed_audits,
        audits_today: 0, // Não disponível na API atual
        critical_issues: 0, // Não disponível na API atual
        average_score: statsResponse.average_score,
        recent_audits: statsResponse.recent_audits
      };
      
      setStats(dashboardStats);

      // Carrega auditorias recentes
      const auditsResponse = await ApiService.listAudits(1, 5);
      setRecentAudits(auditsResponse.audits);
      setAudits(auditsResponse.audits);
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Erro ao carregar dados do dashboard'
      });
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Formata data para exibição
   */
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  /**
   * Retorna cor baseada no status da auditoria
   */
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case 'running':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case 'failed':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  /**
   * Traduz status para português
   */
  const translateStatus = (status: string) => {
    const translations: Record<string, string> = {
      'completed': 'Concluída',
      'running': 'Em execução',
      'failed': 'Falhou',
      'pending': 'Pendente',
      'cancelled': 'Cancelada'
    };
    return translations[status] || status;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-accent-500 bg-clip-text text-transparent font-poppins">
            Dashboard
          </h1>
          <p className="text-text-secondary text-lg font-inter">
            Visão geral das suas auditorias SEO
          </p>
        </div>
        <Link
          to="/audit/new"
          className="btn-primary flex items-center gap-2 transform hover:scale-105 transition-all duration-300 shadow-glow"
        >
          <Plus className="w-5 h-5" />
          Nova Auditoria
        </Link>
      </div>

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card hover:shadow-glow transition-all duration-300 transform hover:scale-105 border border-glass-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-text-secondary font-inter">
                Total de Auditorias
              </p>
              <p className="text-3xl font-bold text-text-primary font-poppins">
                {stats?.total_audits || 0}
              </p>
            </div>
            <div className="p-4 bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/30 rounded-xl shadow-md">
              <Activity className="w-7 h-7 text-primary-600 dark:text-primary-400" />
            </div>
          </div>
        </div>

        <div className="glass-card hover:shadow-glow transition-all duration-300 transform hover:scale-105 border border-glass-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-text-secondary font-inter">
                Concluídas
              </p>
              <p className="text-3xl font-bold text-text-primary font-poppins">
                {stats?.completed_audits || 0}
              </p>
            </div>
            <div className="p-4 bg-gradient-to-br from-success-100 to-success-200 dark:from-success-900/30 dark:to-success-800/30 rounded-xl shadow-md">
              <CheckCircle className="w-7 h-7 text-success-600 dark:text-success-400" />
            </div>
          </div>
        </div>

        <div className="glass-card hover:shadow-glow transition-all duration-300 transform hover:scale-105 border border-glass-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-text-secondary font-inter">
                Em Execução
              </p>
              <p className="text-3xl font-bold text-text-primary font-poppins">
                {stats?.running_audits || 0}
              </p>
            </div>
            <div className="p-4 bg-gradient-to-br from-warning-100 to-warning-200 dark:from-warning-900/30 dark:to-warning-800/30 rounded-xl shadow-md">
              <Clock className="w-7 h-7 text-warning-600 dark:text-warning-400" />
            </div>
          </div>
        </div>

        <div className="glass-card hover:shadow-glow transition-all duration-300 transform hover:scale-105 border border-glass-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-text-secondary font-inter">
                Com Problemas
              </p>
              <p className="text-3xl font-bold text-text-primary font-poppins">
                {stats?.failed_audits || 0}
              </p>
            </div>
            <div className="p-4 bg-gradient-to-br from-error-100 to-error-200 dark:from-error-900/30 dark:to-error-800/30 rounded-xl shadow-md">
              <AlertTriangle className="w-7 h-7 text-error-600 dark:text-error-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Auditorias Recentes */}
      <div className="glass-card border border-glass-border">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-text-primary font-poppins">
            Auditorias Recentes
          </h2>
          <Link
            to="/audit/history"
            className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium font-inter transition-colors duration-200 hover:underline"
          >
            Ver todas
          </Link>
        </div>

        {recentAudits.length === 0 ? (
          <div className="text-center py-12">
            <div className="relative mb-6">
              <FileText className="w-16 h-16 text-text-muted mx-auto" />
              <div className="absolute inset-0 bg-gradient-to-r from-primary-400/20 to-accent-400/20 rounded-full blur-xl"></div>
            </div>
            <p className="text-text-secondary text-lg font-inter mb-6">
              Nenhuma auditoria encontrada
            </p>
            <Link
              to="/audit/new"
              className="btn-primary inline-flex items-center gap-2 transform hover:scale-105 transition-all duration-300"
            >
              <Plus className="w-5 h-5" />
              Criar primeira auditoria
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {recentAudits.map((audit) => (
              <div key={audit.audit_id || audit.id} className="glass-card hover:shadow-glow transition-all duration-300 border border-glass-border">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <Globe className="w-4 h-4 text-text-secondary flex-shrink-0" />
                      <p className="text-sm font-medium text-text-primary truncate font-inter">
                         {audit.url || 'URL não disponível'}
                       </p>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-text-secondary">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(audit.created_at)}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(audit.status)}`}>
                        {translateStatus(audit.status)}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {audit.status === 'completed' && (
                      <Link
                        to={`/audit/result/${audit.audit_id || audit.id}`}
                        className="btn-secondary-sm flex items-center gap-1 text-xs"
                      >
                        <Eye className="w-3 h-3" />
                        Ver Resultado
                      </Link>
                    )}
                    {audit.status === 'running' && (
                      <Link
                        to={`/audit/progress/${audit.audit_id || audit.id}`}
                        className="btn-primary-sm flex items-center gap-1 text-xs"
                      >
                        <Clock className="w-3 h-3" />
                        Acompanhar
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Ações Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/audit/new" className="glass-card hover:shadow-glow transition-all duration-300 transform hover:scale-105 border border-glass-border group">
          <div className="text-center">
            <div className="p-4 bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/30 rounded-xl w-fit mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
              <Plus className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="font-semibold text-text-primary mb-2 font-poppins group-hover:text-primary-600 transition-colors duration-200">
              Nova Auditoria
            </h3>
            <p className="text-sm text-text-secondary font-inter">
              Inicie uma nova auditoria SEO
            </p>
          </div>
        </Link>

        <Link to="/audit/active" className="glass-card hover:shadow-glow transition-all duration-300 transform hover:scale-105 border border-glass-border group">
          <div className="text-center">
            <div className="p-4 bg-gradient-to-br from-warning-100 to-warning-200 dark:from-warning-900/30 dark:to-warning-800/30 rounded-xl w-fit mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
              <Activity className="w-8 h-8 text-warning-600 dark:text-warning-400" />
            </div>
            <h3 className="font-semibold text-text-primary mb-2 font-poppins group-hover:text-warning-600 transition-colors duration-200">
              Auditorias Ativas
            </h3>
            <p className="text-sm text-text-secondary font-inter">
              Acompanhe auditorias em execução
            </p>
          </div>
        </Link>

        <Link to="/reports" className="glass-card hover:shadow-glow transition-all duration-300 transform hover:scale-105 border border-glass-border group">
          <div className="text-center">
            <div className="p-4 bg-gradient-to-br from-success-100 to-success-200 dark:from-success-900/30 dark:to-success-800/30 rounded-xl w-fit mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
              <TrendingUp className="w-8 h-8 text-success-600 dark:text-success-400" />
            </div>
            <h3 className="font-semibold text-text-primary mb-2 font-poppins group-hover:text-success-600 transition-colors duration-200">
              Relatórios
            </h3>
            <p className="text-sm text-text-secondary font-inter">
              Visualize relatórios e métricas
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
}