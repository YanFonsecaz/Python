"""
Middleware para logging estruturado e correlação de requests.

Este módulo implementa middleware Flask para capturar automaticamente
informações de requisições, gerar IDs de correlação e logar métricas
de performance de forma estruturada.
"""

import time
import uuid
from typing import Optional
from flask import Flask, request, g, jsonify
from werkzeug.exceptions import HTTPException
import logging

from app.logging_config import (
    get_request_id, 
    set_correlation_id, 
    log_request_info, 
    log_performance_metric
)
from app.performance_monitor import get_performance_collector

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware para logging automático de requisições HTTP.
    
    Captura informações de cada requisição, gera IDs únicos,
    e loga métricas de performance automaticamente.
    """
    
    def __init__(self, app: Optional[Flask] = None):
        """
        Inicializa o middleware.
        
        Args:
            app: Instância Flask (opcional)
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Configura o middleware na aplicação Flask.
        
        Args:
            app: Instância Flask
        """
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.errorhandler(Exception)(self._handle_exception)
    
    def _before_request(self) -> None:
        """
        Executado antes de cada requisição.
        
        Gera IDs únicos, configura contexto de logging
        e registra início da requisição.
        """
        # Gera ou obtém ID de correlação
        correlation_id = request.headers.get('X-Correlation-ID')
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        # Marca início da requisição
        g.start_time = time.time()
        
        # Registra início da requisição no monitor de performance
        performance_collector = get_performance_collector()
        performance_collector.record_request_start()
        
        # Loga informações da requisição
        request_data = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent', ''),
            "request_id": get_request_id(),
            "correlation_id": correlation_id,
            "content_length": request.content_length or 0,
            "query_params": dict(request.args)
        }
        
        log_request_info(logger, request_data)
    
    def _after_request(self, response) -> object:
        """
        Executado após cada requisição.
        
        Args:
            response: Resposta HTTP
            
        Returns:
            Resposta HTTP modificada
        """
        # Calcula duração da requisição
        duration_ms = (time.time() - g.start_time) * 1000
        
        # Registra fim da requisição no monitor de performance
        performance_collector = get_performance_collector()
        performance_collector.record_request_end(
            endpoint=request.endpoint or request.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        # Adiciona headers de correlação
        response.headers['X-Request-ID'] = get_request_id()
        correlation_id = getattr(g, 'correlation_id', None)
        if correlation_id:
            response.headers['X-Correlation-ID'] = correlation_id
        
        # Loga métricas de performance
        log_performance_metric(
            logger,
            operation=f"{request.method} {request.path}",
            duration_ms=duration_ms,
            status_code=response.status_code,
            response_size=len(response.get_data()) if response.get_data() else 0,
            method=request.method,
            path=request.path,
            endpoint=request.endpoint
        )
        
        return response
    
    def _handle_exception(self, error: Exception) -> object:
        """
        Manipula exceções não tratadas.
        
        Args:
            error: Exceção capturada
            
        Returns:
            Resposta de erro JSON
        """
        # Calcula duração até o erro
        duration_ms = (time.time() - getattr(g, 'start_time', time.time())) * 1000
        
        # Determina código de status
        if isinstance(error, HTTPException):
            status_code = error.code
            message = error.description
        else:
            status_code = 500
            message = "Erro interno do servidor"
        
        # Registra erro no monitor de performance
        performance_collector = get_performance_collector()
        performance_collector.record_error(
            endpoint=request.endpoint or request.path,
            method=request.method,
            error_type=type(error).__name__,
            status_code=status_code
        )
        
        # Loga o erro
        logger.error(
            f"Request failed: {message}",
            extra={
                "operation": f"{request.method} {request.path}",
                "duration": duration_ms,
                "status_code": status_code,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "method": request.method,
                "path": request.path,
                "endpoint": request.endpoint
            },
            exc_info=True
        )
        
        # Retorna resposta de erro estruturada
        response_data = {
            "error": message,
            "request_id": get_request_id(),
            "timestamp": time.time()
        }
        
        # Adiciona detalhes em desenvolvimento
        if logger.isEnabledFor(logging.DEBUG):
            response_data["error_type"] = type(error).__name__
            response_data["error_details"] = str(error)
        
        response = jsonify(response_data)
        response.status_code = status_code
        
        # Adiciona headers de correlação
        response.headers['X-Request-ID'] = get_request_id()
        correlation_id = getattr(g, 'correlation_id', None)
        if correlation_id:
            response.headers['X-Correlation-ID'] = correlation_id
        
        return response


def setup_request_logging(app: Flask) -> RequestLoggingMiddleware:
    """
    Configura middleware de logging para a aplicação.
    
    Args:
        app: Instância Flask
        
    Returns:
        Instância do middleware configurado
    """
    middleware = RequestLoggingMiddleware(app)
    logger.info("Middleware de logging de requisições configurado")
    return middleware