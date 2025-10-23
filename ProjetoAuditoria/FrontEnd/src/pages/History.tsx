import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Trash2, 
  Calendar,
  Globe,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  RefreshCw
} from 'lucide-react';
import { useAuditStore } from '../store/auditStore';
import { useNotifications } from '../store/notificationStore';
import { Spinner, ExportButton } from '../components';
import ApiService from '../services/api';
import type { AuditFilters, PaginationParams } from '../types';

/**
 * Página de histórico de auditorias
 * Lista todas as auditorias com filtros e paginação
 */
export const History: React.FC = () => {
  const navigate = useNavigate();
  const { audits, setAudits, setError } = useAuditStore();
  const { showSuccess, showError, showWarning } = useNotifications();
  
  const [localLoading, setLocalLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<AuditFilters>({});
  const [pagination, setPagination] = useState<PaginationParams>({
    page: 1,
    limit: 10
  });
  const [totalPages, setTotalPages] = useState(1);
  const [totalAudits, setTotalAudits] = useState(0);
  const [selectedAudits, setSelectedAudits] = useState<string[]>([]);
  const [deletingAudits, setDeletingAudits] = useState<string[]>([]);

  /**
   * Carrega a lista de auditorias
   */
  const loadAudits = useCallback(async () => {
    setLocalLoading(true);
    setError(null);

    try {
      const response = await ApiService.listAudits(
        pagination.page, 
        pagination.limit, 
        filters.status, 
        filters.audit_type
      );

      setAudits(response.audits);
      setTotalPages(response.total_pages);
      setTotalAudits(response.total);
    } catch (err) {
      const errorMessage = 'Erro de conexão ao carregar auditorias';
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLocalLoading(false);
    }
  }, [filters, searchTerm, pagination, setAudits, setError, showError]);

  /**
   * Aplica filtros de busca
   */
  const handleSearch = useCallback(() => {
    setPagination(prev => ({ ...prev, page: 1 }));
    loadAudits();
  }, [loadAudits]);

  /**
   * Limpa todos os filtros
   */
  const clearFilters = () => {
    setSearchTerm('');
    setFilters({});
    setPagination({ page: 1, limit: 10 });
  };

  /**
   * Navega para os resultados de uma auditoria
   */
  const viewResults = (auditId: string) => {
    navigate(`/results/${auditId}`);
  };

  /**
   * Faz download do relatório de uma auditoria
   */
  const downloadReport = async (auditId: string) => {
    try {
      const response = await ApiService.downloadReport(auditId, 'docx');
      if (response instanceof Blob) {
        const url = window.URL.createObjectURL(response);
        const link = document.createElement('a');
        link.href = url;
        link.download = `auditoria-${auditId}-relatorio.docx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showSuccess('Relatório baixado com sucesso!');
      } else {
        showError('Erro ao baixar relatório');
      }
    } catch (err) {
      showError('Erro de conexão ao baixar relatório');
    }
  };

  /**
   * Exclui uma auditoria
   */
  const deleteAudit = async (auditId: string) => {
    if (!confirm('Tem certeza que deseja excluir esta auditoria? Esta ação não pode ser desfeita.')) {
      return;
    }

    setDeletingAudits(prev => [...prev, auditId]);
    try {
      await ApiService.deleteAudit(auditId);
      showSuccess('Auditoria excluída com sucesso!');
      loadAudits(); // Recarrega a lista
    } catch (err) {
      showError('Erro ao excluir auditoria');
    } finally {
      setDeletingAudits(prev => prev.filter(id => id !== auditId));
    }
  };

  /**
   * Exclui múltiplas auditorias selecionadas
   */
  const deleteSelectedAudits = async () => {
    if (selectedAudits.length === 0) return;

    if (!confirm(`Tem certeza que deseja excluir ${selectedAudits.length} auditoria(s)? Esta ação não pode ser desfeita.`)) {
      return;
    }

    setDeletingAudits(selectedAudits);
    try {
      const promises = selectedAudits.map(id => ApiService.deleteAudit(id));
      const results = await Promise.allSettled(promises);
      
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.length - successful;

      if (successful > 0) {
        showSuccess(`${successful} auditoria(s) excluída(s) com sucesso!`);
      }
      if (failed > 0) {
        showWarning(`${failed} auditoria(s) não puderam ser excluídas.`);
      }

      setSelectedAudits([]);
      loadAudits(); // Recarrega a lista
    } catch (err) {
      showError('Erro ao excluir auditorias');
    } finally {
      setDeletingAudits([]);
    }
  };

  /**
   * Seleciona/deseleciona uma auditoria
   */
  const toggleAuditSelection = (auditId: string) => {
    setSelectedAudits(prev => 
      prev.includes(auditId) 
        ? prev.filter(id => id !== auditId)
        : [...prev, auditId]
    );
  };

  /**
   * Seleciona/deseleciona todas as auditorias
   */
  const toggleAllSelection = () => {
    if (selectedAudits.length === audits.length) {
      setSelectedAudits([]);
    } else {
      setSelectedAudits(audits.map(audit => audit.id));
    }
  };

  /**
   * Formata a data para exibição
   */
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  /**
   * Retorna o ícone e cor baseado no status
   */
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return { icon: CheckCircle, color: 'text-green-500' };
      case 'failed':
        return { icon: XCircle, color: 'text-red-500' };
      case 'running':
      case 'in_progress':
        return { icon: Clock, color: 'text-blue-500' };
      case 'cancelled':
        return { icon: AlertTriangle, color: 'text-yellow-500' };
      default:
        return { icon: Clock, color: 'text-gray-500' };
    }
  };

  /**
   * Traduz o status para português
   */
  const translateStatus = (status: string) => {
    const translations: Record<string, string> = {
      'pending': 'Pendente',
      'starting': 'Iniciando',
      'running': 'Em Execução',
      'in_progress': 'Em Progresso',
      'completed': 'Concluída',
      'failed': 'Falhou',
      'cancelled': 'Cancelada'
    };
    return translations[status] || status;
  };

  /**
   * Traduz o tipo de auditoria para português
   */
  const translateAuditType = (type: string) => {
    const translations: Record<string, string> = {
      'complete': 'Completa',
      'basic': 'Básica',
      'technical': 'Técnica'
    };
    return translations[type] || type;
  };

  useEffect(() => {
    loadAudits();
  }, [loadAudits]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="glass-card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 via-secondary-500 to-accent-500 bg-clip-text text-transparent font-poppins">
              Histórico de Auditorias
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mt-2 font-inter">
              {totalAudits} auditoria(s) encontrada(s)
            </p>
          </div>
          
          <div className="flex gap-3">
            {selectedAudits.length > 0 && (
              <button
                onClick={deleteSelectedAudits}
                disabled={deletingAudits.length > 0}
                className="btn-danger flex items-center gap-2 text-lg px-6 py-3 shadow-glow hover:shadow-red-500/50 transform hover:scale-105 transition-all duration-300"
              >
                {deletingAudits.length > 0 ? (
                  <Spinner size="sm" />
                ) : (
                  <Trash2 className="w-5 h-5" />
                )}
                <span className="font-poppins">
                  Excluir Selecionadas ({selectedAudits.length})
                </span>
              </button>
            )}
            
            <button
              onClick={loadAudits}
              disabled={localLoading}
              className="btn-secondary flex items-center gap-2 text-lg px-6 py-3 hover:shadow-glow transition-all duration-300"
            >
              <RefreshCw className={`w-5 h-5 ${localLoading ? 'animate-spin' : ''}`} />
              <span className="font-poppins">Atualizar</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filtros e Busca */}
      <div className="glass-card">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Busca */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por URL..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="input pl-12 text-lg py-4 font-inter bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border-gray-200/50 dark:border-gray-700/50 focus:border-primary-500 focus:ring-primary-500/20 transition-all duration-300"
              />
            </div>
          </div>
          
          {/* Botões */}
          <div className="flex gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn-secondary flex items-center gap-2 text-lg px-6 py-4 transition-all duration-300 ${
                showFilters ? 'bg-primary-500 text-white shadow-glow' : 'hover:shadow-glow'
              }`}
            >
              <Filter className="w-5 h-5" />
              <span className="font-poppins">Filtros</span>
            </button>
            <button
              onClick={handleSearch}
              className="btn-primary text-lg px-8 py-4 shadow-glow hover:shadow-primary-500/50 transform hover:scale-105 transition-all duration-300"
            >
              <span className="font-poppins">Buscar</span>
            </button>
          </div>
        </div>

        {/* Filtros Expandidos */}
        {showFilters && (
          <div className="mt-6 pt-6 border-t border-gray-200/30 dark:border-gray-700/30">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2 font-poppins">
                  Status
                </label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters(prev => ({ 
                    ...prev, 
                    status: e.target.value as any || undefined 
                  }))}
                  className="input text-lg py-3 font-inter bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border-gray-200/50 dark:border-gray-700/50 focus:border-primary-500 focus:ring-primary-500/20 transition-all duration-300"
                >
                  <option value="">Todos</option>
                  <option value="completed">Concluída</option>
                  <option value="running">Em Execução</option>
                  <option value="failed">Falhou</option>
                  <option value="cancelled">Cancelada</option>
                </select>
              </div>
              
              <div>
                <label className="block text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2 font-poppins">
                  Tipo
                </label>
                <select
                  value={filters.audit_type || ''}
                  onChange={(e) => setFilters(prev => ({ 
                    ...prev, 
                    audit_type: e.target.value as any || undefined 
                  }))}
                  className="input text-lg py-3 font-inter bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border-gray-200/50 dark:border-gray-700/50 focus:border-primary-500 focus:ring-primary-500/20 transition-all duration-300"
                >
                  <option value="">Todos</option>
                  <option value="complete">Completa</option>
                  <option value="basic">Básica</option>
                  <option value="technical">Técnica</option>
                </select>
              </div>
              
              <div>
                <label className="block text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2 font-poppins">
                  Data (De)
                </label>
                <input
                  type="date"
                  value={filters.date_from || ''}
                  onChange={(e) => setFilters(prev => ({ 
                    ...prev, 
                    date_from: e.target.value || undefined 
                  }))}
                  className="input text-lg py-3 font-inter bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border-gray-200/50 dark:border-gray-700/50 focus:border-primary-500 focus:ring-primary-500/20 transition-all duration-300"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={clearFilters}
                className="btn-secondary text-lg px-6 py-3 hover:shadow-glow transition-all duration-300"
              >
                <span className="font-poppins">Limpar Filtros</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Lista de Auditorias */}
      {localLoading ? (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-glow">
            <Spinner size="lg" />
          </div>
          <p className="text-xl font-semibold text-gray-600 dark:text-gray-300 font-inter">
            Carregando auditorias...
          </p>
        </div>
      ) : audits.length === 0 ? (
        <div className="glass-card text-center py-16">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center mx-auto mb-6 shadow-glow">
            <Globe className="w-10 h-10 text-white" />
          </div>
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4 font-poppins">
            Nenhuma auditoria encontrada
          </h3>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 font-inter max-w-2xl mx-auto">
            Não há auditorias que correspondam aos filtros aplicados.
          </p>
          <button
            onClick={() => navigate('/new-audit')}
            className="btn-primary text-lg px-8 py-4 shadow-glow hover:shadow-primary-500/50 transform hover:scale-105 transition-all duration-300"
          >
            <span className="font-poppins">Criar Nova Auditoria</span>
          </button>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          {/* Header da Tabela */}
          <div className="px-8 py-4 bg-gradient-to-r from-gray-50/80 to-gray-100/80 dark:from-gray-700/80 dark:to-gray-800/80 backdrop-blur-sm border-b border-gray-200/30 dark:border-gray-600/30">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={selectedAudits.length === audits.length && audits.length > 0}
                onChange={toggleAllSelection}
                className="mr-4 w-5 h-5 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span className="text-lg font-semibold text-gray-700 dark:text-gray-300 font-poppins">
                Selecionar Todas
              </span>
            </div>
          </div>

          {/* Lista */}
          <div className="divide-y divide-gray-200/30 dark:divide-gray-700/30">
            {audits.map((audit) => {
              const { icon: StatusIcon, color } = getStatusIcon(audit.status);
              const isDeleting = deletingAudits.includes(audit.id);
              
              return (
                <div key={audit.id} className="p-8 hover:bg-gradient-to-r hover:from-primary-50/30 hover:to-secondary-50/30 dark:hover:from-primary-900/10 dark:hover:to-secondary-900/10 transition-all duration-300 group">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6 flex-1">
                      <input
                        type="checkbox"
                        checked={selectedAudits.includes(audit.id)}
                        onChange={() => toggleAuditSelection(audit.id)}
                        className="flex-shrink-0 w-5 h-5 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                      />
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate font-poppins group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-300">
                            {audit.url}
                          </h3>
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-semibold bg-gradient-to-r from-primary-100 to-secondary-100 dark:from-primary-900/30 dark:to-secondary-900/30 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-700 font-inter">
                            {translateAuditType(audit.audit_type)}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-6 text-base text-gray-600 dark:text-gray-400 font-inter">
                          <div className="flex items-center gap-2">
                            <StatusIcon className={`w-5 h-5 ${color}`} />
                            <span className="font-medium">{translateStatus(audit.status)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="w-5 h-5" />
                            <span>{formatDate(audit.created_at)}</span>
                          </div>
                          {audit.progress > 0 && audit.status === 'running' && (
                            <div className="flex items-center gap-2">
                              <Clock className="w-5 h-5 text-blue-500" />
                              <div className="flex items-center gap-2">
                                <div className="w-20 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                                  <div 
                                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300" 
                                    style={{ width: `${audit.progress}%` }}
                                  ></div>
                                </div>
                                <span className="text-sm font-medium">{audit.progress}%</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Ações */}
                    <div className="flex items-center gap-3">
                      {audit.status === 'completed' && (
                        <>
                          <button
                            onClick={() => viewResults(audit.id)}
                            className="btn-secondary-sm flex items-center gap-2 text-base px-4 py-2 hover:shadow-glow transition-all duration-300 transform hover:scale-105"
                          >
                            <Eye className="w-4 h-4" />
                            <span className="font-poppins">Ver Resultados</span>
                          </button>
                          <ExportButton 
                            auditId={audit.id} 
                            className="btn-secondary-sm text-base px-4 py-2 hover:shadow-glow transition-all duration-300 transform hover:scale-105" 
                          />
                          <button
                            onClick={() => downloadReport(audit.id)}
                            className="btn-secondary-sm flex items-center gap-2 text-base px-4 py-2 hover:shadow-glow transition-all duration-300 transform hover:scale-105"
                          >
                            <Download className="w-4 h-4" />
                            <span className="font-poppins">Relatório</span>
                          </button>
                        </>
                      )}
                      
                      <button
                        onClick={() => deleteAudit(audit.id)}
                        disabled={isDeleting}
                        className="btn-danger-sm flex items-center gap-2 text-base px-4 py-2 hover:shadow-glow hover:shadow-red-500/50 transition-all duration-300 transform hover:scale-105"
                      >
                        {isDeleting ? (
                          <Spinner size="sm" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Paginação */}
      {totalPages > 1 && (
        <div className="glass-card">
          <div className="flex items-center justify-between">
            <div className="text-lg text-gray-600 dark:text-gray-300 font-inter">
              Página <span className="font-bold text-primary-600 dark:text-primary-400">{pagination.page}</span> de <span className="font-bold">{totalPages}</span> ({totalAudits} total)
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
                className="btn-secondary-sm flex items-center gap-2 text-base px-4 py-2 hover:shadow-glow transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
                <span className="font-poppins">Anterior</span>
              </button>
              
              <div className="flex items-center gap-2">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const page = i + 1;
                  return (
                    <button
                      key={page}
                      onClick={() => setPagination(prev => ({ ...prev, page }))}
                      className={`px-4 py-2 text-base rounded-xl font-poppins transition-all duration-300 ${
                        pagination.page === page
                          ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-glow transform scale-110'
                          : 'bg-white/50 dark:bg-gray-800/50 text-gray-700 dark:text-gray-300 hover:bg-primary-100 dark:hover:bg-primary-900/30 hover:text-primary-700 dark:hover:text-primary-300 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}
              </div>
              
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page === totalPages}
                className="btn-secondary-sm flex items-center gap-2 text-base px-4 py-2 hover:shadow-glow transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="font-poppins">Próxima</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};