"""
Sistema de cache para otimização de performance do Sistema de Auditoria SEO.

Este módulo implementa cache em memória, em disco e Redis distribuído para resultados de auditoria,
dados de APIs externas e consultas de banco de dados frequentes.
"""

import logging
import pickle
import json
import hashlib
import time
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Callable, Union, List
from functools import wraps
import sqlite3

# Importar Redis cache
try:
    from .redis_cache import RedisCache, initialize_redis_cache, get_redis_cache
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisCache = None


class MemoryCache:
    """
    Cache em memória thread-safe com TTL (Time To Live).
    
    Implementa cache LRU (Least Recently Used) com expiração automática
    para dados que precisam de acesso rápido.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Inicializa o cache em memória.
        
        Args:
            max_size: Número máximo de itens no cache
            default_ttl: TTL padrão em segundos
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = {}
        self.expiry_times = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def _cleanup_expired(self) -> None:
        """Remove itens expirados do cache."""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self.expiry_times.items()
            if expiry < current_time
        ]
        
        for key in expired_keys:
            self._remove_key(key)
    
    def _remove_key(self, key: str) -> None:
        """Remove uma chave do cache."""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.expiry_times.pop(key, None)
    
    def _evict_lru(self) -> None:
        """Remove o item menos recentemente usado."""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove_key(lru_key)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um item do cache.
        
        Args:
            key: Chave do item
            
        Returns:
            Valor do cache ou None se não encontrado/expirado
        """
        with self.lock:
            self._cleanup_expired()
            
            if key not in self.cache:
                return None
            
            # Atualiza tempo de acesso
            self.access_times[key] = time.time()
            return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Armazena um item no cache.
        
        Args:
            key: Chave do item
            value: Valor a ser armazenado
            ttl: TTL em segundos (usa default se None)
        """
        with self.lock:
            self._cleanup_expired()
            
            # Remove item existente se presente
            if key in self.cache:
                self._remove_key(key)
            
            # Verifica se precisa fazer eviction
            while len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Adiciona novo item
            current_time = time.time()
            ttl = ttl or self.default_ttl
            
            self.cache[key] = value
            self.access_times[key] = current_time
            self.expiry_times[key] = current_time + ttl
    
    def delete(self, key: str) -> bool:
        """
        Remove um item do cache.
        
        Args:
            key: Chave do item
            
        Returns:
            True se item foi removido
        """
        with self.lock:
            if key in self.cache:
                self._remove_key(key)
                return True
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.expiry_times.clear()
    
    def stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dicionário com estatísticas
        """
        with self.lock:
            self._cleanup_expired()
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_ratio": getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1),
                "expired_items": len([
                    key for key, expiry in self.expiry_times.items()
                    if expiry < time.time()
                ])
            }


class DiskCache:
    """
    Cache em disco para dados grandes ou persistentes.
    
    Armazena dados em arquivos no sistema de arquivos com
    metadados de expiração e compressão opcional.
    """
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 500):
        """
        Inicializa o cache em disco.
        
        Args:
            cache_dir: Diretório para arquivos de cache
            max_size_mb: Tamanho máximo do cache em MB
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.metadata_file = self.cache_dir / "metadata.json"
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
        # Carrega metadados existentes
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Carrega metadados do cache."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar metadados do cache: {e}")
        
        return {}
    
    def _save_metadata(self) -> None:
        """Salva metadados do cache."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar metadados do cache: {e}")
    
    def _get_cache_file(self, key: str) -> Path:
        """Retorna caminho do arquivo de cache para uma chave."""
        # Usa hash da chave para evitar problemas com caracteres especiais
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _cleanup_expired(self) -> None:
        """Remove arquivos expirados do cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, meta in self.metadata.items():
            if meta.get('expiry', 0) < current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_key(key)
    
    def _remove_key(self, key: str) -> None:
        """Remove uma chave do cache."""
        try:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
            
            self.metadata.pop(key, None)
        except Exception as e:
            self.logger.error(f"Erro ao remover chave do cache: {e}")
    
    def _enforce_size_limit(self) -> None:
        """Aplica limite de tamanho do cache."""
        total_size = sum(meta.get('size', 0) for meta in self.metadata.values())
        
        if total_size <= self.max_size_bytes:
            return
        
        # Remove arquivos mais antigos até ficar dentro do limite
        sorted_keys = sorted(
            self.metadata.keys(),
            key=lambda k: self.metadata[k].get('access_time', 0)
        )
        
        for key in sorted_keys:
            if total_size <= self.max_size_bytes:
                break
            
            size = self.metadata[key].get('size', 0)
            self._remove_key(key)
            total_size -= size
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um item do cache em disco.
        
        Args:
            key: Chave do item
            
        Returns:
            Valor do cache ou None se não encontrado/expirado
        """
        with self.lock:
            self._cleanup_expired()
            
            if key not in self.metadata:
                return None
            
            try:
                cache_file = self._get_cache_file(key)
                if not cache_file.exists():
                    self._remove_key(key)
                    return None
                
                # Carrega dados
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                
                # Atualiza tempo de acesso
                self.metadata[key]['access_time'] = time.time()
                self._save_metadata()
                
                return data
                
            except Exception as e:
                self.logger.error(f"Erro ao carregar do cache: {e}")
                self._remove_key(key)
                return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Armazena um item no cache em disco.
        
        Args:
            key: Chave do item
            value: Valor a ser armazenado
            ttl: TTL em segundos
        """
        with self.lock:
            try:
                # Remove item existente se presente
                if key in self.metadata:
                    self._remove_key(key)
                
                # Serializa dados
                cache_file = self._get_cache_file(key)
                with open(cache_file, 'wb') as f:
                    pickle.dump(value, f)
                
                # Atualiza metadados
                current_time = time.time()
                file_size = cache_file.stat().st_size
                
                self.metadata[key] = {
                    'expiry': current_time + ttl,
                    'access_time': current_time,
                    'size': file_size,
                    'created': current_time
                }
                
                self._save_metadata()
                self._enforce_size_limit()
                
            except Exception as e:
                self.logger.error(f"Erro ao salvar no cache: {e}")
    
    def delete(self, key: str) -> bool:
        """
        Remove um item do cache.
        
        Args:
            key: Chave do item
            
        Returns:
            True se item foi removido
        """
        with self.lock:
            if key in self.metadata:
                self._remove_key(key)
                self._save_metadata()
                return True
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache."""
        with self.lock:
            try:
                # Remove todos os arquivos
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                
                # Limpa metadados
                self.metadata.clear()
                self._save_metadata()
                
            except Exception as e:
                self.logger.error(f"Erro ao limpar cache: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dicionário com estatísticas
        """
        with self.lock:
            self._cleanup_expired()
            
            total_size = sum(meta.get('size', 0) for meta in self.metadata.values())
            
            return {
                "items": len(self.metadata),
                "total_size_mb": total_size / (1024 * 1024),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "usage_percent": (total_size / self.max_size_bytes) * 100,
                "expired_items": len([
                    key for key, meta in self.metadata.items()
                    if meta.get('expiry', 0) < time.time()
                ])
            }


class CacheManager:
    """
    Gerenciador de cache que combina cache em memória, disco e Redis distribuído.
    
    Implementa estratégia de cache híbrida onde:
    - Redis: Cache distribuído para dados compartilhados entre instâncias
    - Memória: Dados pequenos e frequentes (fallback se Redis indisponível)
    - Disco: Dados grandes ou menos frequentes (fallback local)
    """
    
    def __init__(
        self,
        memory_cache_size: int = 1000,
        disk_cache_size_mb: int = 500,
        cache_dir: str = "cache",
        use_redis: bool = True
    ):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            memory_cache_size: Tamanho do cache em memória
            disk_cache_size_mb: Tamanho do cache em disco (MB)
            cache_dir: Diretório para cache em disco
            use_redis: Se deve tentar usar Redis
        """
        self.memory_cache = MemoryCache(memory_cache_size)
        self.disk_cache = DiskCache(cache_dir, disk_cache_size_mb)
        self.logger = logging.getLogger(__name__)
        
        # Configurar Redis se disponível
        self.redis_cache = None
        self.use_redis = use_redis and REDIS_AVAILABLE
        
        if self.use_redis:
            try:
                self.redis_cache = initialize_redis_cache()
                if self.redis_cache:
                    self.logger.info("Cache Redis inicializado com sucesso")
                else:
                    self.logger.warning("Falha ao inicializar Redis, usando cache local")
                    self.use_redis = False
            except Exception as e:
                self.logger.warning(f"Redis indisponível, usando cache local: {e}")
                self.use_redis = False
        
        # Configurações de cache
        self.memory_threshold_bytes = 1024 * 1024  # 1MB - acima disso vai para disco
        self.redis_ttl = 1800      # 30 minutos para Redis
        self.memory_ttl = 300      # 5 minutos para cache em memória
        self.disk_ttl = 3600       # 1 hora para cache em disco
    
    def _should_use_memory(self, value: Any) -> bool:
        """
        Determina se um valor deve ir para cache em memória.
        
        Args:
            value: Valor a ser avaliado
            
        Returns:
            True se deve usar cache em memória
        """
        try:
            # Estima tamanho do objeto
            serialized = pickle.dumps(value)
            return len(serialized) < self.memory_threshold_bytes
        except Exception:
            return False
    
    def _get_cache_type(self, cache_type: str = "auto") -> str:
        """
        Determina o tipo de cache a usar.
        
        Args:
            cache_type: Tipo solicitado ("auto", "redis", "memory", "disk")
            
        Returns:
            Tipo de cache efetivo
        """
        if cache_type == "redis" and self.use_redis:
            return "redis"
        elif cache_type == "memory":
            return "memory"
        elif cache_type == "disk":
            return "disk"
        else:  # auto
            if self.use_redis:
                return "redis"
            else:
                return "memory"  # Fallback para memória
    
    def get(self, key: str, cache_type: str = "auto") -> Optional[Any]:
        """
        Recupera um item do cache.
        
        Args:
            key: Chave do item
            cache_type: Tipo de cache preferido ("auto", "redis", "memory", "disk")
            
        Returns:
            Valor do cache ou None se não encontrado
        """
        effective_cache_type = self._get_cache_type(cache_type)
        
        # Estratégia de busca baseada no tipo
        if effective_cache_type == "redis" and self.redis_cache:
            # Tenta Redis primeiro
            value = self.redis_cache.get(key)
            if value is not None:
                return value
            
            # Fallback para memória
            value = self.memory_cache.get(key)
            if value is not None:
                # Promove para Redis se encontrado em memória
                self.redis_cache.set(key, value, self.redis_ttl)
                return value
            
            # Fallback para disco
            value = self.disk_cache.get(key)
            if value is not None:
                # Promove para Redis se encontrado em disco
                self.redis_cache.set(key, value, self.redis_ttl)
                return value
        
        elif effective_cache_type == "memory":
            # Busca apenas em memória
            return self.memory_cache.get(key)
        
        elif effective_cache_type == "disk":
            # Busca apenas em disco
            return self.disk_cache.get(key)
        
        else:
            # Fallback: memória primeiro, depois disco
            value = self.memory_cache.get(key)
            if value is not None:
                return value
            
            value = self.disk_cache.get(key)
            if value is not None:
                # Se valor é pequeno, promove para cache em memória
                if self._should_use_memory(value):
                    self.memory_cache.set(key, value, self.memory_ttl)
                return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, cache_type: str = "auto") -> bool:
        """
        Armazena um item no cache apropriado.
        
        Args:
            key: Chave do item
            value: Valor a ser armazenado
            ttl: TTL em segundos (usa padrão se None)
            cache_type: Tipo de cache preferido ("auto", "redis", "memory", "disk")
            
        Returns:
            True se armazenado com sucesso
        """
        effective_cache_type = self._get_cache_type(cache_type)
        success = False
        
        if effective_cache_type == "redis" and self.redis_cache:
            # Armazena no Redis
            redis_ttl = ttl or self.redis_ttl
            success = self.redis_cache.set(key, value, redis_ttl)
            
            # Também armazena em memória se for pequeno (cache duplo)
            if success and self._should_use_memory(value):
                memory_ttl = min(ttl or self.memory_ttl, self.memory_ttl)
                self.memory_cache.set(key, value, memory_ttl)
        
        elif effective_cache_type == "memory":
            # Armazena apenas em memória
            memory_ttl = ttl or self.memory_ttl
            self.memory_cache.set(key, value, memory_ttl)
            success = True
        
        elif effective_cache_type == "disk":
            # Armazena apenas em disco
            disk_ttl = ttl or self.disk_ttl
            self.disk_cache.set(key, value, disk_ttl)
            success = True
        
        else:
            # Fallback: escolhe baseado no tamanho
            if self._should_use_memory(value):
                memory_ttl = ttl or self.memory_ttl
                self.memory_cache.set(key, value, memory_ttl)
                success = True
            else:
                disk_ttl = ttl or self.disk_ttl
                self.disk_cache.set(key, value, disk_ttl)
                success = True
        
        return success
    
    def delete(self, key: str) -> bool:
        """
        Remove um item de todos os caches.
        
        Args:
            key: Chave do item
            
        Returns:
            True se item foi removido de pelo menos um cache
        """
        deleted = False
        
        # Remove do Redis
        if self.redis_cache:
            deleted |= self.redis_cache.delete(key)
        
        # Remove da memória
        deleted |= self.memory_cache.delete(key)
        
        # Remove do disco
        deleted |= self.disk_cache.delete(key)
        
        return deleted
    
    def clear(self, cache_type: str = "all") -> None:
        """
        Limpa caches especificados.
        
        Args:
            cache_type: Tipo de cache a limpar ("all", "redis", "memory", "disk")
        """
        if cache_type in ("all", "redis") and self.redis_cache:
            self.redis_cache.clear()
        
        if cache_type in ("all", "memory"):
            self.memory_cache.clear()
        
        if cache_type in ("all", "disk"):
            self.disk_cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas combinadas dos caches.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "memory": self.memory_cache.stats(),
            "disk": self.disk_cache.stats(),
            "redis_available": self.use_redis
        }
        
        if self.redis_cache:
            stats["redis"] = self.redis_cache.stats()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde de todos os sistemas de cache.
        
        Returns:
            Dicionário com status de saúde
        """
        health = {
            "memory": {"status": "healthy"},
            "disk": {"status": "healthy"},
            "redis": {"status": "not_configured"}
        }
        
        # Verificar Redis se disponível
        if self.redis_cache:
            health["redis"] = self.redis_cache.health_check()
        
        # Status geral
        redis_healthy = health["redis"]["status"] == "healthy"
        overall_status = "healthy" if (redis_healthy or not self.use_redis) else "degraded"
        
        health["overall"] = {
            "status": overall_status,
            "redis_enabled": self.use_redis,
            "fallback_available": True
        }
        
        return health


# Instância global do gerenciador de cache
cache_manager = CacheManager(
    memory_cache_size=int(os.getenv('CACHE_MEMORY_SIZE', '1000')),
    disk_cache_size_mb=int(os.getenv('CACHE_DISK_SIZE_MB', '500')),
    cache_dir=os.getenv('CACHE_DIR', 'cache'),
    use_redis=os.getenv('CACHE_TYPE', 'auto').lower() in ('redis', 'auto')
)


def cached(
    key_func: Optional[Callable] = None,
    ttl: Optional[int] = None,
    cache_type: str = "auto"
):
    """
    Decorador para cache automático de funções.
    
    Args:
        key_func: Função para gerar chave do cache
        ttl: TTL em segundos
        cache_type: Tipo de cache ("redis", "memory", "disk", "auto")
    """
    def cached_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Gera chave baseada no nome da função e argumentos
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{func.__name__}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            # Tenta recuperar do cache
            cached_result = cache_manager.get(cache_key, cache_type)
            if cached_result is not None:
                return cached_result
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl, cache_type)
            
            return result
        return wrapper
    return cached_decorator


def cache_audit_result(audit_id: str, result: Dict[str, Any], ttl: int = 3600, cache_type: str = "auto") -> None:
    """
    Armazena resultado de auditoria no cache.
    
    Args:
        audit_id: ID da auditoria
        result: Resultado da auditoria
        ttl: TTL em segundos
        cache_type: Tipo de cache ("redis", "memory", "disk", "auto")
    """
    cache_key = f"audit_result:{audit_id}"
    cache_manager.set(cache_key, result, ttl, cache_type)


def get_cached_audit_result(audit_id: str, cache_type: str = "auto") -> Optional[Dict[str, Any]]:
    """
    Recupera resultado de auditoria do cache.
    
    Args:
        audit_id: ID da auditoria
        cache_type: Tipo de cache ("redis", "memory", "disk", "auto")
        
    Returns:
        Resultado da auditoria ou None se não encontrado
    """
    cache_key = f"audit_result:{audit_id}"
    return cache_manager.get(cache_key, cache_type)


def cache_api_response(api_name: str, params: Dict[str, Any], response: Any, ttl: int = 1800, cache_type: str = "auto") -> None:
    """
    Armazena resposta de API externa no cache.
    
    Args:
        api_name: Nome da API
        params: Parâmetros da requisição
        response: Resposta da API
        ttl: TTL em segundos
        cache_type: Tipo de cache ("redis", "memory", "disk", "auto")
    """
    params_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()
    cache_key = f"api_response:{api_name}:{params_hash}"
    cache_manager.set(cache_key, response, ttl, cache_type)


def get_cached_api_response(api_name: str, params: Dict[str, Any], cache_type: str = "auto") -> Optional[Any]:
    """
    Recupera resposta de API externa do cache.
    
    Args:
        api_name: Nome da API
        params: Parâmetros da requisição
        cache_type: Tipo de cache ("redis", "memory", "disk", "auto")
        
    Returns:
        Resposta da API ou None se não encontrada
    """
    params_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()
    cache_key = f"api_response:{api_name}:{params_hash}"
    return cache_manager.get(cache_key, cache_type)


def invalidate_audit_cache(audit_id: str) -> None:
    """
    Invalida cache relacionado a uma auditoria.
    
    Args:
        audit_id: ID da auditoria
    """
    cache_key = f"audit_result:{audit_id}"
    cache_manager.delete(cache_key)


def get_cache_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas do sistema de cache.
    
    Returns:
        Dicionário com estatísticas
    """
    return cache_manager.stats()