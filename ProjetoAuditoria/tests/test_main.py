"""
Testes unitários para o módulo main.py do sistema de Auditoria SEO Técnica Automatizada.

Este módulo testa todas as funcionalidades da aplicação Flask:
- AuditOrchestrator
- Endpoints da API Flask
- Integração entre componentes
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

# Importa o módulo a ser testado
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app, AuditOrchestrator


class TestAuditOrchestrator:
    """Testes para a classe AuditOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Fixture que cria um AuditOrchestrator para testes."""
        with patch('app.main.APIManager'), \
             patch('app.main.CrawlerManager'), \
             patch('app.main.ValidatorAgent'), \
             patch('app.main.DocumentorAgent'), \
             patch('app.main.SEOAuditAgent'), \
             patch('app.main.SEODocumentationAgent'), \
             patch('app.main.DataConsolidator'), \
             patch('app.main.ReportGenerator'), \
             patch('app.main.ReportManager'), \
             patch('app.main.DatabaseManager'):
            return AuditOrchestrator()
    
    def test_initialization(self, orchestrator):
        """Testa a inicialização do AuditOrchestrator."""
        assert orchestrator.api_manager is not None
        assert orchestrator.crawler_manager is not None
        assert orchestrator.validator_agent is not None
        assert orchestrator.documentor_agent is not None
        assert orchestrator.seo_audit_agent is not None
        assert orchestrator.seo_documentation_agent is not None
        assert orchestrator.data_consolidator is not None
        assert orchestrator.report_generator is not None
        assert orchestrator.report_manager is not None
        assert orchestrator.db_manager is not None
        assert orchestrator.logger is not None
    
    @patch('app.main.active_audits', {})
    @patch('app.main.audit_results', {})
    def test_execute_full_audit_initialization(self, orchestrator):
        """Testa inicialização da auditoria completa."""
        url = "https://example.com"
        audit_id = "test-audit-123"
        options = {"include_crawler": True}
        
        # Mock dos métodos internos
        with patch.object(orchestrator, '_collect_api_data') as mock_api, \
             patch.object(orchestrator, '_execute_crawler') as mock_crawler, \
             patch.object(orchestrator, '_execute_chrome_validations') as mock_chrome, \
             patch.object(orchestrator, '_consolidate_audit_data') as mock_consolidate, \
             patch.object(orchestrator, '_execute_validations') as mock_validations, \
             patch.object(orchestrator, '_generate_documentation') as mock_docs, \
             patch.object(orchestrator, '_save_audit_to_history') as mock_save:
            
            # Configura mocks
            mock_api.return_value = {"ga4": {}, "gsc": {}, "psi": {}}
            mock_crawler.return_value = {"pages": []}
            mock_chrome.return_value = {"validations": []}
            mock_consolidate.return_value = {"metrics": {}}
            mock_validations.return_value = Mock()
            mock_docs.return_value = {"documentation": {}}
            
            # Executa auditoria
            result = orchestrator.execute_full_audit(url, audit_id, options)
            
            # Verificações básicas
            assert result is not None
            assert result.get('audit_id') == audit_id
            assert result.get('url') == url
    
    def test_execute_full_audit_csv_only_mode(self, orchestrator):
        """Testa auditoria em modo apenas CSV."""
        url = "https://example.com"
        audit_id = "test-audit-123"
        options = {
            "csv_only_mode": True,
            "screaming_frog_csv": "test.csv"
        }
        
        # Mock do método específico para Screaming Frog
        with patch.object(orchestrator, '_execute_screaming_frog_audit') as mock_sf:
            mock_sf.return_value = {"status": "completed", "audit_id": audit_id}
            
            # Executa auditoria
            result = orchestrator.execute_full_audit(url, audit_id, options)
            
            # Verificações
            mock_sf.assert_called_once()
            assert result.get('audit_id') == audit_id
    
    @patch('app.main.active_audits', {})
    def test_update_audit_status(self, orchestrator):
        """Testa atualização de status da auditoria."""
        audit_id = "test-audit-123"
        
        # Adiciona auditoria ativa
        from app.main import active_audits
        active_audits[audit_id] = {
            'status': 'running',
            'current_step': 'initialization',
            'progress': 0
        }
        
        # Atualiza status
        orchestrator._update_audit_status(audit_id, 'collecting_data', 25)
        
        # Verificações
        assert active_audits[audit_id]['current_step'] == 'collecting_data'
        assert active_audits[audit_id]['progress'] == 25
        assert 'last_update' in active_audits[audit_id]
    
    def test_collect_api_data(self, orchestrator):
        """Testa coleta de dados das APIs."""
        url = "https://example.com"
        audit_result = {"steps": []}
        
        # Mock dos métodos da API
        orchestrator.api_manager.get_ga4_data.return_value = {"sessions": 1000}
        orchestrator.api_manager.get_gsc_data.return_value = {"clicks": 500}
        orchestrator.api_manager.get_psi_data.return_value = {"score": 85}
        
        # Executa coleta
        result = orchestrator._collect_api_data(url, audit_result)
        
        # Verificações
        assert result is not None
        assert "ga4" in result
        assert "gsc" in result
        assert "psi" in result
        assert result["ga4"]["sessions"] == 1000
        assert result["gsc"]["clicks"] == 500
        assert result["psi"]["score"] == 85
        assert len(audit_result["steps"]) > 0
    
    def test_consolidate_audit_data(self, orchestrator):
        """Testa consolidação dos dados da auditoria."""
        url = "https://example.com"
        api_data = {
            "ga4": {"sessions": 1000, "users": 800},
            "gsc": {"clicks": 500, "impressions": 2000},
            "psi": {"score": 85, "fcp": 1.2}
        }
        
        crawler_data = {
            "pages": [
                {"url": "https://example.com", "status": 200},
                {"url": "https://example.com/about", "status": 200}
            ],
            "total_pages": 2
        }
        
        chrome_data = {
            "validations": [
                {"type": "accessibility", "passed": True},
                {"type": "performance", "score": 90}
            ]
        }
        
        audit_result = {"steps": []}
        
        # Mock do consolidador
        orchestrator.data_consolidator.consolidate_data_sources.return_value = {
            "summary": {"total_pages": 2},
            "metrics": {"ga4": {"sessions": 1000}, "total_pages": 2, "total_sessions": 1000}
        }
        
        # Executa consolidação
        result = orchestrator._consolidate_audit_data(url, api_data, crawler_data, chrome_data, audit_result)
        
        # Verificações
        assert result is not None
        assert "summary" in result
        assert "metrics" in result
        assert result["summary"]["total_pages"] == 2
        assert result["metrics"]["ga4"]["sessions"] == 1000
        assert len(audit_result["steps"]) > 0
    
    def test_update_audit_status_multiple_calls(self, orchestrator):
        """Testa múltiplas atualizações de status da auditoria."""
        audit_id = "test-audit-123"
        
        # Adiciona auditoria ativa
        from app.main import active_audits
        active_audits[audit_id] = {
            'status': 'running',
            'current_step': 'initialization',
            'progress': 0
        }
        
        # Primeira atualização
        orchestrator._update_audit_status(audit_id, 'collecting_data', 25)
        assert active_audits[audit_id]['current_step'] == 'collecting_data'
        assert active_audits[audit_id]['progress'] == 25
        
        # Segunda atualização
        orchestrator._update_audit_status(audit_id, 'validating', 75)
        assert active_audits[audit_id]['current_step'] == 'validating'
        assert active_audits[audit_id]['progress'] == 75
        
        # Limpa o estado
        active_audits.clear()


class TestFlaskApp:
    """Testes para a aplicação Flask."""
    
    @pytest.fixture
    def client(self):
        """Fixture que cria um cliente de teste Flask."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Fixture que mocka o AuditOrchestrator."""
        with patch('app.main.orchestrator') as mock:
            yield mock
    
    def test_health_endpoint(self, client):
        """Testa o endpoint de health check."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_start_audit_endpoint_success(self, client, mock_orchestrator):
        """Testa endpoint de início de auditoria com sucesso."""
        # Faz requisição com URL válida
        response = client.post('/audit/start', 
                             json={'url': 'https://example.com'})
        
        # Verificações - deve retornar 202 (Accepted) para auditoria iniciada
        assert response.status_code == 202
        data = json.loads(response.data)
        assert 'audit_id' in data
        assert data['url'] == 'https://example.com'
        assert data['status'] == 'started'
    
    def test_start_audit_endpoint_missing_url(self, client, mock_orchestrator):
        """Testa endpoint de início de auditoria sem URL (deve usar placeholder)."""
        mock_orchestrator.execute_full_audit.return_value = "test-audit-123"
        
        response = client.post('/audit/start', 
                             json={'options': {'include_crawler': True}})
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert 'audit_id' in data
        assert data['url'] == 'https://example.com'  # URL placeholder
    
    @patch('app.main.orchestrator')
    def test_start_audit_endpoint_invalid_json(self, mock_orchestrator, client):
        """Testa endpoint de início de auditoria com JSON inválido."""
        response = client.post('/audit/start', 
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.main.orchestrator')
    def test_start_audit_endpoint_invalid_url(self, mock_orchestrator, client):
        """Testa endpoint com URL inválida."""
        response = client.post('/audit/start', 
                             json={'url': 'invalid-url'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'INVALID_URL'
    
    def test_audit_status_endpoint_success(self, client):
        """Testa endpoint de status de auditoria com sucesso."""
        audit_id = "test-audit-123"
        
        # Primeiro, adiciona uma auditoria ativa para testar
        from app.main import active_audits
        active_audits[audit_id] = {
            'status': 'running',
            'url': 'https://example.com',
            'current_step': 'collecting_data',
            'progress': 50,
            'start_time': datetime.now(),
            'last_update': datetime.now()
        }
        
        # Faz requisição
        response = client.get(f'/audit/status/{audit_id}')
        
        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['audit_id'] == audit_id
        assert data['status'] == 'running'
        assert data['url'] == 'https://example.com'
        
        # Limpa o estado
        active_audits.clear()
    
    def test_audit_status_endpoint_not_found(self, client):
        """Testa endpoint de status para auditoria inexistente."""
        audit_id = "nonexistent-audit"
        
        # Faz requisição
        response = client.get(f'/audit/status/{audit_id}')
        
        # Verificações
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'AUDIT_NOT_FOUND'
    
    def test_audit_result_endpoint_success(self, client):
        """Testa endpoint de resultado de auditoria com sucesso."""
        audit_id = "test-audit-123"
        
        # Adiciona resultado de auditoria para testar
        from app.main import audit_results
        audit_results[audit_id] = {
            'audit_id': audit_id,
            'url': 'https://example.com',
            'status': 'completed',
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'overall_score': 85,
            'audit_report': Mock(summary={}, validations=[])
        }
        
        # Faz requisição
        response = client.get(f'/audit/result/{audit_id}')
        
        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['audit_id'] == audit_id
        assert data['status'] == 'completed'
        assert data['overall_score'] == 85
        
        # Limpa o estado
        audit_results.clear()
    
    def test_audit_result_endpoint_not_found(self, client):
        """Testa endpoint de resultado para auditoria inexistente."""
        audit_id = "nonexistent-audit"
        
        # Faz requisição
        response = client.get(f'/audit/result/{audit_id}')
        
        # Verificações
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'RESULT_NOT_FOUND'
    
    def test_cancel_audit_endpoint_success(self, client):
        """Testa endpoint de cancelamento de auditoria com sucesso."""
        audit_id = "test-audit-123"
        
        # Adiciona uma auditoria ativa para cancelar
        from app.main import active_audits
        active_audits[audit_id] = {
            'status': 'running',
            'url': 'https://example.com',
            'current_step': 'collecting_data',
            'progress': 50,
            'start_time': datetime.now(),
            'last_update': datetime.now()
        }
        
        # Faz requisição
        response = client.post(f'/audit/cancel/{audit_id}')
        
        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['audit_id'] == audit_id
        assert data['status'] == 'cancelled'
        
        # Limpa o estado
        active_audits.clear()
    
    def test_cancel_audit_endpoint_not_found(self, client):
        """Testa endpoint de cancelamento para auditoria inexistente."""
        audit_id = "nonexistent-audit"
        
        # Faz requisição
        response = client.post(f'/audit/cancel/{audit_id}')
        
        # Verificações
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'AUDIT_NOT_ACTIVE'
    
    def test_list_audits_endpoint(self, client):
        """Testa endpoint de listagem de auditorias."""
        # Adiciona algumas auditorias para testar
        from app.main import active_audits, audit_results
        
        active_audits["audit-1"] = {
            'status': 'running',
            'url': 'https://example.com',
            'current_step': 'collecting_data',
            'progress': 50,
            'start_time': datetime.now(),
            'last_update': datetime.now()
        }
        
        audit_results["audit-2"] = {
            'audit_id': 'audit-2',
            'url': 'https://test.com',
            'status': 'completed',
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'overall_score': 85,
            'audit_report': Mock(summary={}, validations=[])
        }
        
        # Faz requisição
        response = client.get('/audit/list')
        
        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'audits' in data
        assert len(data['audits']) >= 2
        
        # Limpa o estado
        active_audits.clear()
        audit_results.clear()
    
    @patch('app.main.orchestrator')
    def test_generate_report_endpoint_json(self, mock_orchestrator, client):
        """Testa endpoint de geração de relatório em JSON."""
        audit_id = "test-audit-123"
        
        # Mock do report manager
        mock_orchestrator.report_manager.formatter.format_json_report.return_value = {
            'audit_id': audit_id,
            'report': {'test': 'data'}
        }
        
        # Adiciona resultado de auditoria para testar
        from app.main import audit_results
        audit_results[audit_id] = {
            'audit_id': audit_id,
            'url': 'https://example.com',
            'status': 'completed',
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'overall_score': 85,
            'audit_report': Mock(summary={"test": "data"}, validations=[])
        }
        
        # Faz requisição
        response = client.get(f'/audit/report/{audit_id}?format=json')
        
        # Verificações
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'audit_id' in data
        assert 'report' in data
        
        # Limpa o estado
        audit_results.clear()
    
    @patch('app.main.orchestrator')
    def test_generate_report_endpoint_html(self, mock_orchestrator, client):
        """Testa endpoint de geração de relatório em HTML."""
        audit_id = "test-audit-123"
        
        # Mock do report manager
        mock_orchestrator.report_manager.formatter.format_html_report.return_value = "<!DOCTYPE html><html><body>Test Report</body></html>"
        
        # Adiciona resultado de auditoria para testar
        from app.main import audit_results
        audit_results[audit_id] = {
            'audit_id': audit_id,
            'url': 'https://example.com',
            'status': 'completed',
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'overall_score': 85,
            'audit_report': Mock(summary={"test": "data"}, validations=[])
        }
        
        # Faz requisição
        response = client.get(f'/audit/report/{audit_id}?format=html')
        
        # Verificações
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        assert b'<!DOCTYPE html>' in response.data
        
        # Limpa o estado
        audit_results.clear()
    
    @patch('app.main.orchestrator')
    def test_export_report_endpoint_json(self, mock_orchestrator, client):
        """Testa endpoint de exportação de relatório em JSON."""
        audit_id = "test-audit-123"
        
        # Mock do report manager
        mock_file_path = "/tmp/test_report.json"
        mock_orchestrator.report_manager.exporter.export_json_report.return_value = mock_file_path
        
        # Adiciona resultado de auditoria para testar
        from app.main import audit_results
        audit_results[audit_id] = {
            'audit_id': audit_id,
            'url': 'https://example.com',
            'status': 'completed',
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'overall_score': 85,
            'audit_report': Mock(summary={"test": "data"}, validations=[])
        }
        
        # Mock do send_file para retornar uma resposta válida
        with patch('app.main.send_file') as mock_send_file:
            from flask import Response
            mock_send_file.return_value = Response(
                response='{"test": "data"}',
                status=200,
                headers={'Content-Disposition': 'attachment; filename=test.json'},
                content_type='application/json'
            )
            
            # Faz requisição
            response = client.get(f'/audit/export/{audit_id}?format=json')
            
            # Verificações
            assert response.status_code == 200
            mock_send_file.assert_called_once()
        
        # Limpa o estado
        audit_results.clear()
    
    @patch('app.main.orchestrator')
    def test_export_report_endpoint_csv(self, mock_orchestrator, client):
        """Testa endpoint de exportação de relatório em CSV."""
        audit_id = "test-audit-123"
        
        # Mock do report manager
        mock_file_path = "/tmp/test_report.csv"
        mock_orchestrator.report_manager.exporter.export_csv_summary.return_value = mock_file_path
        
        # Adiciona resultado de auditoria para testar
        from app.main import audit_results
        audit_results[audit_id] = {
            'audit_id': audit_id,
            'url': 'https://example.com',
            'status': 'completed',
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'overall_score': 85,
            'audit_report': Mock(summary={"test": "data"}, validations=[])
        }
        
        # Mock do send_file para retornar uma resposta válida
        with patch('app.main.send_file') as mock_send_file:
            from flask import Response
            mock_send_file.return_value = Response(
                response='test,data\n1,2',
                status=200,
                headers={'Content-Disposition': 'attachment; filename=test.csv'},
                content_type='text/csv; charset=utf-8'
            )
            
            # Faz requisição
            response = client.get(f'/audit/export/{audit_id}?format=csv')
            
            # Verificações
            assert response.status_code == 200
            mock_send_file.assert_called_once()
        
        # Limpa o estado
        audit_results.clear()


class TestFlaskAppErrorHandling:
    """Testes para tratamento de erros da aplicação Flask."""
    
    @pytest.fixture
    def client(self):
        """Fixture que cria um cliente de teste Flask."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_404_error_handler(self, client):
        """Testa tratamento de erro 404."""
        response = client.get('/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Endpoint não encontrado'
    
    def test_500_error_handler(self, client):
        """Testa tratamento de erro 500."""
        # Simula um erro que acontece antes da thread ser criada
        # Vamos forçar um erro no processamento do JSON
        with patch('app.main.uuid.uuid4') as mock_uuid:
            mock_uuid.side_effect = Exception("Erro interno")
            
            response = client.post('/audit/start', 
                                 json={'url': 'https://example.com'})
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert data['error'] == 'Erro interno do servidor'
            assert data['code'] == 'INTERNAL_ERROR'
    
    def test_method_not_allowed_handler(self, client):
        """Testa tratamento de método não permitido."""
        response = client.put('/health')  # PUT não é permitido para /health
        
        # Verificações
        assert response.status_code == 405
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Método não permitido'


class TestFlaskAppIntegration:
    """Testes de integração para a aplicação Flask."""
    
    @pytest.fixture
    def client(self):
        """Fixture que cria um cliente de teste Flask."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_full_audit_workflow(self, client):
        """Testa fluxo completo de auditoria."""
        # 1. Inicia auditoria
        response = client.post('/audit/start', 
                             json={'url': 'https://example.com'})
        
        assert response.status_code == 202
        data = json.loads(response.data)
        audit_id = data['audit_id']
        
        # 2. Verifica status
        response = client.get(f'/audit/status/{audit_id}')
        assert response.status_code == 200
        
        # 3. Simula conclusão da auditoria
        from app.main import active_audits, audit_results
        
        # Move da lista ativa para resultados
        if audit_id in active_audits:
            audit_data = active_audits[audit_id]
            audit_results[audit_id] = {
                'audit_id': audit_id,
                'url': audit_data['url'],
                'status': 'completed',
                'start_time': audit_data['start_time'],
                'end_time': datetime.now(),
                'overall_score': 85,
                'audit_report': Mock(summary={}, validations=[])
            }
            del active_audits[audit_id]
        
        # 4. Verifica resultado
        response = client.get(f'/audit/result/{audit_id}')
        assert response.status_code == 200
        
        # Limpa o estado
        if audit_id in audit_results:
            del audit_results[audit_id]
    
    def test_cors_headers(self, client):
        """Testa se os headers CORS estão configurados."""
        response = client.get('/health')
        
        # Verifica se o CORS está habilitado
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_json_content_type(self, client):
        """Testa se o content-type JSON está correto."""
        response = client.get('/health')
        
        assert response.content_type == 'application/json'
        
        # Verifica se é JSON válido
        data = json.loads(response.data)
        assert isinstance(data, dict)


if __name__ == "__main__":
    # Executa os testes se o arquivo for executado diretamente
    pytest.main([__file__, "-v"])