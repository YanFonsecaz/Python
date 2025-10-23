import React, { useEffect, useState } from 'react';
import { useNotifications } from '../store/notificationStore';
import { Bell, X, Check, AlertTriangle, Info, Wifi, WifiOff } from 'lucide-react';

/**
 * Componente para exibir o centro de notificações
 */
export const NotificationCenter: React.FC = () => {
  const {
    notifications,
    unreadCount,
    isConnected,
    removeNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    connectWebSocket,
    disconnectWebSocket,
  } = useNotifications();

  const [isOpen, setIsOpen] = useState(false);

  // Conecta automaticamente ao WebSocket quando o componente é montado
  useEffect(() => {
    connectWebSocket();
    
    return () => {
      disconnectWebSocket();
    };
  }, [connectWebSocket, disconnectWebSocket]);

  /**
   * Obtém o ícone baseado no tipo da notificação
   */
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <Check className="w-5 h-5 text-green-500" />;
      case 'error':
        return <X className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'progress':
        return <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  /**
   * Obtém as classes CSS baseadas no tipo da notificação
   */
  const getNotificationClasses = (type: string, read: boolean = false) => {
    const baseClasses = `p-4 rounded-lg border-l-4 transition-all duration-200 ${
      read ? 'opacity-60' : 'opacity-100'
    }`;
    
    switch (type) {
      case 'success':
        return `${baseClasses} bg-green-50 border-green-500 dark:bg-green-900/20`;
      case 'error':
        return `${baseClasses} bg-red-50 border-red-500 dark:bg-red-900/20`;
      case 'warning':
        return `${baseClasses} bg-yellow-50 border-yellow-500 dark:bg-yellow-900/20`;
      case 'progress':
        return `${baseClasses} bg-blue-50 border-blue-500 dark:bg-blue-900/20`;
      default:
        return `${baseClasses} bg-blue-50 border-blue-500 dark:bg-blue-900/20`;
    }
  };

  /**
   * Formata o timestamp da notificação
   */
  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) { // menos de 1 minuto
      return 'agora';
    } else if (diff < 3600000) { // menos de 1 hora
      return `${Math.floor(diff / 60000)}m atrás`;
    } else if (diff < 86400000) { // menos de 1 dia
      return `${Math.floor(diff / 3600000)}h atrás`;
    } else {
      return date.toLocaleDateString('pt-BR');
    }
  };

  return (
    <div className="relative">
      {/* Botão do sino de notificações */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
        title="Notificações"
      >
        <Bell className="w-6 h-6" />
        
        {/* Badge de notificações não lidas */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        
        {/* Indicador de conexão */}
        <div className="absolute -bottom-1 -right-1">
          {isConnected ? (
            <Wifi className="w-3 h-3 text-green-500" />
          ) : (
            <WifiOff className="w-3 h-3 text-red-500" />
          )}
        </div>
      </button>

      {/* Painel de notificações */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-96 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-hidden">
          {/* Cabeçalho */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Notificações
            </h3>
            
            <div className="flex items-center space-x-2">
              {/* Status da conexão */}
              <div className="flex items-center space-x-1 text-sm">
                {isConnected ? (
                  <>
                    <Wifi className="w-4 h-4 text-green-500" />
                    <span className="text-green-600 dark:text-green-400">Online</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-4 h-4 text-red-500" />
                    <span className="text-red-600 dark:text-red-400">Offline</span>
                  </>
                )}
              </div>
              
              {/* Botões de ação */}
              {notifications.length > 0 && (
                <div className="flex space-x-1">
                  <button
                    onClick={markAllAsRead}
                    className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                    title="Marcar todas como lidas"
                  >
                    Marcar lidas
                  </button>
                  <span className="text-gray-300">|</span>
                  <button
                    onClick={clearAll}
                    className="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                    title="Limpar todas"
                  >
                    Limpar
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Lista de notificações */}
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Nenhuma notificação</p>
              </div>
            ) : (
              <div className="p-2 space-y-2">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={getNotificationClasses(notification.type, notification.read)}
                  >
                    <div className="flex items-start space-x-3">
                      {/* Ícone da notificação */}
                      <div className="flex-shrink-0 mt-0.5">
                        {getNotificationIcon(notification.type)}
                      </div>
                      
                      {/* Conteúdo da notificação */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                              {notification.title}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                              {notification.message}
                            </p>
                            
                            {/* Barra de progresso para notificações de progresso */}
                            {notification.type === 'progress' && notification.progress !== undefined && (
                              <div className="mt-2">
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${notification.progress}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-500 mt-1">
                                  {notification.progress}%
                                </span>
                              </div>
                            )}
                            
                            <div className="flex items-center justify-between mt-2">
                              <span className="text-xs text-gray-500">
                                {formatTimestamp(notification.timestamp)}
                              </span>
                              
                              {/* Indicador de não lida */}
                              {!notification.read && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                              )}
                            </div>
                          </div>
                          
                          {/* Botões de ação */}
                          <div className="flex items-center space-x-1 ml-2">
                            {!notification.read && (
                              <button
                                onClick={() => markAsRead(notification.id)}
                                className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                                title="Marcar como lida"
                              >
                                <Check className="w-4 h-4" />
                              </button>
                            )}
                            
                            <button
                              onClick={() => removeNotification(notification.id)}
                              className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                              title="Remover notificação"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Overlay para fechar o painel */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default NotificationCenter;