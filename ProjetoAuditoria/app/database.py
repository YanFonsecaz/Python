"""
Módulo de banco de dados SQLite para o sistema de Auditoria SEO Técnica Automatizada.

Este módulo gerencia o armazenamento persistente de auditorias, resultados e histórico
usando SQLite como banco de dados local com pool de conexões para produção.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import os
from .database_pool import get_pool, initialize_pool

# Configurar adaptador de datetime para sqlite3 para evitar warnings de deprecação
def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(s):
    return datetime.fromisoformat(s.decode())

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

# Configuração de logging
logger = logging.getLogger(__name__)


@dataclass
class AuditRecord:
    """Representa um registro de auditoria no banco de dados."""
    audit_id: str
    domain: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    ga4_data: Optional[Dict[str, Any]] = None
    gsc_data: Optional[Dict[str, Any]] = None
    psi_data: Optional[Dict[str, Any]] = None
    screaming_frog_data: Optional[Dict[str, Any]] = None
    chrome_devtools_data: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    consolidated_report: Optional[Dict[str, Any]] = None
    google_doc_url: Optional[str] = None
    error_message: Optional[str] = None


class DatabaseManager:
    """Gerenciador do banco de dados SQLite para auditorias SEO com pool de conexões."""
    
    def __init__(self, db_path: Optional[str] = None, pool_size: int = 10):
        """
        Inicializa o gerenciador do banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco SQLite. Se None, usa o padrão.
            pool_size: Tamanho do pool de conexões para produção.
        """
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'data/seo_audits.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializa o pool de conexões
        initialize_pool(str(self.db_path), pool_size)
        
        self._init_database()
        logger.info(f"Banco de dados inicializado com pool de {pool_size} conexões: {self.db_path}")
    
    def _init_database(self) -> None:
        """Inicializa as tabelas do banco de dados usando o pool de conexões."""
        pool = get_pool()
        
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela principal de auditorias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audits (
                    audit_id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    ga4_data TEXT,
                    gsc_data TEXT,
                    psi_data TEXT,
                    screaming_frog_data TEXT,
                    chrome_devtools_data TEXT,
                    validation_results TEXT,
                    consolidated_report TEXT,
                    google_doc_url TEXT,
                    error_message TEXT
                )
            ''')
            
            # Tabela de métricas históricas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_category TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (audit_id) REFERENCES audits (audit_id)
                )
            ''')
            
            # Tabela de validações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_id TEXT NOT NULL,
                    validation_type TEXT NOT NULL,
                    validation_result TEXT NOT NULL,
                    severity TEXT,
                    description TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (audit_id) REFERENCES audits (audit_id)
                )
            ''')
            
            # Índices para melhor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audits_status ON audits(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audits_domain ON audits(domain)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_audit_id ON metrics_history(audit_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_validations_audit_id ON validations(audit_id)')
            
            conn.commit()
            
            # Índices para melhor performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audits_domain ON audits (domain)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audits_status ON audits (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits (created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_audit_id ON metrics_history (audit_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_validations_audit_id ON validations (audit_id)')
            
            conn.commit()
    
    def create_audit(self, audit_id: str, domain: str) -> bool:
        """
        Cria um novo registro de auditoria usando pool de conexões.
        
        Args:
            audit_id: ID único da auditoria
            domain: Domínio a ser auditado
            
        Returns:
            True se criado com sucesso, False caso contrário
        """
        try:
            pool = get_pool()
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audits (audit_id, domain, status, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (audit_id, domain, 'iniciada', datetime.now()))
                conn.commit()
                
            logger.info(f"Auditoria criada: {audit_id} para domínio {domain}")
            return True
            
        except sqlite3.IntegrityError:
            logger.error(f"Auditoria {audit_id} já existe")
            return False
        except Exception as e:
            logger.error(f"Erro ao criar auditoria {audit_id}: {e}")
            return False
    
    def update_audit_status(self, audit_id: str, status: str, error_message: Optional[str] = None) -> bool:
        """
        Atualiza o status de uma auditoria usando pool de conexões.
        
        Args:
            audit_id: ID da auditoria
            status: Novo status
            error_message: Mensagem de erro opcional
            
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            pool = get_pool()
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                
                update_fields = ['status = ?']
                values = [status]
                
                if status == 'concluída':
                    update_fields.append('completed_at = ?')
                    values.append(datetime.now())
                
                if error_message:
                    update_fields.append('error_message = ?')
                    values.append(error_message)
                
                values.append(audit_id)
                
                cursor.execute(f'''
                    UPDATE audits 
                    SET {', '.join(update_fields)}
                    WHERE audit_id = ?
                ''', values)
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Status da auditoria {audit_id} atualizado para: {status}")
                    return True
                else:
                    logger.error(f"Auditoria {audit_id} não encontrada para atualização de status")
                    return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status da auditoria {audit_id}: {e}")
            return False
    
    def save_audit_data(self, audit_id: str, data_type: str, data: Dict[str, Any]) -> bool:
        """
        Salva dados específicos de uma auditoria.
        
        Args:
            audit_id: ID da auditoria
            data_type: Tipo de dados (ga4_data, gsc_data, etc.)
            data: Dados a serem salvos
            
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        valid_types = [
            'ga4_data', 'gsc_data', 'psi_data', 'screaming_frog_data',
            'chrome_devtools_data', 'validation_results', 'consolidated_report'
        ]
        
        if data_type not in valid_types:
            logger.error(f"Tipo de dados inválido: {data_type}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE audits 
                    SET {data_type} = ?
                    WHERE audit_id = ?
                ''', (json.dumps(data), audit_id))
                
                conn.commit()
                
            logger.info(f"Dados {data_type} salvos para auditoria {audit_id}")
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados {data_type} para auditoria {audit_id}: {e}")
            return False
    
    def get_audit(self, audit_id: str) -> Optional[AuditRecord]:
        """
        Recupera uma auditoria específica.
        
        Args:
            audit_id: ID da auditoria
            
        Returns:
            AuditRecord se encontrado, None caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM audits WHERE audit_id = ?', (audit_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Converte dados JSON de volta para dicionários
                audit_data = dict(row)
                json_fields = [
                    'ga4_data', 'gsc_data', 'psi_data', 'screaming_frog_data',
                    'chrome_devtools_data', 'validation_results', 'consolidated_report'
                ]
                
                for field in json_fields:
                    if audit_data[field]:
                        audit_data[field] = json.loads(audit_data[field])
                
                # Converte timestamps
                audit_data['created_at'] = datetime.fromisoformat(audit_data['created_at'])
                if audit_data['completed_at']:
                    audit_data['completed_at'] = datetime.fromisoformat(audit_data['completed_at'])
                
                return AuditRecord(**audit_data)
                
        except Exception as e:
            logger.error(f"Erro ao recuperar auditoria {audit_id}: {e}")
            return None
    
    def list_audits(self, domain: Optional[str] = None, status: Optional[str] = None, 
                   limit: int = 50) -> List[AuditRecord]:
        """
        Lista auditorias com filtros opcionais.
        
        Args:
            domain: Filtrar por domínio
            status: Filtrar por status
            limit: Limite de resultados
            
        Returns:
            Lista de AuditRecord
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = 'SELECT * FROM audits'
                conditions = []
                params = []
                
                if domain:
                    conditions.append('domain = ?')
                    params.append(domain)
                
                if status:
                    conditions.append('status = ?')
                    params.append(status)
                
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)
                
                query += ' ORDER BY created_at DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                audits = []
                for row in rows:
                    audit_data = dict(row)
                    
                    # Converte dados JSON
                    json_fields = [
                        'ga4_data', 'gsc_data', 'psi_data', 'screaming_frog_data',
                        'chrome_devtools_data', 'validation_results', 'consolidated_report'
                    ]
                    
                    for field in json_fields:
                        if audit_data[field]:
                            audit_data[field] = json.loads(audit_data[field])
                    
                    # Converte timestamps
                    audit_data['created_at'] = datetime.fromisoformat(audit_data['created_at'])
                    if audit_data['completed_at']:
                        audit_data['completed_at'] = datetime.fromisoformat(audit_data['completed_at'])
                    
                    audits.append(AuditRecord(**audit_data))
                
                return audits
                
        except Exception as e:
            logger.error(f"Erro ao listar auditorias: {e}")
            return []
    
    def save_metric(self, audit_id: str, metric_name: str, metric_value: float, 
                   metric_category: str) -> bool:
        """
        Salva uma métrica histórica.
        
        Args:
            audit_id: ID da auditoria
            metric_name: Nome da métrica
            metric_value: Valor da métrica
            metric_category: Categoria da métrica
            
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO metrics_history 
                    (audit_id, metric_name, metric_value, metric_category, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (audit_id, metric_name, metric_value, metric_category, datetime.now()))
                
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar métrica {metric_name} para auditoria {audit_id}: {e}")
            return False
    
    def get_metrics_history(self, domain: str, metric_name: Optional[str] = None, 
                           days: int = 30) -> List[Dict[str, Any]]:
        """
        Recupera histórico de métricas para um domínio.
        
        Args:
            domain: Domínio para filtrar
            metric_name: Nome específico da métrica (opcional)
            days: Número de dias para histórico
            
        Returns:
            Lista de métricas históricas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = '''
                    SELECT m.*, a.domain 
                    FROM metrics_history m
                    JOIN audits a ON m.audit_id = a.audit_id
                    WHERE a.domain = ? 
                    AND m.timestamp >= datetime('now', '-{} days')
                '''.format(days)
                
                params = [domain]
                
                if metric_name:
                    query += ' AND m.metric_name = ?'
                    params.append(metric_name)
                
                query += ' ORDER BY m.timestamp DESC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico de métricas para {domain}: {e}")
            return []
    
    def save_validation(self, audit_id: str, validation_type: str, result: str, 
                       severity: str, description: str) -> bool:
        """
        Salva resultado de uma validação.
        
        Args:
            audit_id: ID da auditoria
            validation_type: Tipo de validação
            result: Resultado da validação
            severity: Severidade do resultado
            description: Descrição da validação
            
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO validations 
                    (audit_id, validation_type, validation_result, severity, description, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (audit_id, validation_type, result, severity, description, datetime.now()))
                
                conn.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar validação {validation_type} para auditoria {audit_id}: {e}")
            return False
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """
        Recupera estatísticas gerais das auditorias.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de auditorias
                cursor.execute('SELECT COUNT(*) FROM audits')
                total_audits = cursor.fetchone()[0]
                
                # Auditorias por status
                cursor.execute('''
                    SELECT status, COUNT(*) 
                    FROM audits 
                    GROUP BY status
                ''')
                status_counts = dict(cursor.fetchall())
                
                # Domínios únicos
                cursor.execute('SELECT COUNT(DISTINCT domain) FROM audits')
                unique_domains = cursor.fetchone()[0]
                
                # Auditoria mais recente
                cursor.execute('''
                    SELECT created_at 
                    FROM audits 
                    ORDER BY created_at DESC 
                    LIMIT 1
                ''')
                latest_audit = cursor.fetchone()
                latest_audit = latest_audit[0] if latest_audit else None
                
                return {
                    'total_audits': total_audits,
                    'status_distribution': status_counts,
                    'unique_domains': unique_domains,
                    'latest_audit': latest_audit
                }
                
        except Exception as e:
            logger.error(f"Erro ao recuperar estatísticas: {e}")
            return {}
    
    def cleanup_old_audits(self, days: int = 90) -> int:
        """
        Remove auditorias antigas do banco de dados.
        
        Args:
            days: Número de dias para manter auditorias
            
        Returns:
            Número de auditorias removidas
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove validações antigas primeiro
                cursor.execute('''
                    DELETE FROM validations 
                    WHERE audit_id IN (
                        SELECT audit_id FROM audits 
                        WHERE created_at < datetime('now', '-{} days')
                    )
                '''.format(days))
                
                # Remove métricas antigas
                cursor.execute('''
                    DELETE FROM metrics_history 
                    WHERE audit_id IN (
                        SELECT audit_id FROM audits 
                        WHERE created_at < datetime('now', '-{} days')
                    )
                '''.format(days))
                
                # Remove auditorias antigas
                cursor.execute('''
                    DELETE FROM audits 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Removidas {deleted_count} auditorias antigas (>{days} dias)")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Erro ao limpar auditorias antigas: {e}")
            return 0