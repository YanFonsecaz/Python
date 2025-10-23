import React, { useState } from 'react';
import { ApiService } from '../services/api';

/**
 * Componente para testar os novos endpoints implementados
 */
export const TestNewEndpoints: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{ [key: string]: any }>({});
  const [auditId, setAuditId] = useState('781c4ef7-795b-4b6a-8a8f-704f12379294');

  /**
   * Testa o endpoint de reset de métricas de performance
   */
  const testResetPerformanceMetrics = async () => {
    setLoading(true);
    try {
      const result = await ApiService.resetPerformanceMetrics();
      setResults(prev => ({ ...prev, resetPerformance: result }));
    } catch (error) {
      setResults(prev => ({ ...prev, resetPerformance: { error: error instanceof Error ? error.message : 'Erro desconhecido' } }));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Testa o endpoint de iniciar processador de auditorias
   */
  const testStartAuditProcessor = async () => {
    setLoading(true);
    try {
      const result = await ApiService.startAuditProcessor();
      setResults(prev => ({ ...prev, startProcessor: result }));
    } catch (error) {
      setResults(prev => ({ ...prev, startProcessor: { error: error instanceof Error ? error.message : 'Erro desconhecido' } }));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Testa o endpoint de obter relatório de auditoria
   */
  const testGetAuditReport = async () => {
    setLoading(true);
    try {
      const result = await ApiService.getAuditReport(auditId);
      setResults(prev => ({ ...prev, auditReport: result }));
    } catch (error) {
      setResults(prev => ({ ...prev, auditReport: { error: error instanceof Error ? error.message : 'Erro desconhecido' } }));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Testa o endpoint de exportar auditoria
   */
  const testExportAudit = async (format: 'json' | 'docx' | 'pdf') => {
    setLoading(true);
    try {
      const blob = await ApiService.exportAudit(auditId, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_${auditId}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setResults(prev => ({ 
        ...prev, 
        exportAudit: { 
          message: `Auditoria exportada com sucesso em formato ${format}`,
          size: blob.size 
        } 
      }));
    } catch (error) {
      setResults(prev => ({ ...prev, exportAudit: { error: error instanceof Error ? error.message : 'Erro desconhecido' } }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        Teste dos Novos Endpoints
      </h2>

      {/* Input para ID da auditoria */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ID da Auditoria para Teste:
        </label>
        <input
          type="text"
          value={auditId}
          onChange={(e) => setAuditId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Digite o ID da auditoria"
        />
      </div>

      {/* Botões de teste */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <button
          onClick={testResetPerformanceMetrics}
          disabled={loading}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
        >
          Resetar Métricas de Performance
        </button>

        <button
          onClick={testStartAuditProcessor}
          disabled={loading}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          Iniciar Processador de Auditorias
        </button>

        <button
          onClick={testGetAuditReport}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Obter Relatório de Auditoria
        </button>

        <div className="flex gap-2">
          <button
            onClick={() => testExportAudit('json')}
            disabled={loading}
            className="px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50 text-sm"
          >
            Exportar JSON
          </button>
          <button
            onClick={() => testExportAudit('docx')}
            disabled={loading}
            className="px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50 text-sm"
          >
            Exportar DOCX
          </button>
          <button
            onClick={() => testExportAudit('pdf')}
            disabled={loading}
            className="px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50 text-sm"
          >
            Exportar PDF
          </button>
        </div>
      </div>

      {/* Indicador de carregamento */}
      {loading && (
        <div className="mb-4 p-3 bg-blue-100 border border-blue-300 rounded">
          <p className="text-blue-700">Executando teste...</p>
        </div>
      )}

      {/* Resultados dos testes */}
      {Object.keys(results).length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Resultados dos Testes:</h3>
          
          {Object.entries(results).map(([key, result]) => (
            <div key={key} className="p-4 bg-gray-50 rounded border">
              <h4 className="font-medium text-gray-700 mb-2 capitalize">
                {key.replace(/([A-Z])/g, ' $1').trim()}:
              </h4>
              <pre className="text-sm text-gray-600 overflow-x-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TestNewEndpoints;