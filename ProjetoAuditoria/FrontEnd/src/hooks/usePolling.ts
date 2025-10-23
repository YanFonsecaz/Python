import { useEffect, useRef, useCallback } from 'react';
import { useAuditStore } from '../store/auditStore';
import { useNotificationStore } from '../store/notificationStore';
import ApiService from '../services/api';
import type { Audit, AuditType } from '../types';

interface UsePollingOptions {
  auditId: string;
  interval?: number;
  onComplete?: (audit: Audit) => void;
  onError?: (error: string) => void;
  enabled?: boolean;
}

/**
 * Hook customizado para fazer polling do status de uma auditoria
 * Atualiza automaticamente o estado da auditoria até que seja concluída
 */
export const usePolling = ({
  auditId,
  interval = 15000, // Aumentado para 15 segundos para reduzir rate limiting
  onComplete,
  onError,
  enabled = true,
}: UsePollingOptions) => {
  const intervalRef = useRef<number | null>(null);
  const retryCountRef = useRef<number>(0);
  const { updateAudit, setError } = useAuditStore();
  const { addNotification } = useNotificationStore();
  
  /**
   * Função para buscar o status da auditoria
   */
  const fetchAuditStatus = useCallback(async () => {
    try {
      const response = await ApiService.getAuditStatus(auditId);
      
      // Reset retry count on successful request
      retryCountRef.current = 0;
      
      if (response.audit_id) {
        const audit: Audit = {
          id: response.audit_id,
          url: '', // URL será preenchida pelo store
          audit_type: 'complete' as AuditType,
          status: response.status,
          progress: response.progress || 0,
          current_step: response.current_step || '',
          created_at: response.start_time || new Date().toISOString(),
          error_message: response.error,
          generate_documentation: false,
          include_screenshots: false
        };
        
        // Atualiza o estado da auditoria
        updateAudit(auditId, audit);
        
        // Verifica se a auditoria foi concluída
        if (audit.status === 'completed' || audit.status === 'failed' || audit.status === 'cancelled') {
          stopPolling();
          
          if (audit.status === 'completed' && onComplete) {
            onComplete(audit);
          } else if (audit.status === 'failed') {
            const errorMessage = audit.error_message || 'Auditoria falhou';
            setError(errorMessage);
            addNotification({ type: 'error', message: errorMessage, title: 'Erro na Auditoria' });
            
            if (onError) {
              onError(errorMessage);
            }
          }
        }
      } else {
        const errorMessage = response.error || 'Erro ao buscar status da auditoria';
        setError(errorMessage);
        addNotification({ type: 'error', message: errorMessage, title: 'Erro' });
        stopPolling();
        
        if (onError) {
          onError(errorMessage);
        }
      }
    } catch (error: any) {
      // Increment retry count
      retryCountRef.current += 1;
      
      // Check if it's a rate limit error
      if (error.response?.status === 429 || error.response?.status === 500) {
        // Implement exponential backoff for rate limit errors
        const backoffDelay = Math.min(60000, interval * Math.pow(2, retryCountRef.current - 1));
        
        console.warn(`Rate limit hit, backing off for ${backoffDelay}ms`);
        
        // Stop current polling and restart with backoff delay
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
        
        setTimeout(() => {
          if (enabled && retryCountRef.current < 3) { // Reduzido para 3 tentativas
            intervalRef.current = setInterval(fetchAuditStatus, Math.max(interval, 20000)); // Mínimo de 20s após rate limit
          } else {
            const errorMessage = 'Muitas tentativas falharam. Tente novamente mais tarde.';
            setError(errorMessage);
            addNotification({ type: 'error', message: errorMessage, title: 'Erro de Conexão' });
            stopPolling();
            
            if (onError) {
              onError(errorMessage);
            }
          }
        }, backoffDelay);
        
        return;
      }
      
      // For other errors, stop polling after 3 attempts
      if (retryCountRef.current >= 3) {
        const errorMessage = 'Erro de conexão ao buscar status da auditoria';
        setError(errorMessage);
        addNotification({ type: 'error', message: errorMessage, title: 'Erro de Conexão' });
        stopPolling();
        
        if (onError) {
          onError(errorMessage);
        }
      }
    }
  }, [auditId, updateAudit, setError, addNotification, onComplete, onError, enabled, interval]);
  
  /**
   * Inicia o polling
   */
  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    // Reset retry count when starting fresh
    retryCountRef.current = 0;
    
    // Primeira busca imediata
    fetchAuditStatus();
    
    // Configura o intervalo
    intervalRef.current = setInterval(fetchAuditStatus, interval);
  }, [fetchAuditStatus, interval]);
  
  /**
   * Para o polling
   */
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);
  
  /**
   * Reinicia o polling
   */
  const restartPolling = useCallback(() => {
    stopPolling();
    startPolling();
  }, [stopPolling, startPolling]);
  
  // Efeito para controlar o polling baseado no enabled
  useEffect(() => {
    if (enabled && auditId) {
      startPolling();
    } else {
      stopPolling();
    }
    
    // Cleanup ao desmontar o componente
    return () => {
      stopPolling();
    };
  }, [enabled, auditId, startPolling, stopPolling]);
  
  return {
    startPolling,
    stopPolling,
    restartPolling,
    isPolling: intervalRef.current !== null,
  };
};