"""
Testes unitários para o módulo database.py do sistema de Auditoria SEO Técnica Automatizada.

Este módulo testa todas as funcionalidades do DatabaseManager, incluindo:
- Criação e inicialização do banco
- Operações CRUD de auditorias
- Salvamento e recuperação de dados
- Métricas históricas
- Validações
- Estatísticas
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Importa o módulo a ser testado
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import DatabaseManager, AuditRecord


class TestDatabaseManager:
    """Classe de testes para DatabaseManager."""
    
    @pytest.fixture
    def temp_db(self):
        """Fixture que cria um banco temporário para testes."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Cria o gerenciador com banco temporário
        db_manager = DatabaseManager(db_path)
        
        yield db_manager
        
        # Limpa após o teste
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_database_initialization(self, temp_db):
        """Testa a inicialização do banco de dados."""
        # Verifica se o arquivo do banco foi criado
        assert os.path.exists(temp_db.db_path)
        
        # Verifica se as tabelas foram criadas
        import sqlite3
        with sqlite3.connect(temp_db.db_path) as conn:
            cursor = conn.cursor()
            
            # Lista todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['audits', 'metrics_history', 'validations']
            for table in expected_tables:
                assert table in tables, f"Tabela {table} não foi criada"
    
    def test_create_audit_success(self, temp_db):
        """Testa a criação bem-sucedida de uma auditoria."""
        audit_id = "test_audit_001"
        domain = "example.com"
        
        result = temp_db.create_audit(audit_id, domain)
        
        assert result is True
        
        # Verifica se a auditoria foi criada no banco
        audit = temp_db.get_audit(audit_id)
        assert audit is not None
        assert audit.audit_id == audit_id
        assert audit.domain == domain
        assert audit.status == "iniciada"
        assert isinstance(audit.created_at, datetime)
    
    def test_create_audit_duplicate(self, temp_db):
        """Testa a tentativa de criar auditoria duplicada."""
        audit_id = "test_audit_002"
        domain = "example.com"
        
        # Primeira criação deve funcionar
        result1 = temp_db.create_audit(audit_id, domain)
        assert result1 is True
        
        # Segunda criação deve falhar
        result2 = temp_db.create_audit(audit_id, domain)
        assert result2 is False
    
    def test_update_audit_status(self, temp_db):
        """Testa a atualização do status de uma auditoria."""
        audit_id = "test_audit_003"
        domain = "example.com"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Atualiza status para 'em_progresso'
        result = temp_db.update_audit_status(audit_id, "em_progresso")
        assert result is True
        
        # Verifica se foi atualizado
        audit = temp_db.get_audit(audit_id)
        assert audit.status == "em_progresso"
        
        # Atualiza para 'concluída' (deve definir completed_at)
        result = temp_db.update_audit_status(audit_id, "concluída")
        assert result is True
        
        audit = temp_db.get_audit(audit_id)
        assert audit.status == "concluída"
        assert audit.completed_at is not None
    
    def test_update_audit_status_with_error(self, temp_db):
        """Testa a atualização do status com mensagem de erro."""
        audit_id = "test_audit_004"
        domain = "example.com"
        error_msg = "Erro de conexão com API"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Atualiza status com erro
        result = temp_db.update_audit_status(audit_id, "erro", error_msg)
        assert result is True
        
        # Verifica se foi atualizado
        audit = temp_db.get_audit(audit_id)
        assert audit.status == "erro"
        assert audit.error_message == error_msg
    
    def test_save_audit_data(self, temp_db):
        """Testa o salvamento de dados específicos de auditoria."""
        audit_id = "test_audit_005"
        domain = "example.com"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Dados de teste
        ga4_data = {
            "sessions": 1000,
            "pageviews": 2500,
            "bounce_rate": 0.45
        }
        
        # Salva dados GA4
        result = temp_db.save_audit_data(audit_id, "ga4_data", ga4_data)
        assert result is True
        
        # Verifica se foi salvo
        audit = temp_db.get_audit(audit_id)
        assert audit.ga4_data == ga4_data
    
    def test_save_audit_data_invalid_type(self, temp_db):
        """Testa o salvamento com tipo de dados inválido."""
        audit_id = "test_audit_006"
        domain = "example.com"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Tenta salvar com tipo inválido
        result = temp_db.save_audit_data(audit_id, "invalid_type", {})
        assert result is False
    
    def test_get_audit_nonexistent(self, temp_db):
        """Testa a recuperação de auditoria inexistente."""
        result = temp_db.get_audit("nonexistent_audit")
        assert result is None
    
    def test_list_audits(self, temp_db):
        """Testa a listagem de auditorias."""
        # Cria várias auditorias
        audits_data = [
            ("audit_001", "example.com"),
            ("audit_002", "test.com"),
            ("audit_003", "example.com"),
        ]
        
        for audit_id, domain in audits_data:
            temp_db.create_audit(audit_id, domain)
        
        # Lista todas as auditorias
        all_audits = temp_db.list_audits()
        assert len(all_audits) == 3
        
        # Lista por domínio
        example_audits = temp_db.list_audits(domain="example.com")
        assert len(example_audits) == 2
        
        # Lista por status
        iniciada_audits = temp_db.list_audits(status="iniciada")
        assert len(iniciada_audits) == 3
    
    def test_save_metric(self, temp_db):
        """Testa o salvamento de métricas históricas."""
        audit_id = "test_audit_007"
        domain = "example.com"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Salva métrica
        result = temp_db.save_metric(
            audit_id, 
            "page_load_time", 
            2.5, 
            "performance"
        )
        assert result is True
    
    def test_get_metrics_history(self, temp_db):
        """Testa a recuperação do histórico de métricas."""
        audit_id = "test_audit_008"
        domain = "example.com"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Salva várias métricas
        metrics = [
            ("page_load_time", 2.5, "performance"),
            ("lcp", 1.8, "core_web_vitals"),
            ("cls", 0.1, "core_web_vitals"),
        ]
        
        for metric_name, value, category in metrics:
            temp_db.save_metric(audit_id, metric_name, value, category)
        
        # Recupera histórico
        history = temp_db.get_metrics_history(domain)
        assert len(history) == 3
        
        # Recupera métrica específica
        lcp_history = temp_db.get_metrics_history(domain, "lcp")
        assert len(lcp_history) == 1
        assert lcp_history[0]["metric_name"] == "lcp"
    
    def test_save_validation(self, temp_db):
        """Testa o salvamento de validações."""
        audit_id = "test_audit_009"
        domain = "example.com"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Salva validação
        result = temp_db.save_validation(
            audit_id,
            "meta_tags",
            "passed",
            "info",
            "Todas as meta tags estão presentes"
        )
        assert result is True
    
    def test_get_audit_statistics(self, temp_db):
        """Testa a recuperação de estatísticas."""
        # Cria algumas auditorias com diferentes status
        temp_db.create_audit("audit_001", "example.com")
        temp_db.create_audit("audit_002", "test.com")
        temp_db.update_audit_status("audit_002", "concluída")
        
        # Recupera estatísticas
        stats = temp_db.get_audit_statistics()
        
        assert stats["total_audits"] == 2
        assert stats["unique_domains"] == 2
        assert "status_distribution" in stats
        assert stats["status_distribution"]["iniciada"] == 1
        assert stats["status_distribution"]["concluída"] == 1
    
    def test_cleanup_old_audits(self, temp_db):
        """Testa a limpeza de auditorias antigas."""
        # Cria auditoria
        audit_id = "test_audit_010"
        temp_db.create_audit(audit_id, "example.com")
        
        # Simula auditoria antiga modificando diretamente no banco
        import sqlite3
        with sqlite3.connect(temp_db.db_path) as conn:
            cursor = conn.cursor()
            old_date = datetime.now() - timedelta(days=100)
            cursor.execute(
                "UPDATE audits SET created_at = ? WHERE audit_id = ?",
                (old_date.isoformat(), audit_id)
            )
            conn.commit()
        
        # Executa limpeza (remove auditorias > 90 dias)
        deleted_count = temp_db.cleanup_old_audits(90)
        assert deleted_count == 1
        
        # Verifica se foi removida
        audit = temp_db.get_audit(audit_id)
        assert audit is None
    
    def test_audit_record_dataclass(self):
        """Testa a estrutura do dataclass AuditRecord."""
        audit = AuditRecord(
            audit_id="test_001",
            domain="example.com",
            status="iniciada",
            created_at=datetime.now()
        )
        
        assert audit.audit_id == "test_001"
        assert audit.domain == "example.com"
        assert audit.status == "iniciada"
        assert isinstance(audit.created_at, datetime)
        assert audit.completed_at is None
        assert audit.ga4_data is None
    
    @patch('app.database.logger')
    def test_error_handling(self, mock_logger, temp_db):
        """Testa o tratamento de erros e logging."""
        # Força um erro tentando atualizar auditoria inexistente
        result = temp_db.update_audit_status("nonexistent", "erro")
        assert result is False
        
        # Verifica se o erro foi logado
        mock_logger.error.assert_called()
    
    def test_database_path_creation(self):
        """Testa a criação automática de diretórios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "subdir", "test.db")
            
            # O diretório pai não existe
            assert not os.path.exists(os.path.dirname(db_path))
            
            # Cria o DatabaseManager
            db_manager = DatabaseManager(db_path)
            
            # Verifica se o diretório foi criado
            assert os.path.exists(os.path.dirname(db_path))
            assert os.path.exists(db_path)
    
    def test_json_serialization(self, temp_db):
        """Testa a serialização/deserialização de dados JSON."""
        audit_id = "test_audit_011"
        domain = "example.com"
        
        # Cria auditoria
        temp_db.create_audit(audit_id, domain)
        
        # Dados complexos com diferentes tipos
        complex_data = {
            "metrics": {
                "performance": 85,
                "accessibility": 92,
                "best_practices": 88,
                "seo": 95
            },
            "issues": [
                {"type": "warning", "message": "Imagem sem alt"},
                {"type": "error", "message": "Meta description ausente"}
            ],
            "timestamp": datetime.now().isoformat(),
            "nested": {
                "deep": {
                    "value": True
                }
            }
        }
        
        # Salva dados complexos
        result = temp_db.save_audit_data(audit_id, "psi_data", complex_data)
        assert result is True
        
        # Recupera e verifica
        audit = temp_db.get_audit(audit_id)
        assert audit.psi_data == complex_data
        assert audit.psi_data["metrics"]["performance"] == 85
        assert len(audit.psi_data["issues"]) == 2
        assert audit.psi_data["nested"]["deep"]["value"] is True


class TestDatabaseIntegration:
    """Testes de integração para o DatabaseManager."""
    
    @pytest.fixture
    def integration_db(self):
        """Fixture para testes de integração."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        
        yield db_manager
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_complete_audit_workflow(self, integration_db):
        """Testa um fluxo completo de auditoria."""
        audit_id = "integration_test_001"
        domain = "example.com"
        
        # 1. Cria auditoria
        assert integration_db.create_audit(audit_id, domain) is True
        
        # 2. Atualiza status para em progresso
        assert integration_db.update_audit_status(audit_id, "em_progresso") is True
        
        # 3. Salva dados de diferentes fontes
        ga4_data = {"sessions": 1000, "users": 800}
        gsc_data = {"clicks": 500, "impressions": 2000}
        psi_data = {"performance": 85, "accessibility": 92}
        
        assert integration_db.save_audit_data(audit_id, "ga4_data", ga4_data) is True
        assert integration_db.save_audit_data(audit_id, "gsc_data", gsc_data) is True
        assert integration_db.save_audit_data(audit_id, "psi_data", psi_data) is True
        
        # 4. Salva métricas
        assert integration_db.save_metric(audit_id, "lcp", 1.8, "core_web_vitals") is True
        assert integration_db.save_metric(audit_id, "cls", 0.1, "core_web_vitals") is True
        
        # 5. Salva validações
        assert integration_db.save_validation(
            audit_id, "meta_tags", "passed", "info", "Meta tags OK"
        ) is True
        
        # 6. Finaliza auditoria
        assert integration_db.update_audit_status(audit_id, "concluída") is True
        
        # 7. Verifica resultado final
        audit = integration_db.get_audit(audit_id)
        assert audit is not None
        assert audit.status == "concluída"
        assert audit.completed_at is not None
        assert audit.ga4_data == ga4_data
        assert audit.gsc_data == gsc_data
        assert audit.psi_data == psi_data
        
        # 8. Verifica métricas históricas
        metrics = integration_db.get_metrics_history(domain)
        assert len(metrics) == 2
        
        # 9. Verifica estatísticas
        stats = integration_db.get_audit_statistics()
        assert stats["total_audits"] == 1
        assert stats["status_distribution"]["concluída"] == 1


if __name__ == "__main__":
    # Executa os testes se o arquivo for executado diretamente
    pytest.main([__file__, "-v"])