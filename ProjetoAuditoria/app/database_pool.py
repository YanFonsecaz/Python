"""
Módulo de pool de conexões para banco de dados SQLite otimizado para produção.

Este módulo implementa um pool de conexões thread-safe para SQLite,
melhorando a performance e confiabilidade em ambiente de produção.
"""

import sqlite3
import threading
import logging
import time
from contextlib import contextmanager
from typing import Optional, Generator
from queue import Queue, Empty
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class SQLiteConnectionPool:
    """
    Pool de conexões SQLite thread-safe para ambiente de produção.
    
    Gerencia um pool de conexões reutilizáveis para melhorar performance
    e evitar problemas de concorrência em aplicações multi-threaded.
    """
    
    def __init__(self, database_path: str, pool_size: int = 10, timeout: float = 30.0):
        """
        Inicializa o pool de conexões.
        
        Args:
            database_path: Caminho para o arquivo do banco SQLite
            pool_size: Número máximo de conexões no pool
            timeout: Timeout em segundos para obter uma conexão
        """
        self.database_path = Path(database_path)
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0
        
        # Garante que o diretório existe
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializa o pool com conexões
        self._initialize_pool()
        
        logger.info(f"Pool de conexões SQLite inicializado: {pool_size} conexões para {database_path}")
    
    def _initialize_pool(self) -> None:
        """Inicializa o pool com conexões pré-criadas."""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            if conn:
                self._pool.put(conn)
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """
        Cria uma nova conexão SQLite otimizada para produção.
        
        Returns:
            Conexão SQLite configurada ou None em caso de erro
        """
        try:
            conn = sqlite3.connect(
                str(self.database_path),
                check_same_thread=False,  # Permite uso em múltiplas threads
                timeout=self.timeout,
                isolation_level=None  # Autocommit mode para melhor performance
            )
            
            # Configurações de performance para produção
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            conn.execute("PRAGMA synchronous=NORMAL")  # Balance entre performance e segurança
            conn.execute("PRAGMA cache_size=10000")  # Cache de 10MB
            conn.execute("PRAGMA temp_store=MEMORY")  # Tabelas temporárias em memória
            conn.execute("PRAGMA mmap_size=268435456")  # Memory-mapped I/O (256MB)
            
            # Configurações de timeout
            conn.execute("PRAGMA busy_timeout=30000")  # 30 segundos
            
            with self._lock:
                self._created_connections += 1
            
            logger.debug(f"Nova conexão SQLite criada (total: {self._created_connections})")
            return conn
            
        except sqlite3.Error as e:
            logger.error(f"Erro ao criar conexão SQLite: {e}")
            return None
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager para obter uma conexão do pool.
        
        Yields:
            Conexão SQLite do pool
            
        Raises:
            RuntimeError: Se não conseguir obter uma conexão no tempo limite
        """
        conn = None
        start_time = time.time()
        
        try:
            # Tenta obter uma conexão do pool
            try:
                conn = self._pool.get(timeout=self.timeout)
            except Empty:
                # Se o pool estiver vazio, tenta criar uma nova conexão
                conn = self._create_connection()
                if not conn:
                    raise RuntimeError(f"Não foi possível obter conexão SQLite em {self.timeout}s")
            
            # Verifica se a conexão ainda está válida
            try:
                conn.execute("SELECT 1")
            except sqlite3.Error:
                # Conexão inválida, cria uma nova
                logger.warning("Conexão SQLite inválida detectada, criando nova")
                conn.close()
                conn = self._create_connection()
                if not conn:
                    raise RuntimeError("Não foi possível criar nova conexão SQLite")
            
            yield conn
            
        except Exception as e:
            logger.error(f"Erro ao usar conexão SQLite: {e}")
            if conn:
                try:
                    conn.rollback()
                except sqlite3.Error:
                    pass
            raise
        finally:
            # Retorna a conexão para o pool se ainda estiver válida
            if conn:
                try:
                    # Verifica se a conexão ainda está válida antes de retornar ao pool
                    conn.execute("SELECT 1")
                    self._pool.put(conn, timeout=1.0)
                except (sqlite3.Error, Exception):
                    # Conexão inválida, fecha e não retorna ao pool
                    try:
                        conn.close()
                    except sqlite3.Error:
                        pass
                    logger.debug("Conexão SQLite inválida descartada")
            
            elapsed = time.time() - start_time
            if elapsed > 1.0:  # Log conexões lentas
                logger.warning(f"Operação SQLite demorou {elapsed:.2f}s")
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Executa uma query SELECT e retorna os resultados.
        
        Args:
            query: Query SQL para executar
            params: Parâmetros da query
            
        Returns:
            Lista de resultados da query
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Executa uma query de modificação (INSERT, UPDATE, DELETE).
        
        Args:
            query: Query SQL para executar
            params: Parâmetros da query
            
        Returns:
            Número de linhas afetadas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Executa múltiplas queries de modificação em uma transação.
        
        Args:
            query: Query SQL para executar
            params_list: Lista de parâmetros para cada execução
            
        Returns:
            Número total de linhas afetadas
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def close_all(self) -> None:
        """Fecha todas as conexões do pool."""
        closed_count = 0
        
        # Fecha todas as conexões no pool
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
                closed_count += 1
            except (Empty, sqlite3.Error):
                break
        
        logger.info(f"Pool de conexões SQLite fechado: {closed_count} conexões")
    
    def get_stats(self) -> dict:
        """
        Retorna estatísticas do pool de conexões.
        
        Returns:
            Dicionário com estatísticas do pool
        """
        return {
            "pool_size": self.pool_size,
            "available_connections": self._pool.qsize(),
            "created_connections": self._created_connections,
            "database_path": str(self.database_path)
        }


# Instância global do pool (será inicializada na aplicação)
_connection_pool: Optional[SQLiteConnectionPool] = None


def initialize_pool(database_path: str, pool_size: int = 10) -> None:
    """
    Inicializa o pool global de conexões.
    
    Args:
        database_path: Caminho para o banco de dados
        pool_size: Tamanho do pool de conexões
    """
    global _connection_pool
    if _connection_pool:
        _connection_pool.close_all()
    
    _connection_pool = SQLiteConnectionPool(database_path, pool_size)


def get_pool() -> SQLiteConnectionPool:
    """
    Retorna o pool global de conexões.
    
    Returns:
        Instância do pool de conexões
        
    Raises:
        RuntimeError: Se o pool não foi inicializado
    """
    if not _connection_pool:
        raise RuntimeError("Pool de conexões não foi inicializado. Chame initialize_pool() primeiro.")
    
    return _connection_pool


def close_pool() -> None:
    """Fecha o pool global de conexões."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.close_all()
        _connection_pool = None