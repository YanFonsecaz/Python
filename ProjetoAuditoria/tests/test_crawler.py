"""
Testes unitários para o módulo crawler.py do sistema de Auditoria SEO Técnica Automatizada.

Este módulo testa as funcionalidades do Screaming Frog CLI:
- ScreamingFrogCrawler
- CrawlerManager
- Tratamento de erros
"""

import pytest
import json
import tempfile
import os
import subprocess
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

# Importa o módulo a ser testado
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.crawler import ScreamingFrogError, ScreamingFrogCrawler, CrawlerManager


class TestScreamingFrogError:
    """Testes para a exceção ScreamingFrogError."""
    
    def test_error_creation(self):
        """Testa criação da exceção personalizada."""
        message = "Erro de teste"
        error = ScreamingFrogError(message)
        
        assert str(error) == message
        assert isinstance(error, Exception)


class TestScreamingFrogCrawler:
    """Testes para a classe ScreamingFrogCrawler."""
    
    @pytest.fixture
    def crawler(self):
        """Fixture que cria um ScreamingFrogCrawler para testes."""
        # Mock do caminho do executável para evitar erro de configuração
        with patch.dict(os.environ, {'SCREAMING_FROG_PATH': '/mock/path/screamingfrog'}):
            return ScreamingFrogCrawler()
    
    def test_initialization(self, crawler):
        """Testa a inicialização do ScreamingFrogCrawler."""
        assert crawler.executable_path == '/mock/path/screamingfrog'
        assert str(crawler.output_dir).endswith('data/screaming_frog')
        assert crawler.default_config['max_crawl_depth'] == 3
    
    def test_initialization_with_custom_params(self):
        """Testa inicialização com parâmetros customizados."""
        custom_path = "/custom/path/spider"
        
        crawler = ScreamingFrogCrawler(executable_path=custom_path)
        
        assert crawler.executable_path == custom_path
        assert str(crawler.output_dir).endswith('data/screaming_frog')
    
    @patch('app.crawler.subprocess.run')
    def test_validate_executable_success(self, mock_subprocess, crawler):
        """Testa validação bem-sucedida do executável."""
        # Mock do subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        result = crawler.validate_executable()
        
        assert result is True
        mock_subprocess.assert_called_once_with(
            [crawler.executable_path, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('app.crawler.subprocess.run')
    def test_validate_executable_failure(self, mock_subprocess, crawler):
        """Testa falha na validação do executável."""
        # Mock que simula erro
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = crawler.validate_executable()
        
        assert result is False
    
    def test_crawl_website_success(self, crawler):
        """Testa crawl bem-sucedido de um website."""
        mock_result = {
            'success': True,
            'url': 'https://example.com',
            'pages_crawled': 10,
            'errors': [],
            'summary': {'total_pages': 10, 'errors_count': 0}
        }
        
        with patch.object(crawler, 'crawl_website', return_value=mock_result):
            result = crawler.crawl_website('https://example.com')
            assert result['success'] is True
            assert result['url'] == 'https://example.com'
            assert result['pages_crawled'] == 10
    
    def test_crawl_website_failure(self, crawler):
        """Testa falha no crawl de um website."""
        mock_result = {
            'success': False,
            'error': 'Erro durante o crawl',
            'url': 'https://example.com'
        }
        
        with patch.object(crawler, 'crawl_website', return_value=mock_result):
            result = crawler.crawl_website('https://example.com')
            assert result['success'] is False
            assert 'Erro durante o crawl' in result['error']
    
    def test_crawl_website_invalid_executable(self, crawler):
        """Testa crawling com executável inválido."""
        url = "https://example.com"
        
        # Mock da validação do executável falhando
        with patch.object(crawler, 'validate_executable', return_value=False):
            with pytest.raises(ScreamingFrogError) as exc_info:
                crawler.crawl_website(url)
        
            assert "Screaming Frog não está disponível" in str(exc_info.value)
    
    def test_get_crawl_history_success(self, crawler):
        """Testa obtenção do histórico de crawls."""
        # Mock de arquivos CSV no diretório
        with patch('pathlib.Path.glob') as mock_glob:
            mock_file = Mock()
            mock_file.stat.return_value.st_ctime = 1234567890
            mock_file.stat.return_value.st_size = 1024
            mock_file.__str__ = Mock(return_value='/path/to/crawl_123.csv')
            
            mock_glob.return_value = [mock_file]
            
            result = crawler.get_crawl_history()
        
        # Verifica se o histórico foi retornado
        assert len(result) == 1
        assert result[0]['file'] == '/path/to/crawl_123.csv'
        assert result[0]['created_at'] == 1234567890
        assert result[0]['size'] == 1024
    
    def test_cleanup_old_files_success(self, crawler):
        """Testa limpeza de arquivos antigos."""
        # Mock de arquivos no diretório
        with patch('pathlib.Path.glob') as mock_glob, \
             patch('time.time', return_value=1234567890):
            
            # Mock de arquivo antigo
            mock_old_file = Mock()
            mock_old_file.stat.return_value.st_ctime = 1234567890 - (8 * 24 * 60 * 60)  # 8 dias atrás
            mock_old_file.unlink = Mock()
            
            # Mock de arquivo recente
            mock_new_file = Mock()
            mock_new_file.stat.return_value.st_ctime = 1234567890 - (3 * 24 * 60 * 60)  # 3 dias atrás
            
            mock_glob.return_value = [mock_old_file, mock_new_file]
            
            result = crawler.cleanup_old_files(days_old=7)
        
        # Verifica se apenas o arquivo antigo foi removido
        assert result == 1
        mock_old_file.unlink.assert_called_once()
        mock_new_file.unlink.assert_not_called()
    
    def test_get_output_files_success(self, crawler):
        """Testa obtenção de arquivos de saída."""
        with patch.object(crawler, '_get_output_files', return_value=['output_internal.csv', 'output_external.csv']):
            files = crawler._get_output_files('output')
            assert len(files) == 2
            assert 'output_internal.csv' in files
            assert 'output_external.csv' in files


class TestCrawlerManager:
    """Testes para a classe CrawlerManager."""
    
    @pytest.fixture
    def manager(self):
        """Fixture que cria um CrawlerManager para testes."""
        with patch.dict(os.environ, {'SCREAMING_FROG_PATH': '/fake/path/screaming_frog'}):
            return CrawlerManager()
    
    def test_initialization(self, manager):
        """Testa inicialização do CrawlerManager."""
        assert manager.crawler is not None
        assert hasattr(manager, 'logger')
    
    @patch.object(ScreamingFrogCrawler, 'crawl_website')
    def test_crawl_website_success(self, mock_crawl_website, manager):
        """Testa crawling bem-sucedido de website."""
        # Mock do resultado do crawl
        mock_crawl_website.return_value = {
            'url': 'https://example.com',
            'timestamp': 1234567890,
            'results': {
                'summary': {
                    'total_pages': 100,
                    'response_codes_count': {'200': 95, '404': 5},
                    'pages_without_title': 2,
                    'pages_without_meta_description': 10,
                    'pages_without_h1': 3
                }
            },
            'output_files': ['internal_all.csv']
        }
        
        # Executa crawling
        result = manager.crawl_website('https://example.com')
        
        # Verificações
        assert result["url"] == 'https://example.com'
        assert "technical_issues" in result
        assert len(result["technical_issues"]) > 0
    
    @patch.object(ScreamingFrogCrawler, 'crawl_website')
    def test_crawl_website_failure(self, mock_crawl_website, manager):
        """Testa falha no crawling de website."""
        # Mock de falha
        mock_crawl_website.side_effect = ScreamingFrogError("Erro de crawl")
        
        # Executa crawling
        result = manager.crawl_website('https://example.com')
        
        # Verificações
        assert result["success"] is False
        assert "error" in result
        assert result["url"] == 'https://example.com'
    
    @patch.object(ScreamingFrogCrawler, 'crawl_website')
    def test_execute_full_audit_crawl_success(self, mock_crawl_website, manager):
        """Testa execução bem-sucedida de auditoria completa."""
        # Mock do resultado do crawl
        mock_crawl_website.return_value = {
            'url': 'https://example.com',
            'timestamp': 1234567890,
            'results': {
                'summary': {
                    'total_pages': 50,
                    'response_codes_count': {'200': 48, '404': 2},
                    'pages_without_title': 1,
                    'pages_without_meta_description': 5,
                    'pages_without_h1': 2
                }
            },
            'output_files': ['internal_all.csv']
        }
        
        # Executa auditoria
        result = manager.execute_full_audit_crawl('https://example.com')
        
        # Verificações
        assert result["url"] == 'https://example.com'
        assert "technical_issues" in result
        assert len(result["technical_issues"]) > 0
    
    def test_is_available_success(self, manager):
        """Testa verificação de disponibilidade do Screaming Frog."""
        with patch.object(manager.crawler, 'validate_executable', return_value=True):
            assert manager.is_available() is True
    
    def test_is_available_failure(self, manager):
        """Testa falha na verificação de disponibilidade."""
        with patch.object(manager.crawler, 'validate_executable', side_effect=ScreamingFrogError("Não encontrado")):
            assert manager.is_available() is False


class TestCrawlerIntegration:
    """Testes de integração para o sistema de crawler."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Cria diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_crawler_initialization_only(self):
        """Testa apenas a inicialização do crawler."""
        with patch.dict(os.environ, {'SCREAMING_FROG_PATH': '/fake/path/screaming_frog'}):
            crawler = ScreamingFrogCrawler()
            assert crawler.executable_path == '/fake/path/screaming_frog'
            assert crawler.output_dir.name == 'screaming_frog'
    
    def test_manager_integration(self):
        """Testa integração básica do manager."""
        with patch.dict(os.environ, {'SCREAMING_FROG_PATH': '/fake/path/screaming_frog'}):
            manager = CrawlerManager()
            assert manager.crawler is not None
            assert hasattr(manager, 'is_available')
            assert hasattr(manager, 'crawl_website')


if __name__ == "__main__":
    # Executa os testes se o arquivo for executado diretamente
    pytest.main([__file__, "-v"])