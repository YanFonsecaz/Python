import { io, Socket } from 'socket.io-client';

/**
 * Interface para mensagens de notificação WebSocket
 */
export interface NotificationMessage {
  type: 'audit_progress' | 'audit_completion' | 'system_alert' | 'metrics_update';
  data: any;
  timestamp: string;
  audit_id?: string;
}

/**
 * Interface para callbacks de eventos WebSocket
 */
export interface WebSocketCallbacks {
  onAuditProgress?: (data: any) => void;
  onAuditCompletion?: (data: any) => void;
  onSystemAlert?: (data: any) => void;
  onMetricsUpdate?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
}

/**
 * Classe para gerenciar conexões WebSocket com o backend
 */
class WebSocketService {
  private socket: Socket | null = null;
  private callbacks: WebSocketCallbacks = {};
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  /**
   * Inicializa a conexão WebSocket
   */
  connect(callbacks: WebSocketCallbacks = {}): void {
    if (this.socket?.connected) {
      console.log('WebSocket já está conectado');
      return;
    }

    this.callbacks = callbacks;
    const serverUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

    this.socket = io(serverUrl, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    });

    this.setupEventListeners();
  }

  /**
   * Configura os listeners de eventos WebSocket
   */
  private setupEventListeners(): void {
    if (!this.socket) return;

    // Eventos de conexão
    this.socket.on('connect', () => {
      console.log('WebSocket conectado com sucesso');
      this.callbacks.onConnect?.();
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket desconectado:', reason);
      this.callbacks.onDisconnect?.();
    });

    this.socket.on('connect_error', (error) => {
      console.error('Erro de conexão WebSocket:', error);
      this.callbacks.onError?.(error);
    });

    // Eventos de notificação
    this.socket.on('audit_progress', (data) => {
      console.log('Progresso da auditoria recebido:', data);
      this.callbacks.onAuditProgress?.(data);
    });

    this.socket.on('audit_completion', (data) => {
      console.log('Auditoria concluída:', data);
      this.callbacks.onAuditCompletion?.(data);
    });

    this.socket.on('system_alert', (data) => {
      console.log('Alerta do sistema:', data);
      this.callbacks.onSystemAlert?.(data);
    });

    this.socket.on('metrics_update', (data) => {
      console.log('Atualização de métricas:', data);
      this.callbacks.onMetricsUpdate?.(data);
    });

    // Evento genérico para notificações
    this.socket.on('notification', (message: NotificationMessage) => {
      console.log('Notificação recebida:', message);
      
      switch (message.type) {
        case 'audit_progress':
          this.callbacks.onAuditProgress?.(message.data);
          break;
        case 'audit_completion':
          this.callbacks.onAuditCompletion?.(message.data);
          break;
        case 'system_alert':
          this.callbacks.onSystemAlert?.(message.data);
          break;
        case 'metrics_update':
          this.callbacks.onMetricsUpdate?.(message.data);
          break;
      }
    });
  }

  /**
   * Entra em uma sala específica (para receber notificações de uma auditoria específica)
   */
  joinAuditRoom(auditId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('join_audit', { audit_id: auditId });
      console.log(`Entrou na sala da auditoria: ${auditId}`);
    }
  }

  /**
   * Sai de uma sala específica
   */
  leaveAuditRoom(auditId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('leave_audit', { audit_id: auditId });
      console.log(`Saiu da sala da auditoria: ${auditId}`);
    }
  }

  /**
   * Envia uma mensagem personalizada
   */
  emit(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    }
  }

  /**
   * Desconecta o WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('WebSocket desconectado manualmente');
    }
  }

  /**
   * Verifica se está conectado
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Obtém o ID da conexão
   */
  getConnectionId(): string | undefined {
    return this.socket?.id;
  }

  /**
   * Atualiza os callbacks
   */
  updateCallbacks(callbacks: WebSocketCallbacks): void {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }
}

// Instância singleton do serviço WebSocket
export const websocketService = new WebSocketService();

// Hook personalizado para usar WebSocket em componentes React
export const useWebSocket = (callbacks: WebSocketCallbacks = {}) => {
  const connect = () => websocketService.connect(callbacks);
  const disconnect = () => websocketService.disconnect();
  const joinAuditRoom = (auditId: string) => websocketService.joinAuditRoom(auditId);
  const leaveAuditRoom = (auditId: string) => websocketService.leaveAuditRoom(auditId);
  const emit = (event: string, data: any) => websocketService.emit(event, data);
  const isConnected = () => websocketService.isConnected();

  return {
    connect,
    disconnect,
    joinAuditRoom,
    leaveAuditRoom,
    emit,
    isConnected,
    connectionId: websocketService.getConnectionId(),
  };
};

export default websocketService;