"""
Configurações e fixtures compartilhadas para todos os testes do sistema de Auditoria SEO.

Este arquivo contém fixtures pytest que podem ser reutilizadas em todos os módulos de teste,
incluindo configurações de banco de dados, mocks de APIs externas e dados de teste.
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sqlite3

# Importa módulos do sistema
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import DatabaseManager


@pytest.fixture
def temp_database():
    """
    Fixture que cria um banco de dados SQLite temporário para testes.
    
    Returns:
        str: Caminho para o arquivo de banco temporário
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
        temp_db_path = temp_file.name
    
    yield temp_db_path
    
    # Cleanup: remove o arquivo temporário
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def db_manager(temp_database):
    """
    Fixture que cria um DatabaseManager com banco temporário.
    
    Args:
        temp_database: Fixture do banco temporário
        
    Returns:
        DatabaseManager: Instância configurada para testes
    """
    manager = DatabaseManager(db_path=temp_database)
    manager.initialize_database()
    return manager


@pytest.fixture
def sample_audit_data():
    """
    Fixture que fornece dados de exemplo para auditorias.
    
    Returns:
        dict: Dados de auditoria de exemplo
    """
    return {
        "audit_id": "test-audit-123",
        "domain": "example.com",
        "status": "em_progresso",
        "created_at": datetime.now(),
        "ga4_data": {
            "sessions": 1000,
            "users": 800,
            "page_views": 2500,
            "bounce_rate": 0.45
        },
        "gsc_data": {
            "clicks": 500,
            "impressions": 10000,
            "ctr": 0.05,
            "position": 15.2
        },
        "psi_data": {
            "performance": 85,
            "accessibility": 92,
            "best_practices": 88,
            "seo": 95,
            "fcp": 1.2,
            "lcp": 2.1,
            "cls": 0.05
        },
        "crawl_data": {
            "total_pages": 150,
            "internal_links": 1200,
            "external_links": 45,
            "images": 300,
            "errors_4xx": 5,
            "errors_5xx": 2
        }
    }


@pytest.fixture
def sample_validation_results():
    """
    Fixture que fornece resultados de validação de exemplo.
    
    Returns:
        list: Lista de resultados de validação
    """
    return [
        {
            "validation_type": "performance",
            "status": "passed",
            "score": 85,
            "message": "Performance dentro dos parâmetros aceitáveis",
            "details": {
                "fcp": 1.2,
                "lcp": 2.1,
                "cls": 0.05
            }
        },
        {
            "validation_type": "seo_structure",
            "status": "warning",
            "score": 75,
            "message": "Algumas páginas sem meta description",
            "details": {
                "missing_meta_desc": 15,
                "duplicate_titles": 3
            }
        },
        {
            "validation_type": "accessibility",
            "status": "passed",
            "score": 92,
            "message": "Boa acessibilidade geral",
            "details": {
                "alt_text_missing": 2,
                "contrast_issues": 1
            }
        }
    ]


@pytest.fixture
def mock_ga4_client():
    """
    Fixture que cria um mock do cliente GA4.
    
    Returns:
        Mock: Cliente GA4 mockado
    """
    mock_client = Mock()
    mock_client.authenticate.return_value = True
    mock_client.get_analytics_data.return_value = {
        "success": True,
        "data": {
            "sessions": 1000,
            "users": 800,
            "page_views": 2500,
            "bounce_rate": 0.45
        }
    }
    return mock_client


@pytest.fixture
def mock_gsc_client():
    """
    Fixture que cria um mock do cliente GSC.
    
    Returns:
        Mock: Cliente GSC mockado
    """
    mock_client = Mock()
    mock_client.authenticate.return_value = True
    mock_client.get_search_data.return_value = {
        "success": True,
        "data": {
            "clicks": 500,
            "impressions": 10000,
            "ctr": 0.05,
            "position": 15.2
        }
    }
    return mock_client


@pytest.fixture
def mock_psi_client():
    """
    Fixture que cria um mock do cliente PSI.
    
    Returns:
        Mock: Cliente PSI mockado
    """
    mock_client = Mock()
    mock_client.get_page_insights.return_value = {
        "success": True,
        "data": {
            "performance": 85,
            "accessibility": 92,
            "best_practices": 88,
            "seo": 95,
            "fcp": 1.2,
            "lcp": 2.1,
            "cls": 0.05
        }
    }
    return mock_client


@pytest.fixture
def mock_screaming_frog_crawler():
    """
    Fixture que cria um mock do Screaming Frog Crawler.
    
    Returns:
        Mock: Crawler mockado
    """
    mock_crawler = Mock()
    mock_crawler.crawl.return_value = {
        "success": True,
        "domain": "example.com",
        "output_dir": "data/crawl_results",
        "crawl_time": 120.5
    }
    mock_crawler.get_results.return_value = {
        "success": True,
        "files": ["internal_all.csv", "external_all.csv", "images_all.csv"],
        "output_dir": "data/crawl_results"
    }
    return mock_crawler


@pytest.fixture
def mock_chrome_devtools():
    """
    Fixture que cria um mock do Chrome DevTools MCP.
    
    Returns:
        Mock: Chrome DevTools mockado
    """
    mock_devtools = Mock()
    mock_devtools.navigate_page.return_value = {"success": True}
    mock_devtools.take_screenshot.return_value = {"success": True, "screenshot": "base64data"}
    mock_devtools.evaluate_script.return_value = {
        "success": True,
        "result": {"performance": {"navigation": {"loadEventEnd": 1200}}}
    }
    mock_devtools.list_network_requests.return_value = {
        "success": True,
        "requests": [
            {"url": "https://example.com", "status": 200, "size": 1024},
            {"url": "https://example.com/style.css", "status": 200, "size": 2048}
        ]
    }
    return mock_devtools


@pytest.fixture
def mock_google_docs_client():
    """
    Fixture que cria um mock do cliente Google Docs.
    
    Returns:
        Mock: Cliente Google Docs mockado
    """
    mock_client = Mock()
    mock_client.authenticate.return_value = True
    mock_client.create_document.return_value = {
        "success": True,
        "document_id": "test-doc-123",
        "document_url": "https://docs.google.com/document/d/test-doc-123"
    }
    mock_client.update_document.return_value = {"success": True}
    mock_client.share_document.return_value = {"success": True}
    return mock_client


@pytest.fixture
def temp_output_directory():
    """
    Fixture que cria um diretório temporário para arquivos de saída.
    
    Returns:
        str: Caminho para o diretório temporário
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_crawl_csv_data():
    """
    Fixture que fornece dados CSV de exemplo do Screaming Frog.
    
    Returns:
        dict: Dados CSV organizados por tipo
    """
    return {
        "internal_all.csv": [
            "Address,Content,Status Code,Status,Title 1,Meta Description 1,H1-1",
            "https://example.com/,text/html,200,OK,Home Page,Welcome to our site,Welcome",
            "https://example.com/about,text/html,200,OK,About Us,Learn about us,About Our Company",
            "https://example.com/contact,text/html,404,Client Error,,,",
        ],
        "external_all.csv": [
            "Source,Destination,Status Code,Status",
            "https://example.com/,https://google.com,200,OK",
            "https://example.com/about,https://facebook.com,200,OK",
        ],
        "images_all.csv": [
            "Source,Address,Alt Text,Size (Bytes)",
            "https://example.com/,https://example.com/logo.png,Company Logo,15420",
            "https://example.com/about,https://example.com/team.jpg,,25680",
        ]
    }


@pytest.fixture
def mock_environment_variables():
    """
    Fixture que mocka variáveis de ambiente necessárias.
    
    Returns:
        dict: Dicionário com variáveis de ambiente mockadas
    """
    env_vars = {
        "GA4_CREDENTIALS_PATH": "/path/to/ga4/credentials.json",
        "GSC_CREDENTIALS_PATH": "/path/to/gsc/credentials.json",
        "PSI_API_KEY": "test-psi-api-key",
        "GOOGLE_DOCS_CREDENTIALS_PATH": "/path/to/docs/credentials.json",
        "SCREAMING_FROG_CLI_PATH": "/path/to/screamingfrogseospider",
        "FLASK_SECRET_KEY": "test-secret-key",
        "DATABASE_PATH": "test_audit_system.db",
        "LOG_LEVEL": "DEBUG",
        "CHROME_DEVTOOLS_PORT": "9222"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_consolidated_report():
    """
    Fixture que fornece um relatório consolidado de exemplo.
    
    Returns:
        dict: Relatório consolidado de exemplo
    """
    return {
        "audit_id": "test-audit-123",
        "domain": "example.com",
        "audit_date": datetime.now().isoformat(),
        "overall_score": 82,
        "summary": {
            "total_pages_analyzed": 150,
            "critical_issues": 3,
            "warnings": 8,
            "recommendations": 12
        },
        "performance": {
            "score": 85,
            "fcp": 1.2,
            "lcp": 2.1,
            "cls": 0.05,
            "status": "good"
        },
        "seo": {
            "score": 78,
            "missing_meta_descriptions": 15,
            "duplicate_titles": 3,
            "missing_alt_text": 8,
            "status": "needs_improvement"
        },
        "accessibility": {
            "score": 92,
            "contrast_issues": 1,
            "missing_labels": 2,
            "status": "good"
        },
        "technical": {
            "score": 88,
            "broken_links": 5,
            "server_errors": 2,
            "redirect_chains": 3,
            "status": "good"
        },
        "recommendations": [
            {
                "priority": "high",
                "category": "seo",
                "issue": "Missing meta descriptions",
                "description": "15 páginas não possuem meta description",
                "solution": "Adicionar meta descriptions únicas para cada página"
            },
            {
                "priority": "medium",
                "category": "performance",
                "issue": "Large images",
                "description": "Algumas imagens são muito grandes",
                "solution": "Otimizar imagens e usar formatos modernos como WebP"
            }
        ]
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Fixture que configura automaticamente o ambiente de teste.
    
    Esta fixture é executada automaticamente para todos os testes.
    """
    # Configura logging para testes
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)  # Suprime logs durante testes
    
    # Configura timezone para testes consistentes
    os.environ['TZ'] = 'UTC'
    
    yield
    
    # Cleanup após os testes
    # Remove arquivos temporários que possam ter sido criados
    temp_files = [
        'test_audit_system.db',
        'test_crawl_results',
        'test_reports'
    ]
    
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            if os.path.isfile(temp_file):
                os.unlink(temp_file)
            elif os.path.isdir(temp_file):
                import shutil
                shutil.rmtree(temp_file)


@pytest.fixture
def flask_test_client():
    """
    Fixture que cria um cliente de teste Flask.
    
    Returns:
        FlaskClient: Cliente de teste configurado
    """
    from app.main import app
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


# Fixtures para testes de performance
@pytest.fixture
def performance_test_data():
    """
    Fixture que fornece dados para testes de performance.
    
    Returns:
        dict: Dados de teste de performance
    """
    return {
        "large_domain_list": [f"site{i}.com" for i in range(100)],
        "large_crawl_data": {
            "pages": [f"https://example.com/page{i}" for i in range(1000)],
            "links": [f"https://example.com/link{i}" for i in range(5000)]
        },
        "stress_test_params": {
            "concurrent_audits": 10,
            "pages_per_audit": 500,
            "duration_minutes": 5
        }
    }


# Fixtures para testes de integração
@pytest.fixture
def integration_test_config():
    """
    Fixture que fornece configuração para testes de integração.
    
    Returns:
        dict: Configuração de teste de integração
    """
    return {
        "test_domain": "httpbin.org",  # Domínio público para testes
        "test_endpoints": [
            "/get",
            "/status/200",
            "/status/404",
            "/delay/1"
        ],
        "expected_responses": {
            "/get": 200,
            "/status/200": 200,
            "/status/404": 404,
            "/delay/1": 200
        }
    }


if __name__ == "__main__":
    # Este arquivo não deve ser executado diretamente
    print("Este é um arquivo de configuração pytest. Execute 'pytest' para rodar os testes.")