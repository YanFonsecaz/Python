"""
Sistema de processamento assíncrono para o Sistema de Auditoria SEO.

Este módulo implementa processamento assíncrono de auditorias usando
threading e queue para melhorar a performance e responsividade da aplicação.
"""

import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime, timedelta
from enum import Enum
from queue import Queue, PriorityQueue, Empty
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json
import os


class TaskStatus(Enum):
    """Status possíveis de uma tarefa."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Prioridades de tarefas."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


@dataclass
class Task:
    """
    Representa uma tarefa assíncrona.
    
    Attributes:
        id: ID único da tarefa
        func: Função a ser executada
        args: Argumentos posicionais
        kwargs: Argumentos nomeados
        priority: Prioridade da tarefa
        status: Status atual
        created_at: Timestamp de criação
        started_at: Timestamp de início
        completed_at: Timestamp de conclusão
        result: Resultado da execução
        error: Erro ocorrido (se houver)
        retry_count: Número de tentativas
        max_retries: Máximo de tentativas
        timeout: Timeout em segundos
        callback: Função de callback
        metadata: Metadados adicionais
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    func: Callable = None
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[int] = None
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """Comparação para ordenação por prioridade."""
        return self.priority.value < other.priority.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte tarefa para dicionário."""
        return {
            "id": self.id,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "error": self.error,
            "metadata": self.metadata
        }


class TaskQueue:
    """
    Fila de tarefas com prioridade e persistência.
    
    Gerencia tarefas pendentes com diferentes prioridades e
    mantém histórico de execução.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Inicializa a fila de tarefas.
        
        Args:
            max_size: Tamanho máximo da fila
        """
        self.queue = PriorityQueue(maxsize=max_size)
        self.tasks = {}  # task_id -> Task
        self.completed_tasks = {}  # task_id -> Task (últimas 1000)
        self.max_completed = 1000
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def add_task(self, task: Task) -> str:
        """
        Adiciona uma tarefa à fila.
        
        Args:
            task: Tarefa a ser adicionada
            
        Returns:
            ID da tarefa
        """
        with self.lock:
            try:
                self.queue.put(task, block=False)
                self.tasks[task.id] = task
                self.logger.info(f"Tarefa {task.id} adicionada à fila")
                return task.id
            except Exception as e:
                self.logger.error(f"Erro ao adicionar tarefa: {e}")
                raise
    
    def get_task(self, timeout: Optional[float] = None) -> Optional[Task]:
        """
        Recupera próxima tarefa da fila.
        
        Args:
            timeout: Timeout para aguardar tarefa
            
        Returns:
            Próxima tarefa ou None se timeout
        """
        try:
            task = self.queue.get(timeout=timeout)
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            return task
        except Empty:
            return None
    
    def complete_task(self, task: Task, result: Any = None, error: str = None) -> None:
        """
        Marca uma tarefa como concluída.
        
        Args:
            task: Tarefa concluída
            result: Resultado da execução
            error: Erro ocorrido (se houver)
        """
        with self.lock:
            task.completed_at = datetime.now()
            task.result = result
            task.error = error
            task.status = TaskStatus.COMPLETED if error is None else TaskStatus.FAILED
            
            # Move para histórico de concluídas
            self.completed_tasks[task.id] = task
            self.tasks.pop(task.id, None)
            
            # Limita tamanho do histórico
            if len(self.completed_tasks) > self.max_completed:
                oldest_id = min(
                    self.completed_tasks.keys(),
                    key=lambda k: self.completed_tasks[k].completed_at
                )
                self.completed_tasks.pop(oldest_id)
            
            self.logger.info(f"Tarefa {task.id} concluída: {task.status.value}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna status de uma tarefa.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Dicionário com status da tarefa
        """
        with self.lock:
            # Procura em tarefas ativas
            if task_id in self.tasks:
                return self.tasks[task_id].to_dict()
            
            # Procura em tarefas concluídas
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id].to_dict()
            
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancela uma tarefa pendente.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            True se tarefa foi cancelada
        """
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()
                    self.complete_task(task, error="Tarefa cancelada")
                    return True
            return False
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da fila.
        
        Returns:
            Dicionário com estatísticas
        """
        with self.lock:
            pending_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            running_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            completed_count = len(self.completed_tasks)
            
            return {
                "pending": pending_count,
                "running": running_count,
                "completed": completed_count,
                "total_active": len(self.tasks),
                "queue_size": self.queue.qsize()
            }


class AsyncProcessor:
    """
    Processador assíncrono de tarefas.
    
    Gerencia pool de threads para execução paralela de tarefas
    com diferentes prioridades e retry automático.
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        queue_size: int = 1000,
        enable_retry: bool = True
    ):
        """
        Inicializa o processador assíncrono.
        
        Args:
            max_workers: Número máximo de workers
            queue_size: Tamanho máximo da fila
            enable_retry: Habilita retry automático
        """
        self.max_workers = max_workers
        self.enable_retry = enable_retry
        self.task_queue = TaskQueue(queue_size)
        self.executor = None  # Será criado no start()
        self.workers = []
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Métricas
        self.metrics = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "average_execution_time": 0.0,
            "started_at": None
        }
    
    def start(self) -> None:
        """Inicia o processador assíncrono."""
        if self.running:
            self.logger.warning("Processador já está rodando")
            return
        
        self.running = True
        self.metrics["started_at"] = datetime.now()
        
        # Cria o ThreadPoolExecutor apenas quando necessário
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Inicia o loop principal em uma thread separada
        main_thread = threading.Thread(target=self._main_loop, daemon=True)
        main_thread.start()
        
        self.logger.info(f"AsyncProcessor iniciado com {self.max_workers} workers")
    
    def _main_loop(self) -> None:
        """Loop principal que processa tarefas usando ThreadPoolExecutor."""
        while self.running:
            try:
                # Pega uma tarefa da fila
                task = self.task_queue.get_task(timeout=1.0)
                if task is None:
                    continue
                
                # Submete a tarefa para o ThreadPoolExecutor
                future = self.executor.submit(self._execute_task, task)
                
                # Não bloqueia - deixa o ThreadPoolExecutor gerenciar
                
            except Exception as e:
                self.logger.error(f"Erro no loop principal: {e}")
                time.sleep(1)
        
        self.logger.info("Loop principal finalizado")
    
    def stop(self, timeout: int = 30) -> None:
        """
        Para o processador assíncrono.
        
        Args:
            timeout: Timeout para aguardar conclusão
        """
        if not self.running:
            self.logger.warning("Processador não está rodando")
            return
        
        self.logger.info("Parando AsyncProcessor...")
        self.running = False
        
        # Para o ThreadPoolExecutor
        if self.executor:
            self.executor.shutdown(wait=True, timeout=timeout)
            self.executor = None
        
        self.logger.info("AsyncProcessor parado")
    
    def _execute_task(self, task: Task) -> None:
        """
        Executa uma tarefa específica.
        
        Args:
            task: Tarefa a ser executada
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Executando tarefa {task.id}")
            
            # Chama callback de início se definido (para sincronizar status)
            if task.callback and hasattr(task.callback, '__name__') and 'audit_callback' in task.callback.__name__:
                try:
                    # Callback especial para notificar início da execução
                    if hasattr(task, 'metadata') and 'audit_id' in task.metadata:
                        audit_id = task.metadata['audit_id']
                        # Atualiza status para 'running' via callback personalizado
                        from app.main import active_audits, orchestrator
                        if audit_id in active_audits:
                            active_audits[audit_id]['status'] = 'running'
                            active_audits[audit_id]['current_step'] = 'running'
                            active_audits[audit_id]['progress'] = 0
                            active_audits[audit_id]['last_update'] = datetime.now()
                            self.logger.info(f"Status da auditoria {audit_id} atualizado para 'running'")
                except Exception as e:
                    self.logger.error(f"Erro ao notificar início da tarefa {task.id}: {e}")
            
            # Executa a função da tarefa
            if task.timeout:
                # Para tarefas com timeout, usa o ThreadPoolExecutor interno
                future = self.executor.submit(task.func, *task.args, **task.kwargs)
                result = future.result(timeout=task.timeout)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            # Marca como completada
            self.task_queue.complete_task(task, result=result)
            
            # Chama callback se definido
            if task.callback:
                try:
                    task.callback(task.id, result, None)
                except Exception as e:
                    self.logger.error(f"Erro no callback da tarefa {task.id}: {e}")
            
            # Atualiza métricas
            execution_time = time.time() - start_time
            self.metrics["tasks_processed"] += 1
            
            # Atualiza tempo médio de execução
            current_avg = self.metrics["average_execution_time"]
            total_tasks = self.metrics["tasks_processed"]
            self.metrics["average_execution_time"] = (
                (current_avg * (total_tasks - 1) + execution_time) / total_tasks
            )
            
            self.logger.info(f"Tarefa {task.id} completada em {execution_time:.2f}s")
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Erro na execução da tarefa {task.id}: {error_msg}")
            
            # Verifica se deve tentar novamente
            if self.enable_retry and task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self.task_queue.add_task(task)
                self.metrics["tasks_retried"] += 1
                self.logger.info(f"Tarefa {task.id} reagendada (tentativa {task.retry_count})")
            else:
                # Marca como falhada
                self.task_queue.complete_task(task, error=error_msg)
                self.metrics["tasks_failed"] += 1
                
                # Chama callback com erro
                if task.callback:
                    try:
                        task.callback(task.id, None, error_msg)
                    except Exception as cb_error:
                        self.logger.error(f"Erro no callback da tarefa {task.id}: {cb_error}")
    
    def submit_task(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Submete uma tarefa para execução assíncrona.
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            priority: Prioridade da tarefa
            timeout: Timeout em segundos
            max_retries: Máximo de tentativas
            callback: Função de callback
            metadata: Metadados adicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            ID da tarefa
        """
        task = Task(
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            callback=callback,
            metadata=metadata or {}
        )
        
        return self.task_queue.add_task(task)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna status de uma tarefa.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            Dicionário com status da tarefa
        """
        return self.task_queue.get_task_status(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancela uma tarefa pendente.
        
        Args:
            task_id: ID da tarefa
            
        Returns:
            True se tarefa foi cancelada
        """
        return self.task_queue.cancel_task(task_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do processador.
        
        Returns:
            Dicionário com estatísticas
        """
        queue_stats = self.task_queue.get_queue_stats()
        
        uptime = None
        if self.metrics["started_at"]:
            uptime = (datetime.now() - self.metrics["started_at"]).total_seconds()
        
        return {
            "running": self.running,
            "max_workers": self.max_workers,
            "uptime_seconds": uptime,
            "queue": queue_stats,
            "metrics": self.metrics.copy()
        }


# Instância global do processador assíncrono
async_processor = AsyncProcessor(
    max_workers=int(os.getenv('ASYNC_MAX_WORKERS', '4')),
    queue_size=int(os.getenv('ASYNC_QUEUE_SIZE', '1000')),
    enable_retry=os.getenv('ASYNC_ENABLE_RETRY', 'true').lower() == 'true'
)


def async_task(
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[int] = None,
    max_retries: int = 3,
    callback: Optional[Callable] = None
):
    """
    Decorador para execução assíncrona de funções.
    
    Args:
        priority: Prioridade da tarefa
        timeout: Timeout em segundos
        max_retries: Máximo de tentativas
        callback: Função de callback
    """
    def async_task_decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return async_processor.submit_task(
                func, *args,
                priority=priority,
                timeout=timeout,
                max_retries=max_retries,
                callback=callback,
                **kwargs
            )
        return wrapper
    return async_task_decorator


def submit_audit_task(
    audit_func: Callable,
    audit_id: str,
    url: str,
    config: Dict[str, Any],
    callback: Optional[Callable] = None
) -> str:
    """
    Submete uma tarefa de auditoria para execução assíncrona.
    
    Args:
        audit_func: Função de auditoria
        audit_id: ID da auditoria
        url: URL a ser auditada
        config: Configuração da auditoria
        callback: Função de callback
        
    Returns:
        ID da tarefa
    """
    metadata = {
        "type": "audit",
        "audit_id": audit_id,
        "url": url
    }
    
    return async_processor.submit_task(
        audit_func,
        audit_id, url, config,
        priority=TaskPriority.HIGH,
        timeout=300,  # 5 minutos
        max_retries=2,
        callback=callback,
        metadata=metadata
    )


def get_audit_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retorna status de uma tarefa de auditoria.
    
    Args:
        task_id: ID da tarefa
        
    Returns:
        Status da tarefa
    """
    return async_processor.get_task_status(task_id)


def start_async_processing() -> None:
    """Inicia o processamento assíncrono."""
    async_processor.start()


def stop_async_processing() -> None:
    """Para o processamento assíncrono."""
    async_processor.stop()


def get_processing_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas do processamento assíncrono.
    
    Returns:
        Dicionário com estatísticas
    """
    return async_processor.get_stats()