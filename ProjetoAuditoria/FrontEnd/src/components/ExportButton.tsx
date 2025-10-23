import React, { useState } from 'react';
import { Download, FileText, FileJson, FileSpreadsheet, Loader2 } from 'lucide-react';

interface ExportButtonProps {
  auditId: string;
  className?: string;
  variant?: 'default' | 'compact';
}

/**
 * Componente para exportar relatórios de auditoria em diferentes formatos
 */
export function ExportButton({ auditId, className = '', variant = 'default' }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  // Hook para fechar dropdown ao clicar fora
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('[data-export-dropdown]')) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showDropdown]);

  /**
   * Realiza o download do arquivo de exportação
   */
  const handleExport = async (format: 'json' | 'html' | 'csv') => {
    setIsExporting(true);
    setShowDropdown(false);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/audit/export/${auditId}?format=${format}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/octet-stream',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao exportar relatório');
      }

      // Obtém o nome do arquivo do cabeçalho Content-Disposition ou gera um padrão
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `audit_report_${auditId}.${format}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Cria blob e inicia download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('Erro ao exportar relatório:', error);
      alert(`Erro ao exportar relatório: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    } finally {
      setIsExporting(false);
    }
  };

  const exportOptions = [
    {
      format: 'json' as const,
      label: 'JSON',
      description: 'Dados completos em formato JSON',
      icon: FileJson,
      color: 'text-blue-600'
    },
    {
      format: 'html' as const,
      label: 'HTML',
      description: 'Relatório visual em HTML',
      icon: FileText,
      color: 'text-orange-600'
    },
    {
      format: 'csv' as const,
      label: 'CSV',
      description: 'Resumo em planilha CSV',
      icon: FileSpreadsheet,
      color: 'text-green-600'
    }
  ];

  if (variant === 'compact') {
    return (
      <div className="relative">
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={isExporting}
          className={`inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
        >
          {isExporting ? (
            <Loader2 className="w-4 h-4 mr-1 animate-spin" />
          ) : (
            <Download className="w-4 h-4 mr-1" />
          )}
          Exportar
        </button>

        {showDropdown && (
          <div className="absolute right-0 z-10 mt-2 w-56 bg-white border border-gray-200 rounded-md shadow-lg">
            <div className="py-1">
              {exportOptions.map((option) => {
                const IconComponent = option.icon;
                return (
                  <button
                    key={option.format}
                    onClick={() => handleExport(option.format)}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <IconComponent className={`w-4 h-4 mr-3 ${option.color}`} />
                    <div className="text-left">
                      <div className="font-medium">{option.label}</div>
                      <div className="text-xs text-gray-500">{option.description}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        disabled={isExporting}
        className={`inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      >
        {isExporting ? (
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
        ) : (
          <Download className="w-4 h-4 mr-2" />
        )}
        Exportar Relatório
      </button>

      {showDropdown && (
        <div className="absolute right-0 z-10 mt-2 w-64 bg-white border border-gray-200 rounded-md shadow-lg">
          <div className="p-2">
            <div className="text-sm font-medium text-gray-900 mb-2">Escolha o formato:</div>
            {exportOptions.map((option) => {
              const IconComponent = option.icon;
              return (
                <button
                  key={option.format}
                  onClick={() => handleExport(option.format)}
                  className="flex items-center w-full px-3 py-2 text-sm text-gray-700 rounded-md hover:bg-gray-100"
                >
                  <IconComponent className={`w-5 h-5 mr-3 ${option.color}`} />
                  <div className="text-left">
                    <div className="font-medium">{option.label}</div>
                    <div className="text-xs text-gray-500">{option.description}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}