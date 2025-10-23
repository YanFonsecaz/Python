"""
Sistema de segurança para o Sistema de Auditoria SEO.

Este módulo implementa medidas de segurança incluindo rate limiting,
validação de CORS, sanitização de entrada e proteções contra ataques comuns.
"""

import logging
import time
import hashlib
import re
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List, Callable, Tuple
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import ipaddress
import os
from urllib.parse import urlparse

from .error_handlers import RateLimitError, ValidationError


class RateLimiter:
    """
    Sistema de rate limiting baseado em sliding window.
    
    Implementa controle de taxa de requisições por IP e endpoint
    para prevenir abuso e ataques DDoS.
    """
    
    def __init__(self):
        """Inicializa o rate limiter."""
        self.requests = defaultdict(lambda: defaultdict(deque))
        self.blocked_ips = {}
        self.logger = logging.getLogger(__name__)
    
    def is_allowed(
        self,
        identifier: str,
        limit: int,
        window: int,
        endpoint: str = "global"
    ) -> Tuple[bool, Optional[int]]:
        """
        Verifica se uma requisição é permitida.
        
        Args:
            identifier: Identificador único (geralmente IP)
            limit: Número máximo de requisições
            window: Janela de tempo em segundos
            endpoint: Endpoint específico (opcional)
            
        Returns:
            Tupla (permitido, tempo_para_retry)
        """
        current_time = time.time()
        
        # Verifica se IP está bloqueado
        if identifier in self.blocked_ips:
            block_until = self.blocked_ips[identifier]
            if current_time < block_until:
                return False, int(block_until - current_time)
            else:
                # Remove bloqueio expirado
                del self.blocked_ips[identifier]
        
        # Limpa requisições antigas
        request_times = self.requests[identifier][endpoint]
        cutoff_time = current_time - window
        
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Verifica limite
        if len(request_times) >= limit:
            # Calcula tempo para retry
            oldest_request = request_times[0]
            retry_after = int(oldest_request + window - current_time) + 1
            
            # Bloqueia IP se exceder muito o limite
            if len(request_times) > limit * 2:
                self.blocked_ips[identifier] = current_time + (window * 2)
                self.logger.warning(
                    f"IP {identifier} bloqueado por excesso de requisições",
                    extra={
                        "ip": identifier,
                        "endpoint": endpoint,
                        "requests_count": len(request_times),
                        "limit": limit
                    }
                )
            
            return False, retry_after
        
        # Adiciona requisição atual
        request_times.append(current_time)
        return True, None
    
    def cleanup_old_entries(self, max_age: int = 3600) -> None:
        """
        Remove entradas antigas para economizar memória.
        
        Args:
            max_age: Idade máxima em segundos
        """
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        # Limpa requisições antigas
        for identifier in list(self.requests.keys()):
            for endpoint in list(self.requests[identifier].keys()):
                request_times = self.requests[identifier][endpoint]
                while request_times and request_times[0] < cutoff_time:
                    request_times.popleft()
                
                # Remove endpoint se vazio
                if not request_times:
                    del self.requests[identifier][endpoint]
            
            # Remove identificador se vazio
            if not self.requests[identifier]:
                del self.requests[identifier]
        
        # Limpa bloqueios expirados
        expired_blocks = [
            ip for ip, block_until in self.blocked_ips.items()
            if current_time >= block_until
        ]
        for ip in expired_blocks:
            del self.blocked_ips[ip]


class SecurityValidator:
    """Validador de segurança para entradas e requisições."""
    
    # Padrões de ataques comuns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+[\'"]?\w+[\'"]?\s*=\s*[\'"]?\w+[\'"]?)',
        r'(--|#|/\*|\*/)',
        r'(\bUNION\s+SELECT\b)',
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$(){}[\]\\]',
        r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b',
        r'(\.\.\/|\.\.\\)',
    ]
    
    def __init__(self):
        """Inicializa o validador de segurança."""
        self.logger = logging.getLogger(__name__)
        
        # Compila padrões regex para performance
        self.xss_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.XSS_PATTERNS]
        self.sql_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.SQL_INJECTION_PATTERNS]
        self.cmd_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.COMMAND_INJECTION_PATTERNS]
    
    def validate_input(self, value: str, field_name: str = "input") -> str:
        """
        Valida e sanitiza entrada do usuário.
        
        Args:
            value: Valor a ser validado
            field_name: Nome do campo para logs
            
        Returns:
            Valor sanitizado
            
        Raises:
            ValidationError: Se entrada for maliciosa
        """
        if not isinstance(value, str):
            return value
        
        original_value = value
        
        # Detecta XSS
        for pattern in self.xss_regex:
            if pattern.search(value):
                self.logger.warning(
                    f"Tentativa de XSS detectada no campo {field_name}",
                    extra={
                        "field": field_name,
                        "value": value[:100],  # Limita tamanho do log
                        "remote_addr": request.remote_addr if request else "unknown"
                    }
                )
                raise ValidationError(
                    f"Entrada inválida detectada no campo {field_name}",
                    field_name,
                    "XSS_ATTEMPT"
                )
        
        # Detecta SQL Injection
        for pattern in self.sql_regex:
            if pattern.search(value):
                self.logger.warning(
                    f"Tentativa de SQL Injection detectada no campo {field_name}",
                    extra={
                        "field": field_name,
                        "value": value[:100],
                        "remote_addr": request.remote_addr if request else "unknown"
                    }
                )
                raise ValidationError(
                    f"Entrada inválida detectada no campo {field_name}",
                    field_name,
                    "SQL_INJECTION_ATTEMPT"
                )
        
        # Detecta Command Injection
        for pattern in self.cmd_regex:
            if pattern.search(value):
                self.logger.warning(
                    f"Tentativa de Command Injection detectada no campo {field_name}",
                    extra={
                        "field": field_name,
                        "value": value[:100],
                        "remote_addr": request.remote_addr if request else "unknown"
                    }
                )
                raise ValidationError(
                    f"Entrada inválida detectada no campo {field_name}",
                    field_name,
                    "COMMAND_INJECTION_ATTEMPT"
                )
        
        # Sanitização básica
        value = value.strip()
        
        # Remove caracteres de controle
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        return value
    
    def validate_url_safety(self, url: str) -> bool:
        """
        Valida se uma URL é segura para processamento.
        
        Args:
            url: URL a ser validada
            
        Returns:
            True se URL for segura
        """
        try:
            parsed = urlparse(url)
            
            # Verifica protocolo
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Verifica se não é IP privado (para evitar SSRF)
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
            except (ValueError, TypeError):
                # Não é IP, continua validação
                pass
            
            # Verifica domínios suspeitos
            suspicious_domains = [
                'localhost',
                '127.0.0.1',
                '0.0.0.0',
                '::1',
                'metadata.google.internal',
                '169.254.169.254'  # AWS metadata
            ]
            
            if parsed.hostname and parsed.hostname.lower() in suspicious_domains:
                return False
            
            return True
            
        except Exception:
            return False
    
    def validate_file_upload(self, filename: str, content: bytes) -> bool:
        """
        Valida upload de arquivo.
        
        Args:
            filename: Nome do arquivo
            content: Conteúdo do arquivo
            
        Returns:
            True se arquivo for seguro
        """
        # Extensões permitidas
        allowed_extensions = {'.txt', '.csv', '.json', '.xml', '.pdf', '.docx'}
        
        # Verifica extensão
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in allowed_extensions:
            return False
        
        # Verifica tamanho (máximo 10MB)
        if len(content) > 10 * 1024 * 1024:
            return False
        
        # Verifica assinaturas de arquivo malicioso
        malicious_signatures = [
            b'\x4D\x5A',  # PE executable
            b'\x7F\x45\x4C\x46',  # ELF executable
            b'\xCA\xFE\xBA\xBE',  # Java class
            b'\x50\x4B\x03\x04',  # ZIP (pode conter executáveis)
        ]
        
        for signature in malicious_signatures:
            if content.startswith(signature):
                return False
        
        return True


class IPWhitelist:
    """Sistema de whitelist de IPs para endpoints administrativos."""
    
    def __init__(self, whitelist: List[str] = None):
        """
        Inicializa whitelist de IPs.
        
        Args:
            whitelist: Lista de IPs ou redes permitidas
        """
        self.whitelist = set()
        self.networks = []
        
        if whitelist:
            for ip_or_network in whitelist:
                try:
                    # Tenta como rede
                    network = ipaddress.ip_network(ip_or_network, strict=False)
                    self.networks.append(network)
                except ValueError:
                    # Trata como IP individual
                    self.whitelist.add(ip_or_network)
    
    def is_allowed(self, ip: str) -> bool:
        """
        Verifica se IP está na whitelist.
        
        Args:
            ip: IP a ser verificado
            
        Returns:
            True se IP for permitido
        """
        if ip in self.whitelist:
            return True
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            for network in self.networks:
                if ip_obj in network:
                    return True
        except ValueError:
            pass
        
        return False


# Instâncias globais
rate_limiter = RateLimiter()
security_validator = SecurityValidator()

# Flag global para controlar se a thread de limpeza já foi iniciada
_cleanup_thread_started = False


def rate_limit(limit: int = 200, window: int = 60, per_endpoint: bool = True):
    """
    Decorator para aplicar rate limiting a endpoints
    
    Args:
        limit: Número máximo de requisições permitidas
        window: Janela de tempo em segundos
        per_endpoint: Se True, aplica limite por endpoint; se False, global
    """
    def rate_limit_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtém informações do cliente
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            user_agent = request.headers.get('User-Agent', '')
            identifier = hashlib.md5(f"{client_ip}:{user_agent}".encode()).hexdigest()
            
            # Define endpoint
            endpoint = func.__name__ if per_endpoint else "global"
            
            # Verifica rate limit
            allowed, retry_after = rate_limiter.is_allowed(identifier, limit, window, endpoint)
            
            if not allowed:
                raise RateLimitError(
                    f"Limite de {limit} requisições por {window} segundos excedido",
                    limit,
                    window,
                    retry_after
                )
            
            return func(*args, **kwargs)
        return wrapper
    return rate_limit_decorator


def validate_security(validate_url: bool = False, validate_json: bool = False):
    """
    Decorador para validação de segurança.
    
    Args:
        validate_url: Se deve validar URLs nos parâmetros
        validate_json: Se deve validar JSON payload
    """
    def validate_security_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Valida parâmetros da URL
            for key, value in request.args.items():
                if isinstance(value, str):
                    kwargs[key] = security_validator.validate_input(value, key)
            
            # Valida parâmetros da rota
            for key, value in kwargs.items():
                if isinstance(value, str):
                    kwargs[key] = security_validator.validate_input(value, key)
            
            # Valida JSON payload se necessário
            if validate_json and request.is_json:
                json_data = request.get_json()
                if json_data:
                    for key, value in json_data.items():
                        if isinstance(value, str):
                            json_data[key] = security_validator.validate_input(value, key)
            
            # Valida URLs se necessário
            if validate_url:
                url_param = request.args.get('url') or kwargs.get('url')
                if url_param and not security_validator.validate_url_safety(url_param):
                    raise ValidationError("URL não é segura para processamento", "url", url_param)
            
            return func(*args, **kwargs)
        return wrapper
    return validate_security_decorator


def require_ip_whitelist(whitelist: List[str]):
    """
    Decorador para restringir acesso por IP.
    
    Args:
        whitelist: Lista de IPs permitidos
    """
    ip_whitelist = IPWhitelist(whitelist)
    
    def ip_whitelist_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            
            if not ip_whitelist.is_allowed(client_ip):
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Acesso negado para IP não autorizado: {client_ip}",
                    extra={
                        "ip": client_ip,
                        "endpoint": func.__name__,
                        "user_agent": request.headers.get('User-Agent', '')
                    }
                )
                
                return jsonify({
                    "error": "Acesso negado",
                    "error_code": "ACCESS_DENIED"
                }), 403
            
            return func(*args, **kwargs)
        return wrapper
    return ip_whitelist_decorator


def setup_security(app: Flask) -> None:
    """
    Configura medidas de segurança na aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    logger = logging.getLogger(__name__)
    
    # Configura CORS
    allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    CORS(app, 
         origins=allowed_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'X-Request-ID'],
         expose_headers=['X-Request-ID'],
         supports_credentials=True)
    
    # Headers de segurança
    @app.after_request
    def add_security_headers(response):
        """Adiciona headers de segurança."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP básico
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    # Configura limpeza periódica do rate limiter (apenas uma vez)
    def setup_cleanup():
        """Configura limpeza periódica do rate limiter."""
        global _cleanup_thread_started
        
        # Verifica se a thread já foi iniciada
        if _cleanup_thread_started:
            return
            
        import threading
        
        cleanup_logger = logging.getLogger(__name__)
        
        def cleanup_worker():
            while True:
                time.sleep(300)  # Limpa a cada 5 minutos
                try:
                    rate_limiter.cleanup_old_entries()
                except Exception as e:
                    cleanup_logger.error(f"Erro na limpeza do rate limiter: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        _cleanup_thread_started = True
        cleanup_logger.info("Thread de limpeza do rate limiter iniciada")
    
    # Inicia a limpeza apenas uma vez
    setup_cleanup()
    
    # Limita tamanho do payload
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    logger.info("Sistema de segurança configurado com sucesso")