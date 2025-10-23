"""
Sistema robusto de tratamento de erros para o Sistema de Auditoria SEO.

Este módulo define handlers de erro personalizados, validações de entrada
e classes de exceção customizadas para melhor controle de erros em produção.
"""

import logging
import traceback
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional, Callable, Union, List
from flask import Flask, request, jsonify, g
import uuid
import time

from .logging_config import get_audit_logger

# Logger para este módulo
logger = get_audit_logger(__name__)


# Contador global para gerar nomes únicos de funções
_function_counter = 0

def _get_unique_function_name(base_name: str) -> str:
    """Gera um nome único para função baseado no nome base."""
    global _function_counter
    _function_counter += 1
    return f"{base_name}_{_function_counter}"


# Classes de exceção customizadas
class AuditSystemError(Exception):
    """Exceção base para erros do sistema de auditoria."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        """
        Inicializa exceção customizada.
        
        Args:
            message: Mensagem de erro
            error_code: Código de erro único
            details: Detalhes adicionais do erro
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "AUDIT_SYSTEM_ERROR"
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()


class ValidationError(AuditSystemError):
    """Exceção para erros de validação de entrada."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        """
        Inicializa erro de validação.
        
        Args:
            message: Mensagem de erro
            field: Campo que falhou na validação
            value: Valor que causou o erro
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["invalid_value"] = str(value)
        
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value


class ExternalAPIError(AuditSystemError):
    """Exceção para erros de APIs externas."""
    
    def __init__(self, message: str, api_name: str, status_code: int = None, response: str = None):
        """
        Inicializa erro de API externa.
        
        Args:
            message: Mensagem de erro
            api_name: Nome da API que falhou
            status_code: Código de status HTTP
            response: Resposta da API
        """
        details = {
            "api_name": api_name,
            "status_code": status_code,
            "response": response
        }
        
        super().__init__(message, "EXTERNAL_API_ERROR", details)
        self.api_name = api_name
        self.status_code = status_code


class DatabaseError(AuditSystemError):
    """Exceção para erros de banco de dados."""
    
    def __init__(self, message: str, operation: str = None, table: str = None):
        """
        Inicializa erro de banco de dados.
        
        Args:
            message: Mensagem de erro
            operation: Operação que falhou (SELECT, INSERT, etc.)
            table: Tabela envolvida no erro
        """
        details = {
            "operation": operation,
            "table": table
        }
        
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation
        self.table = table


class RateLimitError(AuditSystemError):
    """Exceção para erros de rate limiting."""
    
    def __init__(self, message: str, limit: int, window: int, retry_after: int = None):
        """
        Inicializa erro de rate limit.
        
        Args:
            message: Mensagem de erro
            limit: Limite de requisições
            window: Janela de tempo em segundos
            retry_after: Tempo para tentar novamente
        """
        details = {
            "limit": limit,
            "window": window,
            "retry_after": retry_after
        }
        
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.retry_after = retry_after


# Validadores de entrada
class InputValidator:
    """Classe para validação de entradas da API."""
    
    @staticmethod
    def validate_url(url: str) -> str:
        """
        Valida e normaliza uma URL.
        
        Args:
            url: URL a ser validada
            
        Returns:
            URL normalizada
            
        Raises:
            ValidationError: Se a URL for inválida
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL é obrigatória e deve ser uma string", "url", url)
        
        url = url.strip()
        
        if not url:
            raise ValidationError("URL não pode estar vazia", "url", url)
        
        # Adiciona protocolo se não presente
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # Validação básica de formato
        import re
        url_pattern = re.compile(
            r'^https?://'  # protocolo
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domínio
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # porta opcional
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            raise ValidationError("Formato de URL inválido", "url", url)
        
        return url
    
    @staticmethod
    def validate_audit_id(audit_id: str) -> str:
        """
        Valida um ID de auditoria.
        
        Args:
            audit_id: ID a ser validado
            
        Returns:
            ID validado
            
        Raises:
            ValidationError: Se o ID for inválido
        """
        if not audit_id or not isinstance(audit_id, str):
            raise ValidationError("ID de auditoria é obrigatório", "audit_id", audit_id)
        
        audit_id = audit_id.strip()
        
        if not audit_id:
            raise ValidationError("ID de auditoria não pode estar vazio", "audit_id", audit_id)
        
        # Valida formato UUID
        try:
            uuid.UUID(audit_id)
        except ValueError:
            raise ValidationError("ID de auditoria deve ser um UUID válido", "audit_id", audit_id)
        
        return audit_id
    
    @staticmethod
    def validate_pagination(page: Any, limit: Any) -> tuple[int, int]:
        """
        Valida parâmetros de paginação.
        
        Args:
            page: Número da página
            limit: Limite de itens por página
            
        Returns:
            Tupla com página e limite validados
            
        Raises:
            ValidationError: Se os parâmetros forem inválidos
        """
        # Valida página
        try:
            page = int(page) if page is not None else 1
        except (ValueError, TypeError):
            raise ValidationError("Página deve ser um número inteiro", "page", page)
        
        if page < 1:
            raise ValidationError("Página deve ser maior que 0", "page", page)
        
        # Valida limite
        try:
            limit = int(limit) if limit is not None else 10
        except (ValueError, TypeError):
            raise ValidationError("Limite deve ser um número inteiro", "limit", limit)
        
        if limit < 1:
            raise ValidationError("Limite deve ser maior que 0", "limit", limit)
        
        if limit > 100:
            raise ValidationError("Limite não pode ser maior que 100", "limit", limit)
        
        return page, limit
    
    @staticmethod
    def validate_json_payload(data: Any, required_fields: List[str] = None) -> Dict[str, Any]:
        """
        Valida payload JSON.
        
        Args:
            data: Dados a serem validados
            required_fields: Lista de campos obrigatórios
            
        Returns:
            Dados validados
            
        Raises:
            ValidationError: Se os dados forem inválidos
        """
        if not isinstance(data, dict):
            raise ValidationError("Payload deve ser um objeto JSON válido", "payload", type(data).__name__)
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(
                    f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",
                    "required_fields",
                    missing_fields
                )
        
        return data


# Decoradores para tratamento de erros
def handle_errors(func: Callable) -> Callable:
    """
    Decorator para tratamento centralizado de erros.
    
    Args:
        func: Função a ser decorada
        
    Returns:
        Função decorada com tratamento de erros
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Log da requisição
            if hasattr(g, 'request_id'):
                logger.info(f"[{g.request_id}] Executando {func.__name__}")
            
            return func(*args, **kwargs)
            
        except ValidationError as e:
            error_id = str(uuid.uuid4())
            logger.warning(f"[{error_id}] Erro de validação em {func.__name__}: {str(e)}")
            return jsonify({
                'error': 'Erro de validação',
                'message': str(e),
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
        except ExternalAPIError as e:
            error_id = str(uuid.uuid4())
            logger.error(f"[{error_id}] Erro de API externa em {func.__name__}: {str(e)}")
            return jsonify({
                'error': 'Erro de serviço externo',
                'message': 'Falha na comunicação com serviço externo',
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 502
            
        except DatabaseError as e:
            error_id = str(uuid.uuid4())
            logger.error(f"[{error_id}] Erro de banco de dados em {func.__name__}: {str(e)}")
            return jsonify({
                'error': 'Erro de banco de dados',
                'message': 'Falha na operação de banco de dados',
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 500
            
        except AuditSystemError as e:
            error_id = str(uuid.uuid4())
            logger.error(f"[{error_id}] Erro do sistema de auditoria em {func.__name__}: {str(e)}")
            return jsonify({
                'error': 'Erro do sistema',
                'message': str(e),
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 500
            
        except Exception as e:
            error_id = str(uuid.uuid4())
            logger.error(f"[{error_id}] Erro não tratado em {func.__name__}: {str(e)}")
            logger.error(f"[{error_id}] Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Erro interno do servidor',
                'message': 'Ocorreu um erro inesperado',
                'error_id': error_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    # Preservar metadados da função original
    wrapper.__name__ = func.__name__
    wrapper.__qualname__ = func.__qualname__
    wrapper.__module__ = func.__module__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__
    
    return wrapper


def validate_input(schema: Dict[str, Any]) -> Callable:
    """
    Decorator para validação de entrada de dados.
    
    Args:
        schema: Schema de validação
        
    Returns:
        Decorator que valida os dados de entrada
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Validar dados da requisição
                data = request.get_json() if request.is_json else request.form.to_dict()
                
                # Aplicar validação do schema
                validator = InputValidator(schema)
                validated_data = validator.validate(data)
                
                # Adicionar dados validados aos kwargs
                kwargs['validated_data'] = validated_data
                
                return func(*args, **kwargs)
                
            except ValidationError:
                raise  # Re-raise para ser tratado pelo handle_errors
            except Exception as e:
                raise ValidationError(f"Erro na validação de entrada: {str(e)}")
        
        return wrapper
    return decorator


# Handlers de erro globais para Flask
def register_error_handlers(app: Flask) -> None:
    """
    Registra handlers de erro globais na aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    logger = logging.getLogger(__name__)
    
    @app.errorhandler(404)
    def not_found(error):
        """Handler para erro 404."""
        request_id = getattr(g, 'request_id', str(uuid.uuid4()))
        
        logger.warning(
            f"404 Not Found: {request.path}",
            extra={
                "request_id": request_id,
                "path": request.path,
                "method": request.method,
                "remote_addr": request.remote_addr
            }
        )
        
        return jsonify({
            "error": "Endpoint não encontrado",
            "error_code": "NOT_FOUND",
            "path": request.path,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handler para erro 405."""
        request_id = getattr(g, 'request_id', str(uuid.uuid4()))
        
        logger.warning(
            f"405 Method Not Allowed: {request.method} {request.path}",
            extra={
                "request_id": request_id,
                "path": request.path,
                "method": request.method,
                "remote_addr": request.remote_addr
            }
        )
        
        return jsonify({
            "error": f"Método {request.method} não permitido para este endpoint",
            "error_code": "METHOD_NOT_ALLOWED",
            "method": request.method,
            "path": request.path,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 405
    
    @app.errorhandler(413)
    def payload_too_large(error):
        """Handler para erro 413."""
        request_id = getattr(g, 'request_id', str(uuid.uuid4()))
        
        logger.warning(
            f"413 Payload Too Large: {request.path}",
            extra={
                "request_id": request_id,
                "path": request.path,
                "content_length": request.content_length
            }
        )
        
        return jsonify({
            "error": "Payload muito grande",
            "error_code": "PAYLOAD_TOO_LARGE",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 413
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handler para erro 500."""
        request_id = getattr(g, 'request_id', str(uuid.uuid4()))
        
        logger.error(
            f"500 Internal Server Error: {request.path}",
            extra={
                "request_id": request_id,
                "path": request.path,
                "method": request.method,
                "error": str(error),
                "traceback": traceback.format_exc()
            }
        )
        
        return jsonify({
            "error": "Erro interno do servidor",
            "error_code": "INTERNAL_SERVER_ERROR",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 500


# Middleware para adicionar request ID
def add_request_id_middleware(app: Flask) -> None:
    """
    Adiciona middleware para gerar request ID único.
    
    Args:
        app: Instância da aplicação Flask
    """
    @app.before_request
    def before_request():
        """Gera request ID único para cada requisição."""
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Adiciona headers de resposta e log de performance."""
        request_id = getattr(g, 'request_id', 'unknown')
        start_time = getattr(g, 'start_time', time.time())
        
        # Adiciona request ID ao header
        response.headers['X-Request-ID'] = request_id
        
        # Log de performance
        duration = (time.time() - start_time) * 1000
        logger = logging.getLogger(__name__)
        
        logger.info(
            f"Request completed: {request.method} {request.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get('User-Agent', '')
            }
        )
        
        return response