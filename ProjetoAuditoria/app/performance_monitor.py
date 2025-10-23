"""
Sistema de Monitoramento de Performance Avançado

Este módulo implementa um sistema completo de monitoramento de performance
para a aplicação de auditoria SEO, incluindo métricas de sistema, aplicação
e negócio.
"""

import time
import psutil
import threading
import functools
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import os
from flask import request, g, has_request_context

from .logging_config import get_audit_logger, log_performance_metric


@dataclass
class PerformanceMetric:
    """Representa uma métrica de performance."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a métrica para dicionário."""
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


@dataclass
class SystemMetrics:
    """Métricas do sistema."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    load_average: List[float]
    process_count: int
    thread_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte as métricas para dicionário."""
        return asdict(self)


@dataclass
class ApplicationMetrics:
    """Métricas da aplicação."""
    active_requests: int
    total_requests: int
    error_rate: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    cache_hit_rate: float
    database_connections: int
    queue_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte as métricas para dicionário."""
        return asdict(self)


class PerformanceCollector:
    """
    Coletor de métricas de performance.
    
    Coleta métricas do sistema, aplicação e negócio de forma contínua.
    """
    
    def __init__(self, collection_interval: int = 30):
        """
        Inicializa o coletor de métricas.
        
        Args:
            collection_interval: Intervalo de coleta em segundos
        """
        self.collection_interval = collection_interval
        self.logger = get_audit_logger('performance_collector')
        self.is_running = False
        self.collection_thread: Optional[threading.Thread] = None
        
        # Armazenamento de métricas (últimas 24 horas)
        self.max_metrics = int(24 * 60 * 60 / collection_interval)  # 24 horas
        self.system_metrics: deque = deque(maxlen=self.max_metrics)
        self.application_metrics: deque = deque(maxlen=self.max_metrics)
        
        # Contadores de aplicação
        self.request_count = 0
        self.error_count = 0
        self.response_times: deque = deque(maxlen=1000)  # Últimas 1000 requisições
        self.active_requests = 0
        
        # Lock para thread safety
        self._lock = threading.Lock()
    
    def start_collection(self) -> None:
        """Inicia a coleta de métricas."""
        if self.is_running:
            return
        
        self.is_running = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self.collection_thread.start()
        self.logger.info("Coleta de métricas de performance iniciada")
    
    def stop_collection(self) -> None:
        """Para a coleta de métricas."""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        self.logger.info("Coleta de métricas de performance parada")
    
    def _collection_loop(self) -> None:
        """Loop principal de coleta de métricas."""
        while self.is_running:
            try:
                # Coleta métricas do sistema
                system_metrics = self._collect_system_metrics()
                
                # Coleta métricas da aplicação
                app_metrics = self._collect_application_metrics()
                
                # Armazena as métricas
                with self._lock:
                    self.system_metrics.append({
                        'timestamp': datetime.now(),
                        'metrics': system_metrics
                    })
                    self.application_metrics.append({
                        'timestamp': datetime.now(),
                        'metrics': app_metrics
                    })
                
                # Log das métricas críticas
                self._log_critical_metrics(system_metrics, app_metrics)
                
            except Exception as e:
                self.logger.error(f"Erro na coleta de métricas: {e}")
            
            time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memória
        memory = psutil.virtual_memory()
        
        # Disco
        disk = psutil.disk_usage('/')
        
        # Load average (apenas no Unix)
        try:
            load_avg = list(os.getloadavg())
        except (OSError, AttributeError):
            load_avg = [0.0, 0.0, 0.0]
        
        # Processos
        process_count = len(psutil.pids())
        
        # Threads do processo atual
        current_process = psutil.Process()
        thread_count = current_process.num_threads()
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_usage_percent=disk.percent,
            disk_free_gb=disk.free / (1024 * 1024 * 1024),
            load_average=load_avg,
            process_count=process_count,
            thread_count=thread_count
        )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Coleta métricas da aplicação."""
        with self._lock:
            # Taxa de erro
            error_rate = (self.error_count / max(self.request_count, 1)) * 100
            
            # Tempos de resposta
            if self.response_times:
                sorted_times = sorted(self.response_times)
                avg_response_time = sum(sorted_times) / len(sorted_times)
                p95_idx = int(len(sorted_times) * 0.95)
                p99_idx = int(len(sorted_times) * 0.99)
                p95_response_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0
                p99_response_time = sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0
            else:
                avg_response_time = p95_response_time = p99_response_time = 0
        
        # Métricas de cache (se disponível)
        cache_hit_rate = self._get_cache_hit_rate()
        
        # Conexões de banco (estimativa)
        database_connections = self._get_database_connections()
        
        # Tamanho da fila (se disponível)
        queue_size = self._get_queue_size()
        
        return ApplicationMetrics(
            active_requests=self.active_requests,
            total_requests=self.request_count,
            error_rate=error_rate,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            cache_hit_rate=cache_hit_rate,
            database_connections=database_connections,
            queue_size=queue_size
        )
    
    def _get_cache_hit_rate(self) -> float:
        """Obtém a taxa de acerto do cache."""
        try:
            from .cache import cache_manager
            stats = cache_manager.stats()
            total_ops = stats.get('total_operations', 0)
            hits = stats.get('hits', 0)
            return (hits / max(total_ops, 1)) * 100
        except Exception:
            return 0.0
    
    def _get_database_connections(self) -> int:
        """Obtém o número de conexões de banco ativas."""
        try:
            from .database_pool import get_pool_stats
            stats = get_pool_stats()
            return stats.get('active_connections', 0)
        except Exception:
            return 0
    
    def _get_queue_size(self) -> int:
        """Obtém o tamanho da fila de processamento."""
        try:
            from .async_processor import async_processor
            return async_processor.get_queue_size()
        except Exception:
            return 0
    
    def _log_critical_metrics(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics) -> None:
        """Registra métricas críticas no log."""
        # CPU alto
        if system_metrics.cpu_percent > 80:
            self.logger.warning(
                f"CPU usage alto: {system_metrics.cpu_percent}%",
                extra={'metric': 'cpu_usage', 'value': system_metrics.cpu_percent}
            )
        
        # Memória alta
        if system_metrics.memory_percent > 85:
            self.logger.warning(
                f"Uso de memória alto: {system_metrics.memory_percent}%",
                extra={'metric': 'memory_usage', 'value': system_metrics.memory_percent}
            )
        
        # Taxa de erro alta
        if app_metrics.error_rate > 5:
            self.logger.warning(
                f"Taxa de erro alta: {app_metrics.error_rate}%",
                extra={'metric': 'error_rate', 'value': app_metrics.error_rate}
            )
        
        # Tempo de resposta alto
        if app_metrics.p95_response_time > 2000:  # 2 segundos
            self.logger.warning(
                f"Tempo de resposta P95 alto: {app_metrics.p95_response_time}ms",
                extra={'metric': 'response_time_p95', 'value': app_metrics.p95_response_time}
            )
    
    def record_request_start(self) -> None:
        """Registra o início de uma requisição."""
        with self._lock:
            self.active_requests += 1
            self.request_count += 1
    
    def record_request_end(self, endpoint: str, method: str, status_code: int, duration_ms: float) -> None:
        """
        Registra o fim de uma requisição.
        
        Args:
            endpoint: Endpoint da requisição
            method: Método HTTP
            status_code: Código de status HTTP
            duration_ms: Tempo de resposta em milissegundos
        """
        with self._lock:
            self.active_requests = max(0, self.active_requests - 1)
            self.response_times.append(duration_ms)
            if status_code >= 400:
                self.error_count += 1
    
    def record_error(self, endpoint: str, method: str, error_type: str, status_code: int) -> None:
        """Registra um erro."""
        with self._lock:
            self.error_count += 1
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas atuais do sistema."""
        return self._collect_system_metrics()
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """Coleta métricas atuais da aplicação."""
        return self._collect_application_metrics()
    
    def get_request_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas de requisições."""
        with self._lock:
            return {
                'total_requests': self.request_count,
                'active_requests': self.active_requests,
                'error_count': self.error_count,
                'error_rate': (self.error_count / max(self.request_count, 1)) * 100,
                'avg_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0
            }
    
    def reset_metrics(self) -> None:
        """Reseta todas as métricas coletadas."""
        with self._lock:
            self.request_count = 0
            self.error_count = 0
            self.response_times.clear()
            self.active_requests = 0
            self.system_metrics.clear()
            self.application_metrics.clear()
    
    def monitor_performance(self, func: Callable) -> Callable:
        """Decorator para monitorar performance de funções."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log da métrica de performance
                if hasattr(self, 'logger'):
                    log_performance_metric(
                        self.logger,
                        operation=func.__name__,
                        duration_ms=duration_ms,
                        status='success'
                    )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log do erro
                if hasattr(self, 'logger'):
                    log_performance_metric(
                        self.logger,
                        operation=func.__name__,
                        duration_ms=duration_ms,
                        status='error',
                        error_type=type(e).__name__
                    )
                
                raise
        
        return wrapper
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtém as métricas atuais."""
        system_metrics = self._collect_system_metrics()
        app_metrics = self._collect_application_metrics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': system_metrics.to_dict(),
            'application': app_metrics.to_dict()
        }
    
    def get_metrics_history(self, hours: int = 1) -> Dict[str, Any]:
        """
        Obtém o histórico de métricas.
        
        Args:
            hours: Número de horas de histórico
            
        Returns:
            Histórico de métricas
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            # Filtra métricas do sistema
            system_history = [
                {
                    'timestamp': entry['timestamp'].isoformat(),
                    'metrics': entry['metrics'].to_dict()
                }
                for entry in self.system_metrics
                if entry['timestamp'] >= cutoff_time
            ]
            
            # Filtra métricas da aplicação
            app_history = [
                {
                    'timestamp': entry['timestamp'].isoformat(),
                    'metrics': entry['metrics'].to_dict()
                }
                for entry in self.application_metrics
                if entry['timestamp'] >= cutoff_time
            ]
        
        return {
            'system_metrics': system_history,
            'application_metrics': app_history
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtém o status de saúde baseado nas métricas."""
        current_metrics = self.get_current_metrics()
        system = current_metrics['system']
        app = current_metrics['application']
        
        # Determina o status geral
        issues = []
        
        if system['cpu_percent'] > 90:
            issues.append('CPU usage crítico')
        elif system['cpu_percent'] > 80:
            issues.append('CPU usage alto')
        
        if system['memory_percent'] > 95:
            issues.append('Memória crítica')
        elif system['memory_percent'] > 85:
            issues.append('Memória alta')
        
        if app['error_rate'] > 10:
            issues.append('Taxa de erro crítica')
        elif app['error_rate'] > 5:
            issues.append('Taxa de erro alta')
        
        if app['p95_response_time'] > 5000:
            issues.append('Tempo de resposta crítico')
        elif app['p95_response_time'] > 2000:
            issues.append('Tempo de resposta alto')
        
        # Determina o status
        if any('crítico' in issue or 'crítica' in issue for issue in issues):
            status = 'critical'
        elif issues:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'issues': issues,
            'metrics': current_metrics,
            'last_updated': datetime.now().isoformat()
        }


def performance_monitor(func: Callable) -> Callable:
    """
    Decorator para monitorar performance de funções.
    
    Args:
        func: Função a ser monitorada
        
    Returns:
        Função decorada
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = get_audit_logger(f'performance.{func.__name__}')
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log da performance
            log_performance_metric(
                logger.logger,
                func.__name__,
                duration_ms,
                status='success',
                module=func.__module__
            )
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log do erro com performance
            log_performance_metric(
                logger.logger,
                func.__name__,
                duration_ms,
                status='error',
                error=str(e),
                module=func.__module__
            )
            
            raise
    
    return wrapper


# Instância global do coletor
performance_collector = PerformanceCollector()


def initialize_performance_monitoring() -> None:
    """Inicializa o sistema de monitoramento de performance."""
    performance_collector.start_collection()


def get_performance_collector() -> PerformanceCollector:
    """Obtém a instância do coletor de performance."""
    return performance_collector


def shutdown_performance_monitoring() -> None:
    """Finaliza o sistema de monitoramento de performance."""
    performance_collector.stop_collection()