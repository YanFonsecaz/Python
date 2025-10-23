import { create } from 'zustand';
import type { Notification } from '../types';
import { websocketService } from '../services/websocket';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;
  connectionId?: string;
  
  // Ações básicas
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  
  // WebSocket
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  setConnectionStatus: (connected: boolean, connectionId?: string) => void;
  
  // Filtros
  getNotificationsByType: (type: string) => Notification[];
  getNotificationsByAudit: (auditId: string) => Notification[];
  getUnreadNotifications: () => Notification[];
}

/**
 * Store para gerenciamento de notificações em tempo real
 * Controla mensagens de sucesso, erro, aviso e informação com WebSocket
 */
export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isConnected: false,
  connectionId: undefined,
  
  /**
   * Adiciona uma nova notificação
   */
  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9);
    const timestamp = Date.now();
    
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp,
    };
    
    set((state) => ({
      notifications: [...state.notifications, newNotification],
      unreadCount: state.unreadCount + 1,
    }));
    
    // Remove automaticamente após 5 segundos (exceto para erros)
    if (notification.type !== 'error') {
      setTimeout(() => {
        get().removeNotification(id);
      }, 5000);
    }
  },
  
  /**
   * Remove uma notificação específica
   */
  removeNotification: (id: string) => {
    set((state) => {
      const notification = state.notifications.find(n => n.id === id);
      const wasUnread = notification && !notification.read;
      
      return {
        notifications: state.notifications.filter((n) => n.id !== id),
        unreadCount: wasUnread ? state.unreadCount - 1 : state.unreadCount,
      };
    });
  },
  
  /**
   * Limpa todas as notificações
   */
  clearNotifications: () => {
    set({
      notifications: [],
      unreadCount: 0,
    });
  },

  /**
   * Marca uma notificação como lida
   */
  markAsRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map(n => 
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: state.notifications.find(n => n.id === id && !n.read) 
        ? state.unreadCount - 1 
        : state.unreadCount,
    }));
  },

  /**
   * Marca todas as notificações como lidas
   */
  markAllAsRead: () => {
    set((state) => ({
      notifications: state.notifications.map(n => ({ ...n, read: true })),
      unreadCount: 0,
    }));
  },

  /**
   * Conecta ao WebSocket
   */
  connectWebSocket: () => {
    const { addNotification, setConnectionStatus } = get();
    
    websocketService.connect({
      onConnect: () => {
        setConnectionStatus(true, websocketService.getConnectionId());
        addNotification({
          type: 'success',
          title: 'Conectado',
          message: 'Conexão em tempo real estabelecida',
        });
      },

      onDisconnect: () => {
        setConnectionStatus(false);
        addNotification({
          type: 'warning',
          title: 'Desconectado',
          message: 'Conexão em tempo real perdida',
        });
      },

      onError: () => {
        addNotification({
          type: 'error',
          title: 'Erro de Conexão',
          message: 'Falha na conexão WebSocket',
        });
      },

      onAuditProgress: (data) => {
        addNotification({
          type: 'info',
          title: 'Progresso da Auditoria',
          message: `${data.step} - ${data.progress}%`,
        });
      },

      onAuditCompletion: (data) => {
        const isSuccess = data.status === 'completed';
        addNotification({
          type: isSuccess ? 'success' : 'error',
          title: isSuccess ? 'Auditoria Concluída' : 'Auditoria Falhou',
          message: data.summary || (isSuccess ? 'Auditoria finalizada com sucesso' : 'Erro durante a auditoria'),
        });
      },

      onSystemAlert: (data) => {
        addNotification({
          type: data.level === 'critical' ? 'error' : 'warning',
          title: 'Alerta do Sistema',
          message: data.message,
        });
      },

      onMetricsUpdate: (data) => {
        if (data.alert) {
          addNotification({
            type: 'info',
            title: 'Atualização de Métricas',
            message: data.message || 'Métricas do sistema atualizadas',
          });
        }
      },
    });
  },

  /**
   * Desconecta do WebSocket
   */
  disconnectWebSocket: () => {
    websocketService.disconnect();
    set({
      isConnected: false,
      connectionId: undefined,
    });
  },

  /**
   * Define o status da conexão
   */
  setConnectionStatus: (connected, connectionId) => {
    set({
      isConnected: connected,
      connectionId,
    });
  },

  /**
   * Obtém notificações por tipo
   */
  getNotificationsByType: (type) => {
    return get().notifications.filter(n => n.type === type);
  },

  /**
   * Obtém notificações por auditoria
   */
  getNotificationsByAudit: (auditId) => {
    return get().notifications.filter(n => n.auditId === auditId);
  },

  /**
   * Obtém notificações não lidas
   */
  getUnreadNotifications: () => {
    return get().notifications.filter(n => !n.read);
  },
}));

// Helper functions para facilitar o uso
export const useNotifications = () => {
  const store = useNotificationStore();
  
  return {
    // Estados
    notifications: store.notifications,
    unreadCount: store.unreadCount,
    isConnected: store.isConnected,
    connectionId: store.connectionId,
    
    // Ações básicas
    addNotification: store.addNotification,
    removeNotification: store.removeNotification,
    clearNotifications: store.clearNotifications,
    markAsRead: store.markAsRead,
    markAllAsRead: store.markAllAsRead,
    
    // WebSocket
    connectWebSocket: store.connectWebSocket,
    disconnectWebSocket: store.disconnectWebSocket,
    setConnectionStatus: store.setConnectionStatus,
    
    // Filtros
    getNotificationsByType: store.getNotificationsByType,
    getNotificationsByAudit: store.getNotificationsByAudit,
    getUnreadNotifications: store.getUnreadNotifications,
    
    // Helper functions
    showSuccess: (message: string, title = '') => 
      store.addNotification({ type: 'success', message, title }),
    
    showError: (message: string, title = '') => 
      store.addNotification({ type: 'error', message, title }),
    
    showWarning: (message: string, title = '') => 
      store.addNotification({ type: 'warning', message, title }),
    
    showInfo: (message: string, title = '') => 
      store.addNotification({ type: 'info', message, title }),
      
    clearAll: store.clearNotifications,
  };
};