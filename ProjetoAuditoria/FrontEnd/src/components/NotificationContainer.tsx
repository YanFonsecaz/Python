import React from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { useNotificationStore } from '../store/notificationStore';

/**
 * Componente para exibir notificações toast
 */
export const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotificationStore();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-400" />;
      default:
        return <Info className="h-5 w-5 text-blue-400" />;
    }
  };

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'info':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
      default:
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
    }
  };

  const getTextColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-800 dark:text-green-200';
      case 'error':
        return 'text-red-800 dark:text-red-200';
      case 'warning':
        return 'text-yellow-800 dark:text-yellow-200';
      case 'info':
        return 'text-blue-800 dark:text-blue-200';
      default:
        return 'text-blue-800 dark:text-blue-200';
    }
  };

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`
            p-4 rounded-lg border shadow-lg transform transition-all duration-300 ease-in-out
            ${getBackgroundColor(notification.type)}
            animate-slide-in-right
          `}
        >
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {getIcon(notification.type)}
            </div>
            <div className="ml-3 flex-1">
              {notification.title && (
                <h3 className={`text-sm font-medium ${getTextColor(notification.type)}`}>
                  {notification.title}
                </h3>
              )}
              <p className={`text-sm ${notification.title ? 'mt-1' : ''} ${getTextColor(notification.type)}`}>
                {notification.message}
              </p>
            </div>
            <div className="ml-4 flex-shrink-0">
              <button
                type="button"
                className={`
                  inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2
                  ${notification.type === 'success' ? 'text-green-500 hover:bg-green-100 dark:hover:bg-green-800 focus:ring-green-600' : ''}
                  ${notification.type === 'error' ? 'text-red-500 hover:bg-red-100 dark:hover:bg-red-800 focus:ring-red-600' : ''}
                  ${notification.type === 'warning' ? 'text-yellow-500 hover:bg-yellow-100 dark:hover:bg-yellow-800 focus:ring-yellow-600' : ''}
                  ${notification.type === 'info' ? 'text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-800 focus:ring-blue-600' : ''}
                `}
                onClick={() => removeNotification(notification.id)}
              >
                <span className="sr-only">Fechar</span>
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};