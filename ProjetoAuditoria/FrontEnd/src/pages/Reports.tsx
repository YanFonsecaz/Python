import { useState, useEffect } from 'react';
import { FileText, Download, Filter, BarChart3, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { Spinner } from '../components';
import { useNotificationStore } from '../store/notificationStore';
import { ApiService } from '../services/api';
import type { AuditType, AuditStatus } from '../types';

interface ReportFilter {
  dateFrom: string;
  dateTo: string;
  auditType: AuditType | 'all';
  status: AuditStatus | 'all';
}

interface ConsolidatedReport {
  report_type: string;
  generated_at: string;
  summary: {
    total_audits_analyzed: number;
    average_score: number;
    score_range: {
      min: number;
      max: number;
      median: number;
    };
    total_issues_found: number;
    most_common_issues: Array<{
      issue_type: string;
      count: number;
      percentage: number;
    }>;
    audit_success_rate: number;
    data_completeness: number;
  };
  metrics: {
    average_score: number;
    min_score: number;
    max_score: number;
    median_score: number;
    score_std_dev: number;
    total_issues: number;
  };
  insights: Array<{
    type: string;
    title: string;
    description: string;
    severity: 'critical' | 'warning' | 'info';
    recommendations: string[];
  }>;
  trends: {
    score_trends: any[];
    improvement_opportunities: Array<{
      issue_type: string;
      impact_level: string;
      affected_percentage: number;
      estimated_improvement: number;
      priority: string;
    }>;
    performance_patterns: any;
  };
  recommendations: Array<{
    category: string;
    priority: string;
    title: string;
    description: string;
    estimated_impact: string;
    effort_level: string;
  }>;
}

/**
 * Página de relatórios - permite visualizar e baixar relatórios consolidados
 */
export function Reports() {
  const { addNotification } = useNotificationStore();
  
  const [loading, setLoading] = useState(false);
  const [consolidatedReport, setConsolidatedReport] = useState<ConsolidatedReport | null>(null);
  const [filters, setFilters] = useState<ReportFilter>({
    dateFrom: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    dateTo: new Date().toISOString().split('T')[0],
    auditType: 'all',
    status: 'all'
  });

  /**
   * Carrega os dados dos relatórios consolidados da API
   */
  const loadConsolidatedReport = async () => {
    // Evita múltiplas chamadas simultâneas
    if (loading) return;
    
    setLoading(true);
    try {
      const params = {
        start_date: filters.dateFrom,
        end_date: filters.dateTo,
        ...(filters.auditType !== 'all' && { audit_type: filters.auditType }),
        ...(filters.status !== 'all' && { status: filters.status }),
        limit: 100
      };

      const report = await ApiService.getConsolidatedReport(params);
      setConsolidatedReport(report);

      addNotification({
        type: 'success',
        title: 'Sucesso',
        message: 'Relatório consolidado carregado com sucesso!'
      });
    } catch (error) {
      console.error('Erro ao carregar relatório consolidado:', error);
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Erro ao carregar relatório consolidado. Verifique se há auditorias no período selecionado.'
      });
      
      // Fallback para dados simulados em caso de erro
      setConsolidatedReport(null);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Faz download do relatório consolidado
   */
  const downloadConsolidatedReport = async () => {
    if (!consolidatedReport) {
      addNotification({
        type: 'warning',
        title: 'Aviso',
        message: 'Nenhum relatório disponível para download'
      });
      return;
    }

    setLoading(true);
    try {
      // Gera arquivo JSON do relatório
      const reportData = JSON.stringify(consolidatedReport, null, 2);
      const blob = new Blob([reportData], { type: 'application/json' });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `relatorio_consolidado_${filters.dateFrom}_${filters.dateTo}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      addNotification({
        type: 'success',
        title: 'Download',
        message: 'Relatório baixado com sucesso!'
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Erro ao baixar relatório consolidado'
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Atualiza filtros
   */
  const updateFilter = (key: keyof ReportFilter, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  /**
   * Aplica filtros e recarrega dados
   */
  const applyFilters = () => {
    // Evita múltiplas chamadas simultâneas
    if (loading) return;
    loadConsolidatedReport();
  };

  /**
   * Obtém ícone baseado na severidade
   */
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default:
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
    }
  };

  /**
   * Obtém cor baseada na prioridade
   */
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      default:
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    }
  };

  useEffect(() => {
    loadConsolidatedReport();
  }, []);

  if (loading && !consolidatedReport) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Relatórios Consolidados
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Visualize e baixe relatórios consolidados das auditorias SEO
          </p>
        </div>
        
        <button
          onClick={downloadConsolidatedReport}
          disabled={loading || !consolidatedReport}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          {loading ? 'Carregando...' : 'Baixar Relatório'}
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Filtros de Período e Tipo
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Inicial
            </label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => updateFilter('dateFrom', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data Final
            </label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => updateFilter('dateTo', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tipo de Auditoria
            </label>
            <select
              value={filters.auditType}
              onChange={(e) => updateFilter('auditType', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">Todos</option>
              <option value="complete">Completa</option>
              <option value="basic">Básica</option>
              <option value="technical">Técnica</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => updateFilter('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">Todos</option>
              <option value="completed">Concluída</option>
              <option value="running">Em Execução</option>
              <option value="failed">Falhou</option>
            </select>
          </div>
        </div>
        
        <div className="flex justify-end mt-4">
          <button
            onClick={applyFilters}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            <Filter className="w-4 h-4" />
            {loading ? 'Carregando...' : 'Aplicar Filtros'}
          </button>
        </div>
      </div>

      {/* Resumo Executivo */}
      {consolidatedReport && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total de Auditorias
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {consolidatedReport.summary.total_audits_analyzed}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Pontuação Média
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {consolidatedReport.summary.average_score.toFixed(1)}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Taxa de Sucesso
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {consolidatedReport.summary.audit_success_rate.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total de Problemas
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {consolidatedReport.summary.total_issues_found}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Principais Problemas */}
      {consolidatedReport && consolidatedReport.summary.most_common_issues.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Principais Problemas Identificados
          </h2>
          
          <div className="space-y-3">
            {consolidatedReport.summary.most_common_issues.slice(0, 5).map((issue, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="flex items-center justify-center w-8 h-8 bg-red-100 text-red-600 rounded-full text-sm font-bold">
                    {index + 1}
                  </span>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {issue.issue_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {issue.count} ocorrências ({issue.percentage.toFixed(1)}% das auditorias)
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-red-600 h-2 rounded-full" 
                      style={{ width: `${Math.min(issue.percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insights Consolidados */}
      {consolidatedReport && consolidatedReport.insights.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Insights e Análises
          </h2>
          
          <div className="space-y-4">
            {consolidatedReport.insights.map((insight, index) => (
              <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  {getSeverityIcon(insight.severity)}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                      {insight.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-3">
                      {insight.description}
                    </p>
                    {insight.recommendations.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                          Recomendações:
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                          {insight.recommendations.map((rec, recIndex) => (
                            <li key={recIndex}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Oportunidades de Melhoria */}
      {consolidatedReport && consolidatedReport.trends.improvement_opportunities.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Oportunidades de Melhoria
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {consolidatedReport.trends.improvement_opportunities.slice(0, 6).map((opportunity, index) => (
              <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {opportunity.issue_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(opportunity.priority)}`}>
                    {opportunity.priority}
                  </span>
                </div>
                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <p>Impacto: <span className="font-medium">{opportunity.impact_level}</span></p>
                  <p>Afeta: <span className="font-medium">{opportunity.affected_percentage.toFixed(1)}%</span> das auditorias</p>
                  <p>Melhoria estimada: <span className="font-medium text-green-600">+{opportunity.estimated_improvement.toFixed(1)} pontos</span></p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recomendações */}
      {consolidatedReport && consolidatedReport.recommendations.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recomendações Prioritárias
          </h2>
          
          <div className="space-y-4">
            {consolidatedReport.recommendations.slice(0, 5).map((recommendation, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {recommendation.title}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(recommendation.priority)}`}>
                    {recommendation.priority}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-2">
                  {recommendation.description}
                </p>
                <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                  <span>Impacto: <span className="font-medium">{recommendation.estimated_impact}</span></span>
                  <span>Esforço: <span className="font-medium">{recommendation.effort_level}</span></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Estado vazio */}
      {!loading && !consolidatedReport && (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Nenhum relatório disponível
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Não há auditorias no período selecionado ou ocorreu um erro ao carregar os dados.
          </p>
          <button
            onClick={loadConsolidatedReport}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Tentar Novamente
          </button>
        </div>
      )}
    </div>
  );
}