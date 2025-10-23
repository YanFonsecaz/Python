import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  ArrowLeft,
  RefreshCw,
  Eye,
  Download,
  Pause,
  Play,
  X
} from 'lucide-react';
import { useAuditStore } from '../store/auditStore';
import { useNotificationStore } from '../store/notificationStore';
import { usePolling } from '../hooks/usePolling';
import { ApiService } from '../services/api';
import { Spinner } from '../components';
import type { Audit, AuditStatus } from '../types';

/**
 * Página de Progresso da Auditoria - Acompanha auditorias em execução
 */
export function AuditProgress() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { audits, updateAudit, setLoading, loading } = useAuditStore();
  const { addNotification } = useNotificationStore();
  
  const [audit, setAudit] = useState<Audit | null>(null);

  // Hook de polling para auditoria específica (apenas quando há ID)
  const { startPolling, stopPolling, isPolling } = usePolling({
    auditId: id || '',
    enabled: !!id && !!audit,
    onComplete: (completedAudit) => {
      setAudit(completedAudit);
      addNotification({
        type: 'success',
        title: 'Auditoria Concluída',
        message: `A auditoria foi concluída com sucesso!`
      });
    },
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Erro na Auditoria',
        message: error
      });
    }
  });

  // Busca auditoria específica ou lista auditorias ativas
  useEffect(() => {
    if (id) {
      // Página de progresso específica
      loadAuditDetails(id);
      startPolling();
    } else {
      // Página de auditorias ativas - não inicia polling aqui
      loadActiveAudits();
    }

    return () => {
      if (id) {
        stopPolling();
      }
    };
  }, [id]);

  /**
   * Carrega detalhes de uma auditoria específica
   */
  const loadAuditDetails = async (auditId: string) => {
    setLoading(true);
    try {
      const response = await ApiService.getAuditStatus(auditId);
      // Converte AuditStatusResponse para Audit
      const auditData: Audit = {
        id: response.audit_id,
        url: '', // URL não está disponível na resposta de status
        status: response.status,
        progress: response.progress,
        created_at: response.start_time,
        audit_type: 'complete', // Valor padrão
        generate_documentation: false, // Valor padrão
        include_screenshots: false, // Valor padrão
        current_step: response.current_step,
        error_message: response.error
      };
      setAudit(auditData);
      updateAudit(auditData.id, auditData);
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Erro ao carregar detalhes da auditoria'
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Carrega lista de auditorias ativas
   */
  const loadActiveAudits = async () => {
    setLoading(true);
    try {
      const response = await ApiService.listAudits(1, 50);
      // Filtra apenas auditorias ativas
      const activeAudits = response.audits.filter(
        audit => audit.status === 'running' || audit.status === 'in_progress' || audit.status === 'starting'
      );
      
      // Atualiza o store com as auditorias ativas
      activeAudits.forEach(audit => {
        updateAudit(audit.id, audit);
      });
      
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Erro ao carregar auditorias ativas'
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Cancela uma auditoria
   */
  const handleCancelAudit = async (auditId: string) => {
    if (!confirm('Tem certeza que deseja cancelar esta auditoria?')) {
      return;
    }

    try {
      setLoading(true);
      await ApiService.cancelAudit(auditId);
      
      addNotification({
        type: 'success',
        title: 'Auditoria Cancelada',
        message: 'A auditoria foi cancelada com sucesso'
      });
      
      // Para polling se estiver ativo
      if (isPolling) {
        stopPolling();
      }
      
      // Se estamos na página específica da auditoria, navega para o histórico
      if (id === auditId) {
        navigate('/audit/history');
      } else {
        // Se estamos na lista de auditorias ativas, recarrega a lista
        loadActiveAudits();
      }
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Erro ao Cancelar',
        message: error.response?.data?.error || 'Erro ao cancelar auditoria'
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Retorna cor baseada no status
   */
  const getStatusColor = (status: AuditStatus) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case 'running':
      case 'in_progress':
        return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case 'failed':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      case 'cancelled':
        return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
      default:
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
    }
  };

  /**
   * Retorna ícone baseado no status
   */
  const getStatusIcon = (status: AuditStatus) => {
    switch (status) {
      case 'completed':
        return CheckCircle;
      case 'failed':
        return XCircle;
      case 'running':
      case 'in_progress':
        return RefreshCw;
      case 'starting':
        return Clock;
      default:
        return AlertTriangle;
    }
  };

  /**
   * Traduz status para português
   */
  const translateStatus = (status: AuditStatus) => {
    const translations: Record<AuditStatus, string> = {
      'pending': 'Pendente',
      'starting': 'Iniciando',
      'running': 'Em execução',
      'in_progress': 'Em progresso',
      'completed': 'Concluída',
      'failed': 'Falhou',
      'cancelled': 'Cancelada'
    };
    return translations[status] || status;
  };

  /**
   * Formata tempo decorrido
   */
  const formatElapsedTime = (createdAt: string) => {
    const now = new Date();
    const created = new Date(createdAt);
    const diff = now.getTime() - created.getTime();
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    }
    return `${minutes}m`;
  };

  // Renderização para auditoria específica
  if (id && audit) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20">
        <div className="container mx-auto px-4 py-8 space-y-8">
          {/* Header */}
          <div className="glass-card p-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link
                  to="/audit/history"
                  className="btn-secondary flex items-center gap-2 hover:scale-105 transition-transform"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Voltar
                </Link>
                
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Progresso da Auditoria
                  </h1>
                  <p className="text-gray-600 dark:text-gray-300 mt-1 font-medium">
                    {audit.url}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <button
                  onClick={() => loadAuditDetails(audit.id)}
                  className="btn-secondary flex items-center gap-2 hover:scale-105 transition-all duration-200"
                  disabled={loading}
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                  Atualizar
                </button>
                
                <div className="flex items-center gap-2 glass-card px-3 py-2">
                  <span className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                    Polling:
                  </span>
                  <button
                    onClick={isPolling ? stopPolling : startPolling}
                    className={`p-2 rounded-lg transition-all duration-200 hover:scale-110 ${
                      isPolling 
                        ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white shadow-lg shadow-green-500/25' 
                        : 'bg-gradient-to-r from-gray-400 to-gray-500 text-white shadow-lg shadow-gray-500/25'
                    }`}
                  >
                    {isPolling ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Status Card */}
          <div className="glass-card p-8 animate-slide-up">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-6">
                <div className={`p-6 rounded-2xl ${getStatusColor(audit.status)} shadow-lg hover:scale-105 transition-transform duration-200`}>
                  {React.createElement(getStatusIcon(audit.status), { className: "w-10 h-10" })}
                </div>
                
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                    {translateStatus(audit.status)}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300 font-medium">
                    Iniciado há {formatElapsedTime(audit.created_at)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                {audit.status === 'completed' && (
                  <>
                    <Link
                      to={`/audit/result/${audit.id}`}
                      className="btn-primary flex items-center gap-2 hover:scale-105 transition-all duration-200 shadow-lg shadow-blue-500/25"
                    >
                      <Eye className="w-4 h-4" />
                      Ver Resultado
                    </Link>
                    <button className="btn-secondary flex items-center gap-2 hover:scale-105 transition-all duration-200">
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  </>
                )}
                
                {(audit.status === 'running' || audit.status === 'in_progress') && (
                  <button
                    onClick={() => handleCancelAudit(audit.id)}
                    disabled={loading}
                    className="btn-danger flex items-center gap-2 hover:scale-105 transition-all duration-200 shadow-lg shadow-red-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <X className="w-4 h-4" />
                    {loading ? 'Cancelando...' : 'Cancelar'}
                  </button>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            {(audit.status === 'running' || audit.status === 'in_progress') && (
              <div className="space-y-6 animate-pulse-subtle">
                <div className="flex items-center justify-between">
                  <span className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                    Progresso
                  </span>
                  <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {audit.progress || 0}%
                  </span>
                </div>
                <div className="relative">
                  <div className="progress-bar h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                    <div 
                      className="progress-fill h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full transition-all duration-1000 ease-out shadow-lg"
                      style={{ width: `${audit.progress || 0}%` }}
                    />
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
                </div>
                
                {audit.current_step && (
                  <div className="glass-card p-4 animate-fade-in">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      <span className="text-blue-600 dark:text-blue-400 font-semibold">Etapa atual:</span> {audit.current_step}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {audit.status === 'failed' && audit.error_message && (
              <div className="mt-6 p-6 bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 border border-red-200 dark:border-red-800 rounded-2xl shadow-lg animate-shake">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                    <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
                  </div>
                  <h3 className="text-lg font-bold text-red-800 dark:text-red-200">
                    Erro na Auditoria
                  </h3>
                </div>
                <p className="text-red-700 dark:text-red-300 font-medium leading-relaxed">
                  {audit.error_message}
                </p>
              </div>
            )}
          </div>

          {/* Audit Details */}
          <div className="glass-card p-8 animate-slide-up" style={{animationDelay: '0.2s'}}>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-3">
              <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"></div>
              Detalhes da Auditoria
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                <label className="label text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Tipo de Auditoria</label>
                <p className="text-lg font-medium text-gray-900 dark:text-white capitalize bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  {audit.audit_type}
                </p>
              </div>
              
              <div className="space-y-2">
                <label className="label text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Data de Início</label>
                <p className="text-lg font-medium text-gray-900 dark:text-white">
                  {new Date(audit.created_at).toLocaleString('pt-BR')}
                </p>
              </div>
              
              <div className="space-y-2">
                <label className="label text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Documentação</label>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${audit.generate_documentation ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    {audit.generate_documentation ? 'Sim' : 'Não'}
                  </p>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="label text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Screenshots</label>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${audit.include_screenshots ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    {audit.include_screenshots ? 'Sim' : 'Não'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Renderização para auditorias ativas
  const filteredActiveAudits = audits.filter(
    audit => audit.status === 'running' || audit.status === 'in_progress' || audit.status === 'starting'
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20">
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Header */}
        <div className="glass-card p-6 animate-fade-in">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Auditorias Ativas
              </h1>
              <p className="text-gray-600 dark:text-gray-300 mt-1 font-medium">
                Acompanhe o progresso das auditorias em execução
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={loadActiveAudits}
                className="btn-secondary flex items-center gap-2 hover:scale-105 transition-all duration-200"
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Atualizar
              </button>
              
              <Link to="/audit/new" className="btn-primary hover:scale-105 transition-all duration-200 shadow-lg shadow-blue-500/25">
                Nova Auditoria
              </Link>
            </div>
          </div>
        </div>

        {/* Active Audits List */}
        {filteredActiveAudits.length === 0 ? (
          <div className="glass-card text-center py-16 animate-slide-up">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-3xl"></div>
              <Clock className="w-20 h-20 text-gray-400 dark:text-gray-500 mx-auto mb-6 relative z-10" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
              Nenhuma auditoria ativa
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-8 text-lg">
              Não há auditorias em execução no momento
            </p>
            <Link to="/audit/new" className="btn-primary text-lg px-8 py-3 hover:scale-105 transition-all duration-200 shadow-lg shadow-blue-500/25">
              Iniciar Nova Auditoria
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {filteredActiveAudits.map((audit, index) => {
              return (
                <div key={audit.id} className="glass-card p-6 animate-slide-up hover:scale-[1.02] transition-all duration-300" style={{animationDelay: `${index * 0.1}s`}}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6 flex-1">
                      <div className={`p-4 rounded-2xl ${getStatusColor(audit.status)} shadow-lg hover:scale-110 transition-transform duration-200`}>
                        {React.createElement(getStatusIcon(audit.status), { className: "w-8 h-8" })}
                      </div>
                      
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                          {audit.url}
                        </h3>
                        <div className="flex items-center gap-4 mb-4">
                          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(audit.status)} shadow-sm`}>
                            {translateStatus(audit.status)}
                          </span>
                          <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                            {formatElapsedTime(audit.created_at)}
                          </span>
                        </div>
                        
                        {/* Progress Bar */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                              Progresso
                            </span>
                            <span className="text-sm font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                              {audit.progress}%
                            </span>
                          </div>
                          <div className="relative">
                            <div className="progress-bar h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                              <div 
                                className="progress-fill h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-full transition-all duration-1000 ease-out"
                                style={{ width: `${audit.progress}%` }}
                              />
                            </div>
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <Link
                        to={`/audit/progress/${audit.id}`}
                        className="btn-secondary text-sm flex items-center gap-2 hover:scale-105 transition-all duration-200"
                      >
                        <Eye className="w-4 h-4" />
                        Detalhes
                      </Link>
                      
                      {(audit.status === 'running' || audit.status === 'in_progress') && (
                        <button
                          onClick={() => handleCancelAudit(audit.id)}
                          disabled={loading}
                          className="btn-danger text-sm flex items-center gap-2 hover:scale-105 transition-all duration-200 shadow-lg shadow-red-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <X className="w-4 h-4" />
                          {loading ? 'Cancelando...' : 'Cancelar'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}