"""
Gerenciador de WebSockets para notificações em tempo real.

Este módulo implementa um sistema de WebSockets usando Flask-SocketIO
para fornecer notificações em tempo real sobre o progresso das auditorias,
alertas do sistema e atualizações de métricas.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from dataclasses import dataclass, asdict
import json
import threading
import time

logger = logging.getLogger(__name__)


@dataclass
class NotificationMessage:
    """Estrutura de uma mensagem de notificação."""
    id: str
    type: str  # 'audit_progress', 'audit_complete', 'system_alert', 'metric_update'
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: str = 'normal'  # 'low', 'normal', 'high', 'critical'
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização JSON."""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority
        }


class WebSocketManager:
    """
    Gerenciador de WebSockets para notificações em tempo real.
    
    Gerencia conexões de clientes, salas de notificação e envio
    de mensagens em tempo real para o frontend.
    """
    
    def __init__(self, app: Optional[Flask] = None):
        """
        Inicializa o gerenciador de WebSockets.
        
        Args:
            app: Instância Flask (opcional)
        """
        self.socketio: Optional[SocketIO] = None
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.notification_history: List[NotificationMessage] = []
        self.max_history_size = 1000
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Inicializa o SocketIO com a aplicação Flask.
        
        Args:
            app: Instância Flask
        """
        self.socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=False,
            engineio_logger=False
        )
        
        self._register_handlers()
        logger.info("WebSocket Manager inicializado com sucesso")
    
    def _register_handlers(self) -> None:
        """Registra os handlers de eventos WebSocket."""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handler para conexão de cliente."""
            client_id = self._get_client_id()
            
            self.connected_clients[client_id] = {
                'connected_at': datetime.now(),
                'rooms': ['general'],
                'last_activity': datetime.now()
            }
            
            # Adiciona à sala geral
            join_room('general')
            
            logger.info(f"Cliente conectado: {client_id}")
            
            # Envia notificações recentes
            self._send_recent_notifications(client_id)
            
            emit('connection_established', {
                'client_id': client_id,
                'timestamp': datetime.now().isoformat(),
                'message': 'Conectado ao sistema de notificações'
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handler para desconexão de cliente."""
            client_id = self._get_client_id()
            
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            logger.info(f"Cliente desconectado: {client_id}")
        
        @self.socketio.on('join_audit_room')
        def handle_join_audit_room(data):
            """Handler para entrar em sala de auditoria específica."""
            audit_id = data.get('audit_id')
            if not audit_id:
                emit('error', {'message': 'audit_id é obrigatório'})
                return
            
            client_id = self._get_client_id()
            room_name = f'audit_{audit_id}'
            
            join_room(room_name)
            
            if client_id in self.connected_clients:
                self.connected_clients[client_id]['rooms'].append(room_name)
            
            logger.info(f"Cliente {client_id} entrou na sala {room_name}")
            
            emit('joined_audit_room', {
                'audit_id': audit_id,
                'room': room_name,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('leave_audit_room')
        def handle_leave_audit_room(data):
            """Handler para sair de sala de auditoria específica."""
            audit_id = data.get('audit_id')
            if not audit_id:
                emit('error', {'message': 'audit_id é obrigatório'})
                return
            
            client_id = self._get_client_id()
            room_name = f'audit_{audit_id}'
            
            leave_room(room_name)
            
            if client_id in self.connected_clients:
                rooms = self.connected_clients[client_id]['rooms']
                if room_name in rooms:
                    rooms.remove(room_name)
            
            logger.info(f"Cliente {client_id} saiu da sala {room_name}")
            
            emit('left_audit_room', {
                'audit_id': audit_id,
                'room': room_name,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('request_metrics')
        def handle_request_metrics():
            """Handler para solicitar métricas atuais."""
            client_id = self._get_client_id()
            
            # Aqui você pode integrar com o sistema de métricas
            # Por enquanto, enviamos dados mock
            metrics = self._get_current_metrics()
            
            emit('metrics_update', metrics)
            
            logger.debug(f"Métricas enviadas para cliente {client_id}")
    
    def _get_client_id(self) -> str:
        """
        Obtém ID único do cliente conectado.
        
        Returns:
            ID único do cliente
        """
        from flask import request
        return request.sid if hasattr(request, 'sid') else 'unknown'
    
    def _send_recent_notifications(self, client_id: str) -> None:
        """
        Envia notificações recentes para um cliente específico.
        
        Args:
            client_id: ID do cliente
        """
        # Envia as últimas 10 notificações
        recent_notifications = self.notification_history[-10:]
        
        for notification in recent_notifications:
            self.socketio.emit(
                'notification',
                notification.to_dict(),
                room=client_id
            )
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas atuais do sistema.
        
        Returns:
            Dicionário com métricas atuais
        """
        # Integração com sistema de métricas existente
        # Por enquanto, retorna dados mock
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'disk_usage': 23.1
            },
            'application': {
                'active_audits': 3,
                'completed_audits_today': 15,
                'average_response_time': 245
            },
            'alerts': {
                'active_count': 2,
                'critical_count': 0
            }
        }
    
    def send_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = 'normal',
        room: Optional[str] = None,
        audit_id: Optional[str] = None
    ) -> None:
        """
        Envia notificação para clientes conectados.
        
        Args:
            notification_type: Tipo da notificação
            title: Título da notificação
            message: Mensagem da notificação
            data: Dados adicionais (opcional)
            priority: Prioridade da notificação
            room: Sala específica (opcional)
            audit_id: ID da auditoria (opcional)
        """
        if not self.socketio:
            logger.warning("SocketIO não inicializado")
            return
        
        notification = NotificationMessage(
            id=f"notif_{int(time.time() * 1000)}",
            type=notification_type,
            title=title,
            message=message,
            data=data or {},
            timestamp=datetime.now(),
            priority=priority
        )
        
        # Adiciona ao histórico
        self.notification_history.append(notification)
        
        # Limita o tamanho do histórico
        if len(self.notification_history) > self.max_history_size:
            self.notification_history = self.notification_history[-self.max_history_size:]
        
        # Determina a sala de destino
        target_room = room
        if audit_id:
            target_room = f'audit_{audit_id}'
        elif not target_room:
            target_room = 'general'
        
        # Envia notificação
        self.socketio.emit(
            'notification',
            notification.to_dict(),
            room=target_room
        )
        
        logger.info(f"Notificação enviada: {title} (tipo: {notification_type}, sala: {target_room})")
    
    def send_audit_progress(
        self,
        audit_id: str,
        progress: int,
        stage: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Envia atualização de progresso de auditoria.
        
        Args:
            audit_id: ID da auditoria
            progress: Progresso em porcentagem (0-100)
            stage: Estágio atual da auditoria
            details: Detalhes adicionais (opcional)
        """
        self.send_notification(
            notification_type='audit_progress',
            title=f'Progresso da Auditoria {audit_id[:8]}...',
            message=f'{stage} - {progress}% concluído',
            data={
                'audit_id': audit_id,
                'progress': progress,
                'stage': stage,
                'details': details or {}
            },
            audit_id=audit_id
        )
    
    def send_audit_complete(
        self,
        audit_id: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Envia notificação de auditoria concluída.
        
        Args:
            audit_id: ID da auditoria
            result: Resultado da auditoria
        """
        score = result.get('overall_score', 0)
        
        self.send_notification(
            notification_type='audit_complete',
            title='Auditoria Concluída',
            message=f'Auditoria {audit_id[:8]}... finalizada com score {score}',
            data={
                'audit_id': audit_id,
                'result': result
            },
            priority='high',
            audit_id=audit_id
        )
    
    def send_system_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = 'warning',
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Envia alerta do sistema.
        
        Args:
            alert_type: Tipo do alerta
            message: Mensagem do alerta
            severity: Severidade (info, warning, error, critical)
            data: Dados adicionais (opcional)
        """
        priority_map = {
            'info': 'low',
            'warning': 'normal',
            'error': 'high',
            'critical': 'critical'
        }
        
        self.send_notification(
            notification_type='system_alert',
            title=f'Alerta do Sistema: {alert_type}',
            message=message,
            data={
                'alert_type': alert_type,
                'severity': severity,
                'details': data or {}
            },
            priority=priority_map.get(severity, 'normal')
        )
    
    def send_metrics_update(self, metrics: Dict[str, Any]) -> None:
        """
        Envia atualização de métricas.
        
        Args:
            metrics: Dicionário com métricas atualizadas
        """
        if not self.socketio:
            return
        
        self.socketio.emit('metrics_update', metrics, room='general')
        logger.debug("Métricas atualizadas enviadas")
    
    def get_connected_clients_count(self) -> int:
        """
        Retorna o número de clientes conectados.
        
        Returns:
            Número de clientes conectados
        """
        return len(self.connected_clients)
    
    def get_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna histórico de notificações.
        
        Args:
            limit: Limite de notificações a retornar
            
        Returns:
            Lista de notificações
        """
        recent_notifications = self.notification_history[-limit:]
        return [notif.to_dict() for notif in recent_notifications]


# Instância global do gerenciador
websocket_manager = WebSocketManager()


def init_websockets(app: Flask) -> WebSocketManager:
    """
    Inicializa o sistema de WebSockets na aplicação Flask.
    
    Args:
        app: Instância Flask
        
    Returns:
        Instância do WebSocketManager
    """
    websocket_manager.init_app(app)
    logger.info("Sistema de WebSockets inicializado")
    return websocket_manager