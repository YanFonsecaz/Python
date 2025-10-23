import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Info, 
  Download, 
  ArrowLeft,
  ExternalLink,
  Clock,
  Globe,
  Smartphone,
  Shield,
  Search,
  Image,
  Link as LinkIcon
} from 'lucide-react';
import { useAuditStore } from '../store/auditStore';
import { useNotifications } from '../store/notificationStore';
import { Spinner, ExportButton } from '../components';
import ApiService from '../services/api';
import type { Audit, AuditResult } from '../types';

/**
 * Página de resultados de auditoria
 * Exibe os resultados detalhados de uma auditoria específica
 */
export const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { audits } = useAuditStore();
  const { showSuccess, showError } = useNotifications();
  
  const [audit, setAudit] = useState<Audit | null>(null);
  const [result, setResult] = useState<AuditResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingReport, setDownloadingReport] = useState(false);

  /**
   * Carrega os dados da auditoria e seus resultados
   */
  const loadAuditData = useCallback(async () => {
    if (!id) {
      setError('ID da auditoria não fornecido');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Primeiro tenta buscar no store local
      const localAudit = audits.find(a => a.id === id);
      if (localAudit) {
        setAudit(localAudit);
      }

      // Busca os resultados da API
      const response = await ApiService.getAuditResult(id);
      setResult(response);
      
      // Se não tinha auditoria local, busca os dados básicos
      if (!localAudit) {
        const statusResponse = await ApiService.getAuditStatus(id);
        // Converte AuditStatusResponse para Audit
        const auditData: Audit = {
          id: statusResponse.audit_id,
          url: '', // URL será preenchida pelo resultado
          status: statusResponse.status,
          progress: statusResponse.progress,
          created_at: statusResponse.start_time,
          audit_type: 'complete', // Valor padrão
          generate_documentation: false,
          include_screenshots: false,
          current_step: statusResponse.current_step,
          error_message: statusResponse.error
        };
        setAudit(auditData);
      }
    } catch (err) {
      const errorMessage = 'Erro de conexão ao carregar resultados';
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [id, audits, showError]);

  /**
   * Faz download do relatório
   */
  const handleDownloadReport = async () => {
    if (!id) return;

    setDownloadingReport(true);
    try {
      const response = await ApiService.downloadReport(id, 'pdf');
      if (response instanceof Blob) {
        // Cria um link temporário para download
        const url = window.URL.createObjectURL(response);
        const link = document.createElement('a');
        link.href = url;
        link.download = `auditoria-${id}-relatorio.pdf`;
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
    } finally {
      setDownloadingReport(false);
    }
  };

  /**
   * Formata a data para exibição
   */
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  /**
   * Retorna o ícone e cor baseado no score
   */
  const getScoreIcon = (score: number) => {
    if (score >= 80) return { icon: CheckCircle, color: 'text-green-500' };
    if (score >= 60) return { icon: AlertTriangle, color: 'text-yellow-500' };
    return { icon: XCircle, color: 'text-red-500' };
  };

  /**
   * Renderiza uma seção de análise
   */
  const renderAnalysisSection = (title: string, analysis: any, icon: React.ElementType) => {
    const Icon = icon;
    
    return (
      <div className="glass-card hover:shadow-glow transition-all duration-300 group">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl shadow-lg group-hover:shadow-primary-500/25 transition-all duration-300">
            <Icon className="w-7 h-7 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white font-poppins">{title}</h3>
        </div>
        
        {analysis && (
          <div className="space-y-6">
            {analysis.score !== undefined && (
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-xl">
                <span className="text-lg font-semibold text-gray-700 dark:text-gray-300 font-inter">Score:</span>
                <div className="flex items-center gap-3">
                  <span className="text-3xl font-bold text-gray-900 dark:text-white font-poppins">
                    {analysis.score}/100
                  </span>
                  {(() => {
                    const { icon: ScoreIcon, color } = getScoreIcon(analysis.score);
                    return <ScoreIcon className={`w-8 h-8 ${color}`} />;
                  })()}
                </div>
              </div>
            )}
            
            {analysis.issues && analysis.issues.length > 0 && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                <h4 className="text-lg font-bold text-red-800 dark:text-red-200 mb-3 font-poppins flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  Problemas Encontrados
                </h4>
                <ul className="space-y-2">
                  {analysis.issues.map((issue: string, index: number) => (
                    <li key={index} className="flex items-start gap-3 text-sm text-red-700 dark:text-red-300 font-inter">
                      <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                      <span className="leading-relaxed">{issue}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {analysis.recommendations && analysis.recommendations.length > 0 && (
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
                <h4 className="text-lg font-bold text-blue-800 dark:text-blue-200 mb-3 font-poppins flex items-center gap-2">
                  <Info className="w-5 h-5" />
                  Recomendações
                </h4>
                <ul className="space-y-2">
                  {analysis.recommendations.map((rec: string, index: number) => (
                    <li key={index} className="flex items-start gap-3 text-sm text-blue-700 dark:text-blue-300 font-inter">
                      <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span className="leading-relaxed">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  useEffect(() => {
    loadAuditData();
  }, [loadAuditData]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-96 space-y-4">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-glow">
          <Spinner size="lg" />
        </div>
        <p className="text-xl font-semibold text-gray-600 dark:text-gray-300 font-inter">
          Carregando resultados...
        </p>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="glass-card text-center py-16">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center mx-auto mb-6 shadow-glow">
            <XCircle className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4 font-poppins">
            Erro ao Carregar Resultados
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 font-inter max-w-2xl mx-auto">
            {error || 'Não foi possível carregar os resultados da auditoria.'}
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => navigate('/history')}
              className="btn-secondary flex items-center gap-2 text-lg px-6 py-3"
            >
              <ArrowLeft className="w-5 h-5" />
              Voltar ao Histórico
            </button>
            <button
              onClick={loadAuditData}
              className="btn-primary text-lg px-6 py-3 shadow-glow hover:shadow-primary-500/50"
            >
              Tentar Novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="glass-card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <button
              onClick={() => navigate('/history')}
              className="btn-secondary flex items-center gap-2 text-lg px-6 py-3"
            >
              <ArrowLeft className="w-5 h-5" />
              Voltar
            </button>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 via-secondary-500 to-accent-500 bg-clip-text text-transparent font-poppins">
                Resultados da Auditoria
              </h1>
              {audit && (
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300 font-inter">
                    <Globe className="w-4 h-4" />
                    <span className="font-medium">{audit.url}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300 font-inter">
                    <Clock className="w-4 h-4" />
                    <span>{formatDate(audit.created_at)}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          <div className="flex gap-3">
            {id && <ExportButton auditId={id} className="shadow-glow hover:shadow-primary-500/50 transform hover:scale-105 transition-all duration-300" />}
            
            <button
              onClick={handleDownloadReport}
              disabled={downloadingReport}
              className="btn-primary flex items-center gap-2 text-lg px-6 py-3 shadow-glow hover:shadow-primary-500/50 transform hover:scale-105 transition-all duration-300"
            >
              {downloadingReport ? (
                <Spinner size="sm" />
              ) : (
                <Download className="w-5 h-5" />
              )}
              <span className="font-poppins">
                {downloadingReport ? 'Baixando...' : 'Baixar Relatório'}
              </span>
            </button>
            
            {audit?.url && (
              <a
                href={audit.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary flex items-center gap-2 text-lg px-6 py-3 hover:shadow-glow transition-all duration-300"
              >
                <ExternalLink className="w-5 h-5" />
                <span className="font-poppins">Visitar Site</span>
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Score Geral */}
      {result.overall_score !== undefined && (
        <div className="glass-card bg-gradient-to-br from-primary-500/10 to-secondary-500/10 border-primary-200 dark:border-primary-800">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3 font-poppins">
                Score Geral
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 font-inter max-w-2xl">
                Pontuação geral da auditoria baseada em todos os critérios analisados
              </p>
            </div>
            <div className="text-center">
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-glow mb-4">
                <div className="text-center">
                  <div className="text-4xl font-bold text-white font-poppins">
                    {result.overall_score}
                  </div>
                  <div className="text-sm text-white/80 font-inter">/ 100</div>
                </div>
              </div>
              {(() => {
                const { icon: ScoreIcon } = getScoreIcon(result.overall_score);
                return <ScoreIcon className="w-10 h-10 mx-auto text-primary-600 dark:text-primary-400" />;
              })()}
            </div>
          </div>
        </div>
      )}

      {/* Análises Detalhadas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {result.seo_analysis && renderAnalysisSection(
          'Análise SEO',
          result.seo_analysis,
          Search
        )}
        
        {result.technical_analysis && renderAnalysisSection(
          'Análise Técnica',
          result.technical_analysis,
          Globe
        )}
        
        {result.performance_analysis && renderAnalysisSection(
          'Performance',
          result.performance_analysis,
          Clock
        )}
        
        {result.mobile_analysis && renderAnalysisSection(
          'Mobile',
          result.mobile_analysis,
          Smartphone
        )}
        
        {result.security_analysis && renderAnalysisSection(
          'Segurança',
          result.security_analysis,
          Shield
        )}
        
        {result.accessibility_analysis && renderAnalysisSection(
          'Acessibilidade',
          result.accessibility_analysis,
          Info
        )}
      </div>

      {/* Informações Adicionais */}
      {(result.screenshots || result.generated_docs) && (
        <div className="glass-card">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 font-poppins">
            Recursos Adicionais
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.screenshots && (
              <div className="flex items-center gap-4 p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border border-blue-200 dark:border-blue-800 hover:shadow-glow transition-all duration-300">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg">
                  <Image className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h4 className="text-xl font-bold text-blue-900 dark:text-blue-100 font-poppins">Screenshots</h4>
                  <p className="text-blue-700 dark:text-blue-300 font-inter">
                    Capturas de tela disponíveis para análise visual
                  </p>
                </div>
              </div>
            )}
            
            {result.generated_docs && (
              <div className="flex items-center gap-4 p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl border border-green-200 dark:border-green-800 hover:shadow-glow transition-all duration-300">
                <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg">
                  <LinkIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h4 className="text-xl font-bold text-green-900 dark:text-green-100 font-poppins">Documentação</h4>
                  <p className="text-green-700 dark:text-green-300 font-inter">
                    Documentação técnica gerada automaticamente
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};