"""
Sistema de logging robusto para produção do Sistema de Auditoria SEO.

Este módulo configura logging estruturado com rotação de arquivos,
diferentes níveis de log e formatação adequada para monitoramento.
Inclui suporte para correlação de requests, métricas de performance,
e integração com sistemas de monitoramento externos.
"""

import logging
import logging.handlers
import os
import sys
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
import structlog
from structlog.stdlib import LoggerFactory
from flask import request, g, has_request_context


# Thread-local storage para contexto de logging
_context = threading.local()


def get_request_id() -> str:
    """
    Obtém ou gera um ID único para a requisição atual.
    
    Returns:
        ID único da requisição
    """
    if has_request_context():
        if not hasattr(g, 'request_id'):
            g.request_id = str(uuid.uuid4())
        return g.request_id
    
    # Fallback para contextos sem Flask
    if not hasattr(_context, 'request_id'):
        _context.request_id = str(uuid.uuid4())
    return _context.request_id


def get_correlation_id() -> Optional[str]:
    """
    Obtém o ID de correlação da requisição atual.
    
    Returns:
        ID de correlação se disponível
    """
    if has_request_context():
        return request.headers.get('X-Correlation-ID') or getattr(g, 'correlation_id', None)
    return getattr(_context, 'correlation_id', None)


def set_correlation_id(correlation_id: str) -> None:
    """
    Define o ID de correlação para o contexto atual.
    
    Args:
        correlation_id: ID de correlação a ser definido
    """
    if has_request_context():
        g.correlation_id = correlation_id
    else:
        _context.correlation_id = correlation_id


class JSONFormatter(logging.Formatter):
    """
    Formatador JSON para logs estruturados em produção.
    
    Converte logs em formato JSON para facilitar parsing e análise
    por ferramentas de monitoramento como ELK Stack, Splunk, etc.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o log record em JSON estruturado.
        
        Args:
            record: Record do log a ser formatado
            
        Returns:
            String JSON formatada
        """
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": os.getpid(),
            "thread_id": record.thread,
            "request_id": get_request_id(),
        }
        
        # Adiciona ID de correlação se disponível
        correlation_id = get_correlation_id()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id
        
        # Adiciona informações de contexto Flask se disponível
        if has_request_context():
            try:
                log_entry.update({
                    "method": request.method,
                    "path": request.path,
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', ''),
                })
            except Exception:
                pass  # Ignora erros de contexto
        
        # Adiciona informações de exceção se presente
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Adiciona campos extras se presentes
        extra_fields = ['audit_id', 'user_ip', 'duration', 'operation', 
                       'status_code', 'response_size', 'cache_hit', 'db_queries']
        
        for field in extra_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ProductionFormatter(logging.Formatter):
    """
    Formatador para logs em produção com informações essenciais.
    
    Formato otimizado para leitura humana em produção,
    incluindo informações de contexto importantes.
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class DevelopmentFormatter(logging.Formatter):
    """
    Formatador para desenvolvimento com cores e informações detalhadas.
    
    Inclui cores para facilitar identificação visual dos níveis de log
    durante desenvolvimento e debugging.
    """
    
    # Códigos de cor ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Ciano
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarelo
        'ERROR': '\033[31m',      # Vermelho
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def format(self, record: logging.LogRecord) -> str:
        """Adiciona cores ao log para desenvolvimento."""
        if sys.stdout.isatty():  # Só adiciona cores se for terminal
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class AuditLoggerAdapter(logging.LoggerAdapter):
    """
    Adapter para adicionar contexto de auditoria aos logs.
    
    Automaticamente adiciona audit_id e outras informações
    contextuais relevantes aos logs.
    """
    
    def __init__(self, logger: logging.Logger, audit_id: Optional[str] = None):
        """
        Inicializa o adapter com contexto de auditoria.
        
        Args:
            logger: Logger base
            audit_id: ID da auditoria para contexto
        """
        super().__init__(logger, {"audit_id": audit_id})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Processa a mensagem adicionando contexto.
        
        Args:
            msg: Mensagem do log
            kwargs: Argumentos adicionais
            
        Returns:
            Tupla com mensagem processada e kwargs
        """
        if self.extra.get("audit_id"):
            msg = f"[{self.extra['audit_id']}] {msg}"
        
        return msg, kwargs


def setup_logging(
    environment: str = "development",
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    enable_json: bool = False,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configura o sistema de logging para a aplicação.
    
    Args:
        environment: Ambiente (development, production, testing)
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Diretório para arquivos de log
        enable_json: Se deve usar formatação JSON
        max_file_size: Tamanho máximo do arquivo de log em bytes
        backup_count: Número de arquivos de backup a manter
    """
    # Configura diretório de logs
    if log_dir is None:
        log_dir = os.getenv('LOG_DIR', 'logs')
    
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Converte string de nível para constante
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Remove handlers existentes
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura formatadores baseado no ambiente
    if environment == "production" or enable_json:
        formatter = JSONFormatter()
        console_formatter = ProductionFormatter()
    else:
        formatter = DevelopmentFormatter()
        console_formatter = formatter
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    
    # Handler para arquivo principal com rotação
    main_log_file = log_path / "app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    
    # Handler para erros separado
    error_log_file = log_path / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler para auditoria separado
    audit_log_file = log_path / "audit.log"
    audit_handler = logging.handlers.RotatingFileHandler(
        audit_log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(formatter)
    
    # Configura logger raiz
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configura logger específico para auditoria
    audit_logger = logging.getLogger('audit')
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False  # Não propaga para o logger raiz
    
    # Configura loggers de bibliotecas externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Configura structlog se disponível
    try:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    except Exception as e:
        logging.getLogger(__name__).warning(f"Falha ao configurar structlog: {e}")
    
    logging.getLogger(__name__).info(
        f"Sistema de logging configurado - Ambiente: {environment}, "
        f"Nível: {log_level}, Diretório: {log_path}"
    )


def get_audit_logger(audit_id: str) -> AuditLoggerAdapter:
    """
    Retorna um logger com contexto de auditoria.
    
    Args:
        audit_id: ID da auditoria para contexto
        
    Returns:
        Logger adapter com contexto de auditoria
    """
    base_logger = logging.getLogger('audit')
    return AuditLoggerAdapter(base_logger, audit_id)


def log_request_info(logger: logging.Logger, request_data: Dict[str, Any]) -> None:
    """
    Loga informações de requisição HTTP de forma estruturada.
    
    Args:
        logger: Logger a ser usado
        request_data: Dados da requisição
    """
    logger.info(
        "HTTP Request",
        extra={
            "method": request_data.get("method"),
            "path": request_data.get("path"),
            "user_ip": request_data.get("remote_addr"),
            "user_agent": request_data.get("user_agent"),
            "request_id": request_data.get("request_id")
        }
    )


def log_performance_metric(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    **kwargs
) -> None:
    """
    Loga métricas de performance de forma estruturada.
    
    Args:
        logger: Logger a ser usado
        operation: Nome da operação
        duration_ms: Duração em milissegundos
        **kwargs: Dados adicionais
    """
    logger.info(
        f"Performance: {operation}",
        extra={
            "operation": operation,
            "duration": duration_ms,  # Mudança: removido _ms do nome
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
            **kwargs
        }
    )


def log_api_call(
    logger: logging.Logger,
    api_name: str,
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    **kwargs
) -> None:
    """
    Loga chamadas de API externa de forma estruturada.
    
    Args:
        logger: Logger a ser usado
        api_name: Nome da API (ex: 'google_analytics')
        method: Método HTTP
        url: URL da API
        status_code: Código de status da resposta
        duration_ms: Duração da chamada em milissegundos
        **kwargs: Dados adicionais
    """
    logger.info(
        f"API Call: {api_name}",
        extra={
            "operation": f"api_call_{api_name}",
            "api_name": api_name,
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration": duration_ms,
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
            **kwargs
        }
    )


def log_cache_operation(
    logger: logging.Logger,
    operation: str,
    cache_type: str,
    key: str,
    hit: bool,
    duration_ms: Optional[float] = None,
    **kwargs
) -> None:
    """
    Loga operações de cache de forma estruturada.
    
    Args:
        logger: Logger a ser usado
        operation: Tipo de operação (get, set, delete)
        cache_type: Tipo de cache (redis, memory, disk)
        key: Chave do cache
        hit: Se foi um cache hit (para operações get)
        duration_ms: Duração da operação
        **kwargs: Dados adicionais
    """
    logger.info(
        f"Cache {operation}: {cache_type}",
        extra={
            "operation": f"cache_{operation}",
            "cache_type": cache_type,
            "cache_key": key,
            "cache_hit": hit,
            "duration": duration_ms,
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
            **kwargs
        }
    )


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    duration_ms: float,
    rows_affected: Optional[int] = None,
    **kwargs
) -> None:
    """
    Loga operações de banco de dados de forma estruturada.
    
    Args:
        logger: Logger a ser usado
        operation: Tipo de operação (SELECT, INSERT, UPDATE, DELETE)
        table: Nome da tabela
        duration_ms: Duração da operação
        rows_affected: Número de linhas afetadas
        **kwargs: Dados adicionais
    """
    logger.info(
        f"DB {operation}: {table}",
        extra={
            "operation": f"db_{operation.lower()}",
            "db_table": table,
            "db_operation": operation,
            "duration": duration_ms,
            "rows_affected": rows_affected,
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
            **kwargs
        }
    )


# Configuração padrão baseada em variáveis de ambiente
def configure_default_logging() -> None:
    """Configura logging com valores padrão das variáveis de ambiente."""
    environment = os.getenv('FLASK_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_dir = os.getenv('LOG_DIR', 'logs')
    enable_json = os.getenv('LOG_FORMAT', '').lower() == 'json'
    
    setup_logging(
        environment=environment,
        log_level=log_level,
        log_dir=log_dir,
        enable_json=enable_json
    )