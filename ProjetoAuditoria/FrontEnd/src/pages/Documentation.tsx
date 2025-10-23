import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  DocumentTextIcon, 
  ArrowDownTrayIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  ChartBarIcon,
  ClockIcon,
  LinkIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { useDocumentationStore, type DocumentationSection } from '../store/documentationStore';
import { Spinner } from '../components';

/**
 * Página de documentação de auditoria
 * Exibe a documentação completa de uma auditoria específica
 */
export function Documentation() {
  const { auditId } = useParams<{ auditId: string }>();
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState<string>('');
  const [downloadFormat, setDownloadFormat] = useState<'docx' | 'pdf'>('docx');

  const {
    documentation,
    loading,
    error,
    downloading,
    downloadError,
    fetchDocumentation,
    downloadDocumentation,
    clearError,
    clearDocumentation
  } = useDocumentationStore();

  // Carregar documentação ao montar o componente
  useEffect(() => {
    if (auditId) {
      fetchDocumentation(auditId);
    }

    // Limpar dados ao desmontar
    return () => {
      clearDocumentation();
    };
  }, [auditId, fetchDocumentation, clearDocumentation]);

  // Função para fazer download da documentação
  const handleDownload = async () => {
    if (auditId) {
      await downloadDocumentation(auditId, downloadFormat);
    }
  };

  // Função para navegar para uma seção específica
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      setActiveSection(sectionId);
    }
  };

  // Função para renderizar ícone baseado no tipo da seção
  const getSectionIcon = (type: DocumentationSection['type']) => {
    switch (type) {
      case 'summary':
        return <InformationCircleIcon className="h-5 w-5" />;
      case 'technical':
        return <DocumentTextIcon className="h-5 w-5" />;
      case 'recommendations':
        return <ExclamationTriangleIcon className="h-5 w-5" />;
      case 'issues':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'metrics':
        return <ChartBarIcon className="h-5 w-5" />;
      default:
        return <DocumentTextIcon className="h-5 w-5" />;
    }
  };

  // Função para renderizar seção da documentação
  const renderSection = (section: DocumentationSection, level: number = 0) => {
    const headingClass = level === 0 
      ? 'text-2xl font-bold text-gray-900 dark:text-white mb-4'
      : level === 1
      ? 'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3'
      : 'text-lg font-medium text-gray-700 dark:text-gray-300 mb-2';

    return (
      <div key={section.id} id={section.id} className={`mb-6 ${level > 0 ? 'ml-4' : ''}`}>
        <div className="flex items-center gap-2 mb-3">
          {getSectionIcon(section.type)}
          <h3 className={headingClass}>{section.title}</h3>
        </div>
        
        <div className="prose prose-gray dark:prose-invert max-w-none">
          <div dangerouslySetInnerHTML={{ __html: section.content }} />
        </div>

        {section.subsections && section.subsections.length > 0 && (
          <div className="mt-4">
            {section.subsections.map(subsection => 
              renderSection(subsection, level + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <Spinner />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Carregando documentação...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <ExclamationTriangleIcon className="h-6 w-6 text-red-600 dark:text-red-400" />
            <h2 className="text-lg font-semibold text-red-800 dark:text-red-200">
              Erro ao Carregar Documentação
            </h2>
          </div>
          <p className="text-red-700 dark:text-red-300 mb-4">{error}</p>
          <div className="flex gap-3">
            <button
              onClick={() => auditId && fetchDocumentation(auditId)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Tentar Novamente
            </button>
            <button
              onClick={() => navigate('/auditorias')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Voltar às Auditorias
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!documentation) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <InformationCircleIcon className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
            <h2 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200">
              Documentação Não Encontrada
            </h2>
          </div>
          <p className="text-yellow-700 dark:text-yellow-300 mb-4">
            A documentação para esta auditoria não foi encontrada ou ainda não foi gerada.
          </p>
          <button
            onClick={() => navigate('/auditorias')}
            className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
          >
            Voltar às Auditorias
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/auditorias')}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <ArrowLeftIcon className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {documentation.title}
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Auditoria ID: {documentation.audit_id}
              </p>
            </div>
          </div>

          {/* Controles de Download */}
          <div className="flex items-center gap-3">
            <select
              value={downloadFormat}
              onChange={(e) => setDownloadFormat(e.target.value as 'docx' | 'pdf')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="docx">Word (.docx)</option>
              <option value="pdf">PDF (.pdf)</option>
            </select>
            
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
              {downloading ? 'Baixando...' : 'Download'}
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-center gap-2">
            <LinkIcon className="h-5 w-5 text-gray-500" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">URL Auditada</p>
              <p className="font-medium text-gray-900 dark:text-white truncate">
                {documentation.metadata.audit_url || 'N/A'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ClockIcon className="h-5 w-5 text-gray-500" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Data da Auditoria</p>
              <p className="font-medium text-gray-900 dark:text-white">
                {documentation.metadata.audit_date 
                  ? new Date(documentation.metadata.audit_date).toLocaleDateString('pt-BR')
                  : 'N/A'
                }
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Problemas Críticos</p>
              <p className="font-medium text-red-600 dark:text-red-400">
                {documentation.metadata.critical_issues}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ChartBarIcon className="h-5 w-5 text-yellow-500" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total de Issues</p>
              <p className="font-medium text-yellow-600 dark:text-yellow-400">
                {documentation.metadata.total_issues}
              </p>
            </div>
          </div>
        </div>

        {/* Erro de Download */}
        {downloadError && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center gap-2">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-400" />
              <p className="text-red-700 dark:text-red-300">{downloadError}</p>
              <button
                onClick={clearError}
                className="ml-auto text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-8">
        {/* Índice de Navegação */}
        {documentation.sections.length > 0 && (
          <div className="w-64 flex-shrink-0">
            <div className="sticky top-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Índice
              </h3>
              <nav className="space-y-2">
                {documentation.sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      activeSection === section.id
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {getSectionIcon(section.type)}
                      <span className="text-sm">{section.title}</span>
                    </div>
                  </button>
                ))}
              </nav>
            </div>
          </div>
        )}

        {/* Conteúdo da Documentação */}
        <div className="flex-1 min-w-0">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
            {documentation.content && (
              <div className="prose prose-gray dark:prose-invert max-w-none mb-8">
                <div dangerouslySetInnerHTML={{ __html: documentation.content }} />
              </div>
            )}

            {documentation.sections.map((section) => renderSection(section))}

            {documentation.sections.length === 0 && !documentation.content && (
              <div className="text-center py-12">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">
                  Nenhum conteúdo de documentação disponível.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Documentation;