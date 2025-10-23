"""
Sistema de cache Redis para otimização de performance do Sistema de Auditoria SEO.

Este módulo implementa cache distribuído usando Redis para resultados de auditoria,
dados de APIs externas e consultas de banco de dados frequentes.
"""

import logging
import json
import pickle
import hashlib
import time
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, List
from functools import wraps
import redis
from redis.connection import ConnectionPool
from redis.exceptions import (
    ConnectionError, TimeoutError, RedisError,
    ResponseError, DataError
)


class RedisCache:
    """
    Cache Redis thread-safe com TTL (Time To Live) e fallback.
    
    Implementa cache distribuído com serialização automática,
    compressão opcional e recuperação de falhas.
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ssl: bool = False,
        socket_timeout: int = 5,
        connection_pool_size: int = 10,
        max_connections: int = 50,
        default_ttl: int = 3600,
        key_prefix: str = 'audit_cache:'
    ):
        """
        Inicializa o cache Redis.
        
        Args:
            host: Host do Redis
            port: Porta do Redis
            db: Número do banco de dados Redis
            password: Senha do Redis (opcional)
            ssl: Usar SSL/TLS
            socket_timeout: Timeout de socket em segundos
            connection_pool_size: Tamanho inicial do pool de conexões
            max_connections: Máximo de conexões no pool
            default_ttl: TTL padrão em segundos
            key_prefix: Prefixo para todas as chaves
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.ssl = ssl
        self.socket_timeout = socket_timeout
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.logger = logging.getLogger(__name__)
        
        # Configurar pool de conexões
        self.connection_pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            ssl=ssl,
            socket_timeout=socket_timeout,
            connection_pool_class_kwargs={
                'max_connections': max_connections
            }
        )
        
        # Inicializar cliente Redis
        self.redis_client = redis.Redis(
            connection_pool=self.connection_pool,
            decode_responses=False  # Manter bytes para pickle
        )
        
        # Testar conexão
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Testa a conexão com o Redis."""
        try:
            self.redis_client.ping()
            self.logger.info(f"Conexão Redis estabelecida: {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"Falha na conexão Redis: {e}")
            raise ConnectionError(f"Não foi possível conectar ao Redis: {e}")
    
    def _make_key(self, key: str) -> str:
        """
        Cria uma chave completa com prefixo.
        
        Args:
            key: Chave base
            
        Returns:
            Chave completa com prefixo
        """
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """
        Serializa um valor para armazenamento.
        
        Args:
            value: Valor a ser serializado
            
        Returns:
            Valor serializado em bytes
        """
        try:
            # Tentar JSON primeiro (mais eficiente)
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                return json.dumps(value, ensure_ascii=False).encode('utf-8')
            else:
                # Usar pickle para objetos complexos
                return pickle.dumps(value)
        except Exception as e:
            self.logger.warning(f"Erro na serialização JSON, usando pickle: {e}")
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """
        Deserializa um valor do armazenamento.
        
        Args:
            data: Dados serializados
            
        Returns:
            Valor deserializado
        """
        try:
            # Tentar JSON primeiro
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Usar pickle como fallback
                return pickle.loads(data)
            except Exception as e:
                self.logger.error(f"Erro na deserialização: {e}")
                return None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um valor do cache.
        
        Args:
            key: Chave do valor
            
        Returns:
            Valor armazenado ou None se não encontrado
        """
        try:
            full_key = self._make_key(key)
            data = self.redis_client.get(full_key)
            
            if data is None:
                return None
            
            value = self._deserialize_value(data)
            
            # Log de acesso (apenas em debug)
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Cache hit: {key}")
            
            return value
            
        except (ConnectionError, TimeoutError) as e:
            self.logger.warning(f"Erro de conexão Redis ao buscar {key}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do valor
            value: Valor a ser armazenado
            ttl: TTL em segundos (usa default se None)
            
        Returns:
            True se armazenado com sucesso, False caso contrário
        """
        try:
            full_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            ttl_seconds = ttl or self.default_ttl
            
            result = self.redis_client.setex(
                full_key,
                ttl_seconds,
                serialized_value
            )
            
            # Log de armazenamento (apenas em debug)
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Cache set: {key} (TTL: {ttl_seconds}s)")
            
            return bool(result)
            
        except (ConnectionError, TimeoutError) as e:
            self.logger.warning(f"Erro de conexão Redis ao armazenar {key}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado ao armazenar {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Remove um valor do cache.
        
        Args:
            key: Chave do valor
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            full_key = self._make_key(key)
            result = self.redis_client.delete(full_key)
            
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Cache delete: {key}")
            
            return bool(result)
            
        except (ConnectionError, TimeoutError) as e:
            self.logger.warning(f"Erro de conexão Redis ao deletar {key}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado ao deletar {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Verifica se uma chave existe no cache.
        
        Args:
            key: Chave a ser verificada
            
        Returns:
            True se a chave existe, False caso contrário
        """
        try:
            full_key = self._make_key(key)
            return bool(self.redis_client.exists(full_key))
        except Exception as e:
            self.logger.error(f"Erro ao verificar existência de {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Define um novo TTL para uma chave existente.
        
        Args:
            key: Chave do valor
            ttl: Novo TTL em segundos
            
        Returns:
            True se TTL foi definido, False caso contrário
        """
        try:
            full_key = self._make_key(key)
            return bool(self.redis_client.expire(full_key, ttl))
        except Exception as e:
            self.logger.error(f"Erro ao definir TTL para {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        Retorna o TTL restante de uma chave.
        
        Args:
            key: Chave do valor
            
        Returns:
            TTL em segundos (-1 se sem TTL, -2 se não existe)
        """
        try:
            full_key = self._make_key(key)
            return self.redis_client.ttl(full_key)
        except Exception as e:
            self.logger.error(f"Erro ao obter TTL de {key}: {e}")
            return -2
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Remove múltiplas chaves do cache.
        
        Args:
            pattern: Padrão de chaves (usa prefixo se None)
            
        Returns:
            Número de chaves removidas
        """
        try:
            if pattern is None:
                pattern = f"{self.key_prefix}*"
            else:
                pattern = self._make_key(pattern)
            
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {e}")
            return 0
    
    def stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache Redis.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            info = self.redis_client.info()
            
            # Contar chaves com nosso prefixo
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            key_count = len(keys)
            
            return {
                'type': 'redis',
                'host': self.host,
                'port': self.port,
                'db': self.db,
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'key_count': key_count,
                'key_prefix': self.key_prefix,
                'default_ttl': self.default_ttl,
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'type': 'redis',
                'error': str(e),
                'connected': False
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde da conexão Redis.
        
        Returns:
            Dicionário com status de saúde
        """
        try:
            start_time = time.time()
            self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'host': self.host,
                'port': self.port,
                'db': self.db
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'host': self.host,
                'port': self.port,
                'db': self.db
            }
    
    def close(self) -> None:
        """Fecha as conexões do pool."""
        try:
            self.connection_pool.disconnect()
            self.logger.info("Conexões Redis fechadas")
        except Exception as e:
            self.logger.error(f"Erro ao fechar conexões Redis: {e}")


# Instância global do cache Redis
redis_cache: Optional[RedisCache] = None


def initialize_redis_cache() -> Optional[RedisCache]:
    """
    Inicializa o cache Redis com configurações do ambiente.
    
    Returns:
        Instância do RedisCache ou None se falhar
    """
    global redis_cache
    
    try:
        # Configurações do ambiente
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', '6379'))
        db = int(os.getenv('REDIS_DB', '0'))
        password = os.getenv('REDIS_PASSWORD') or None
        ssl = os.getenv('REDIS_SSL', 'false').lower() == 'true'
        socket_timeout = int(os.getenv('REDIS_SOCKET_TIMEOUT', '5'))
        connection_pool_size = int(os.getenv('REDIS_CONNECTION_POOL_SIZE', '10'))
        max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))
        default_ttl = int(os.getenv('CACHE_DEFAULT_TTL', '3600'))
        
        redis_cache = RedisCache(
            host=host,
            port=port,
            db=db,
            password=password,
            ssl=ssl,
            socket_timeout=socket_timeout,
            connection_pool_size=connection_pool_size,
            max_connections=max_connections,
            default_ttl=default_ttl
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Cache Redis inicializado: {host}:{port}")
        
        return redis_cache
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Falha ao inicializar Redis, usando cache em memória: {e}")
        return None


def get_redis_cache() -> Optional[RedisCache]:
    """
    Retorna a instância global do cache Redis.
    
    Returns:
        Instância do RedisCache ou None se não inicializado
    """
    return redis_cache


# Funções de conveniência para cache Redis
def redis_get(key: str) -> Optional[Any]:
    """Recupera um valor do cache Redis."""
    if redis_cache:
        return redis_cache.get(key)
    return None


def redis_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Armazena um valor no cache Redis."""
    if redis_cache:
        return redis_cache.set(key, value, ttl)
    return False


def redis_delete(key: str) -> bool:
    """Remove um valor do cache Redis."""
    if redis_cache:
        return redis_cache.delete(key)
    return False


def redis_clear(pattern: Optional[str] = None) -> int:
    """Remove múltiplas chaves do cache Redis."""
    if redis_cache:
        return redis_cache.clear(pattern)
    return 0


def redis_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache Redis."""
    if redis_cache:
        return redis_cache.stats()
    return {'type': 'redis', 'status': 'not_initialized'}


def redis_health() -> Dict[str, Any]:
    """Verifica a saúde do cache Redis."""
    if redis_cache:
        return redis_cache.health_check()
    return {'status': 'not_initialized'}