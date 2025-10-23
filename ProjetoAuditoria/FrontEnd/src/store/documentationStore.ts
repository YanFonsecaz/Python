import { create } from 'zustand';
import { ApiService } from '../services/api';

/**
 * Interface para os dados de documentação de auditoria
 */
export interface DocumentationData {
  audit_id: string;
  title: string;
  content: string;
  sections: DocumentationSection[];
  metadata: {
    generated_at: string;
    audit_url: string;
    audit_date: string;
    total_issues: number;
    critical_issues: number;
    warnings: number;
  };
}

/**
 * Interface para seções da documentação
 */
export interface DocumentationSection {
  id: string;
  title: string;
  content: string;
  subsections?: DocumentationSection[];
  type: 'summary' | 'technical' | 'recommendations' | 'issues' | 'metrics';
}

/**
 * Interface para o estado do store de documentação
 */
interface DocumentationState {
  // Estado dos dados
  documentation: DocumentationData | null;
  loading: boolean;
  error: string | null;
  
  // Estado de download
  downloading: boolean;
  downloadError: string | null;
  
  // Ações
  fetchDocumentation: (auditId: string) => Promise<void>;
  downloadDocumentation: (auditId: string, format?: 'docx' | 'pdf') => Promise<void>;
  clearDocumentation: () => void;
  clearError: () => void;
}

/**
 * Store Zustand para gerenciar o estado da documentação de auditorias
 */
export const useDocumentationStore = create<DocumentationState>((set) => ({
  // Estado inicial
  documentation: null,
  loading: false,
  error: null,
  downloading: false,
  downloadError: null,

  /**
   * Busca a documentação de uma auditoria específica
   */
  fetchDocumentation: async (auditId: string) => {
    set({ loading: true, error: null });
    
    try {
      const data = await ApiService.getAuditDocumentation(auditId);
      
      // Transformar os dados da API para o formato esperado
      const documentation: DocumentationData = {
        audit_id: auditId,
        title: data.title || `Documentação da Auditoria ${auditId}`,
        content: data.content || '',
        sections: data.sections || [],
        metadata: {
          generated_at: data.generated_at || new Date().toISOString(),
          audit_url: data.audit_url || '',
          audit_date: data.audit_date || '',
          total_issues: data.total_issues || 0,
          critical_issues: data.critical_issues || 0,
          warnings: data.warnings || 0,
        }
      };
      
      set({ 
        documentation, 
        loading: false, 
        error: null 
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.message || 
                          'Erro ao carregar documentação';
      
      set({ 
        documentation: null, 
        loading: false, 
        error: errorMessage 
      });
    }
  },

  /**
   * Faz download da documentação em formato específico
   */
  downloadDocumentation: async (auditId: string, format: 'docx' | 'pdf' = 'docx') => {
    set({ downloading: true, downloadError: null });
    
    try {
      const blob = await ApiService.downloadAuditDocumentation(auditId, format);
      
      // Criar URL temporária para download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Definir nome do arquivo
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      link.download = `documentacao_auditoria_${auditId}_${timestamp}.${format}`;
      
      // Executar download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Limpar URL temporária
      window.URL.revokeObjectURL(url);
      
      set({ downloading: false, downloadError: null });
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 
                          error.message || 
                          'Erro ao fazer download da documentação';
      
      set({ 
        downloading: false, 
        downloadError: errorMessage 
      });
    }
  },

  /**
   * Limpa os dados de documentação do store
   */
  clearDocumentation: () => {
    set({ 
      documentation: null, 
      loading: false, 
      error: null,
      downloading: false,
      downloadError: null
    });
  },

  /**
   * Limpa apenas os erros do store
   */
  clearError: () => {
    set({ 
      error: null, 
      downloadError: null 
    });
  },
}));

export default useDocumentationStore;