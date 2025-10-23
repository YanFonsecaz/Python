"""
Testes unitários para o módulo apis.py do sistema de Auditoria SEO Técnica Automatizada.

Este módulo testa todas as funcionalidades dos clientes de API:
- GA4APIClient
- GSCAPIClient  
- PSIAPIClient
- APIManager
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import requests

# Importa o módulo a ser testado
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.apis import (
    GA4APIClient, GSCAPIClient, PSIAPIClient, APIManager
)


class TestGA4APIClient:
    """Testes para GA4APIClient."""
    
    @pytest.fixture
    @patch('app.apis.service_account.Credentials.from_service_account_file')
    @patch('app.apis.build')
    def ga4_client(self, mock_build, mock_credentials):
        """Fixture que cria um cliente GA4 para testes."""
        mock_credentials.return_value = Mock()
        mock_build.return_value = Mock()
        return GA4APIClient(
            property_id='123456789',
            credentials_path='/path/to/credentials.json'
        )
    
    def test_initialization_success(self, ga4_client):
        """Testa inicialização bem-sucedida do GA4."""
        # Verifica se o cliente foi inicializado corretamente
        assert ga4_client.property_id == '123456789'
        assert ga4_client.credentials_path == '/path/to/credentials.json'
        assert ga4_client.service is not None
    
    @patch('app.apis.service_account.Credentials.from_service_account_file')
    def test_initialization_failure(self, mock_credentials):
        """Testa falha na inicialização do GA4."""
        # Mock que gera exceção
        mock_credentials.side_effect = Exception("Credenciais inválidas")
        
        # Verifica se a exceção é propagada
        with pytest.raises(Exception):
            GA4APIClient('123456789', '/path/to/credentials.json')
    
    def test_get_page_metrics_not_authenticated(self, ga4_client):
        """Testa get_page_metrics sem autenticação."""
        # Simula cliente não autenticado
        ga4_client.service = None
        
        result = ga4_client.get_page_metrics('/test-page')
        # O método retorna um dicionário vazio quando não há serviço
        assert result == {}
    
    @patch('app.apis.service_account.Credentials.from_service_account_file')
    @patch('app.apis.build')
    def test_get_page_metrics_success(self, mock_build, mock_credentials, ga4_client):
        """Testa coleta bem-sucedida de métricas de página."""
        # Mock do serviço autenticado
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock da resposta da API
        mock_response = {
            'rows': [
                {
                    'dimensionValues': [{'value': '/test-page'}, {'value': 'Test Page'}],
                    'metricValues': [
                        {'value': '100'},  # screenPageViews
                        {'value': '50'},   # sessions
                        {'value': '0.4'},  # bounceRate
                        {'value': '120'},  # averageSessionDuration
                        {'value': '5'}     # conversions
                    ]
                }
            ]
        }
        
        # Configurar o mock corretamente
        mock_service.properties.return_value.runReport.return_value.execute.return_value = mock_response
        ga4_client.service = mock_service
        
        result = ga4_client.get_page_metrics('/test-page')
        
        assert result is not None
        assert 'page_views' in result
        assert result['page_views'] == 100
    
    @patch('app.apis.service_account.Credentials.from_service_account_file')
    @patch('app.apis.build')
    def test_get_page_metrics_api_error(self, mock_build, mock_credentials, ga4_client):
        """Testa erro na API do GA4."""
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_service.properties().runReport().execute.side_effect = Exception("API Error")
        
        ga4_client.service = mock_service
        
        result = ga4_client.get_page_metrics('/test-page')
        # O método retorna um dicionário vazio em caso de erro
        assert result == {}


class TestGSCAPIClient:
    """Testes para GSCAPIClient."""
    
    @pytest.fixture
    @patch('app.apis.service_account.Credentials.from_service_account_file')
    @patch('app.apis.build')
    def gsc_client(self, mock_build, mock_credentials):
        """Fixture que cria um cliente GSC para testes."""
        mock_credentials.return_value = Mock()
        mock_build.return_value = Mock()
        return GSCAPIClient(
            site_url='https://example.com',
            credentials_path='/path/to/credentials.json'
        )
    
    def test_initialization_success(self, gsc_client):
        """Testa inicialização bem-sucedida do GSC."""
        # Verifica se o cliente foi inicializado corretamente
        assert gsc_client.site_url == 'https://example.com'
        assert gsc_client.credentials_path == '/path/to/credentials.json'
        assert gsc_client.service is not None
    
    @patch('app.apis.service_account.Credentials.from_service_account_file')
    @patch('app.apis.build')
    def test_get_page_performance_success(self, mock_build, mock_credentials, gsc_client):
        """Testa coleta bem-sucedida de performance de página."""
        # Mock do serviço autenticado
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock da resposta da API
        mock_response = {
            'rows': [
                {
                    'keys': ['https://example.com/test-page'],
                    'clicks': 100,
                    'impressions': 1000,
                    'ctr': 0.1,
                    'position': 5.5
                }
            ]
        }
        
        mock_service.searchanalytics().query().execute.return_value = mock_response
        gsc_client.service = mock_service
        
        result = gsc_client.get_page_performance('https://example.com/test-page')
        
        assert result is not None
        assert 'clicks' in result
        assert result['clicks'] == 100
    
    def test_get_page_performance_not_authenticated(self, gsc_client):
        """Testa get_page_performance sem autenticação."""
        # Simula cliente não autenticado
        gsc_client.service = None
        
        result = gsc_client.get_page_performance('https://example.com/test-page')
        assert result == {}


class TestPSIAPIClient:
    """Testes para PSIAPIClient."""
    
    @pytest.fixture
    def psi_client(self):
        """Fixture que cria um cliente PSI para testes."""
        return PSIAPIClient(api_key='test_api_key')
    
    @patch('app.apis.requests.get')
    def test_analyze_page_success(self, mock_get, psi_client):
        """Testa análise bem-sucedida de página."""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'lighthouseResult': {
                'categories': {
                    'performance': {'score': 0.85},
                    'accessibility': {'score': 0.92},
                    'best-practices': {'score': 0.88},
                    'seo': {'score': 0.95}
                },
                'audits': {
                    'largest-contentful-paint': {
                        'numericValue': 1800,
                        'displayValue': '1.8 s'
                    },
                    'cumulative-layout-shift': {
                        'numericValue': 0.1,
                        'displayValue': '0.1'
                    },
                    'first-input-delay': {
                        'numericValue': 50,
                        'displayValue': '50 ms'
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Executa análise de página
        result = psi_client.analyze_page("https://example.com")
        
        # Verificações
        assert result['performance_score'] == 85
        assert result['accessibility_score'] == 92
        assert result['best_practices_score'] == 88
        assert result['seo_score'] == 95
        assert result['core_web_vitals']['lcp'] == 1.8
        assert result['core_web_vitals']['cls'] == 0.1
        assert result['core_web_vitals']['fid'] == 50
    
    @patch('app.apis.requests.get')
    def test_analyze_page_api_error(self, mock_get, psi_client):
        """Testa erro na API do PSI."""
        # Mock de resposta com erro
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'error': 'Internal Server Error'}
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response
        
        result = psi_client.analyze_page('https://example.com')
        assert result == {}
    
    @patch('app.apis.requests.get')
    def test_analyze_page_rate_limit(self, mock_get, psi_client):
        """Testa limite de taxa da API."""
        # Mock de resposta com limite de taxa
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {'error': 'Rate limit exceeded'}
        mock_response.raise_for_status.side_effect = requests.HTTPError("429 Too Many Requests")
        mock_get.return_value = mock_response
        
        result = psi_client.analyze_page('https://example.com')
        assert result == {}
    
    def test_analyze_page_no_api_key(self):
        """Testa PSIAPIClient sem chave de API."""
        with pytest.raises(TypeError):
            PSIAPIClient()  # Deve falhar sem api_key


class TestAPIManager:
    """Testes para APIManager."""
    
    @pytest.fixture
    @patch('os.path.exists')
    @patch('app.apis.GA4APIClient')
    @patch('app.apis.GSCAPIClient')
    @patch('app.apis.PSIAPIClient')
    def api_manager(self, mock_psi, mock_gsc, mock_ga4, mock_exists):
        """Fixture para APIManager."""
        mock_exists.return_value = True
        
        with patch.dict(os.environ, {
            'GA4_PROPERTY_ID': 'test-property',
            'GA4_CREDENTIALS_PATH': 'test-creds.json',
            'GSC_SITE_URL': 'https://example.com',
            'GSC_CREDENTIALS_PATH': 'test-creds.json',
            'PSI_API_KEY': 'test-key'
        }):
            manager = APIManager()
            # Mock dos clientes para que não sejam None
            manager.ga4_client = mock_ga4.return_value
            manager.gsc_client = mock_gsc.return_value
            manager.psi_client = mock_psi.return_value
            return manager
    
    @patch.dict(os.environ, {
        'DEV_MODE': 'false',
        'GA4_PROPERTY_ID': '123456789',
        'GA4_CREDENTIALS_PATH': '/fake/path/ga4.json',
        'GSC_SITE_URL': 'https://example.com',
        'GSC_CREDENTIALS_PATH': '/fake/path/gsc.json',
        'PSI_API_KEY': 'fake_api_key'
    })
    @patch('os.path.exists')
    @patch('app.apis.GA4APIClient')
    @patch('app.apis.GSCAPIClient')
    @patch('app.apis.PSIAPIClient')
    def test_initialization(self, mock_psi, mock_gsc, mock_ga4, mock_exists, api_manager):
        """Testa inicialização do APIManager."""
        # Mock que os arquivos existem
        mock_exists.return_value = True
        
        # Cria nova instância para testar inicialização
        manager = APIManager()
        
        # Verifica se os clientes foram criados
        mock_ga4.assert_called_once()
        mock_gsc.assert_called_once()
        mock_psi.assert_called_once()
    
    def test_get_comprehensive_data_success(self, api_manager):
        """Testa coleta bem-sucedida de dados abrangentes."""
        url = 'https://example.com/test-page'
        
        # Mock dos métodos dos clientes
        with patch.object(api_manager.ga4_client, 'get_page_metrics') as mock_ga4, \
             patch.object(api_manager.gsc_client, 'get_page_performance') as mock_gsc, \
             patch.object(api_manager.psi_client, 'analyze_page') as mock_psi:
            
            # Configurar mocks
            mock_ga4.return_value = {'page_views': 100, 'sessions': 150}
            mock_gsc.return_value = {'clicks': 50, 'impressions': 500}
            mock_psi.return_value = {'performance_score': 85}
            
            result = api_manager.get_comprehensive_data(url)
            
            assert result is not None
            assert 'ga4_data' in result
            assert 'gsc_data' in result
            assert 'psi_mobile_data' in result
            assert 'psi_desktop_data' in result
    
    def test_get_comprehensive_data_partial_failure(self, api_manager):
        """Testa coleta com falha parcial de APIs."""
        url = 'https://example.com/test-page'
        
        # Mock dos métodos dos clientes com uma falha
        with patch.object(api_manager.ga4_client, 'get_page_metrics') as mock_ga4, \
             patch.object(api_manager.gsc_client, 'get_page_performance') as mock_gsc, \
             patch.object(api_manager.psi_client, 'analyze_page') as mock_psi:
            
            # GA4 falha, outros funcionam
            mock_ga4.return_value = None
            mock_gsc.return_value = {'clicks': 50, 'impressions': 500}
            mock_psi.return_value = {'performance_score': 85}
            
            result = api_manager.get_comprehensive_data(url)
            
            assert result is not None
            assert result['ga4_data'] is None
            assert result['gsc_data'] is not None
            assert result['psi_mobile_data'] is not None
            assert result['psi_desktop_data'] is not None
    
    def test_get_comprehensive_data_no_clients(self):
        """Testa coleta de dados sem clientes configurados."""
        with patch.dict(os.environ, {}, clear=True):
            manager = APIManager()
            result = manager.get_comprehensive_data('https://example.com')
            
            # Deve retornar um dicionário com estrutura padrão mas dados vazios
            assert result['url'] == 'https://example.com'
            assert 'timestamp' in result
            assert result['ga4_data'] == {}
            assert result['gsc_data'] == {}
            assert result['psi_mobile_data'] == {}
            assert result['psi_desktop_data'] == {}
    
    @patch('app.apis.GA4APIClient')
    def test_get_ga4_data_only(self, mock_ga4, api_manager):
        """Testa obtenção apenas de dados GA4."""
        url = "https://example.com"
        expected_data = {'page_views': 1000, 'sessions': 800}
        
        # Mock do método get_page_metrics
        with patch.object(api_manager.ga4_client, 'get_page_metrics') as mock_method:
            mock_method.return_value = expected_data
            
            result = api_manager.get_ga4_data(url)
            
            assert result == expected_data
            # O método get_ga4_data extrai o path da URL, então verifica com '/'
            mock_method.assert_called_once_with('/')
    
    @patch('app.apis.GSCAPIClient')
    def test_get_gsc_data_only(self, mock_gsc, api_manager):
        """Testa obtenção apenas de dados GSC."""
        url = "https://example.com"
        expected_data = {'total_clicks': 500, 'total_impressions': 2000}
        
        # Mock do método get_page_performance
        with patch.object(api_manager.gsc_client, 'get_page_performance') as mock_method:
            mock_method.return_value = expected_data
            
            result = api_manager.get_gsc_data(url)
            
            assert result == expected_data
            mock_method.assert_called_once_with(url)
    
    @patch('app.apis.PSIAPIClient')
    def test_get_psi_data_only(self, mock_psi, api_manager):
        """Testa obtenção apenas de dados PSI."""
        url = "https://example.com"
        expected_data = {'performance_score': 85, 'lcp': 1.8}
        
        # Mock do método analyze_page
        with patch.object(api_manager.psi_client, 'analyze_page') as mock_method:
            mock_method.return_value = expected_data
            
            result = api_manager.get_psi_data(url)
            
            # O método get_psi_data retorna dados para mobile e desktop
            expected_result = {
                'mobile': expected_data,
                'desktop': expected_data
            }
            assert result == expected_result
            assert mock_method.call_count == 2  # Chamado para mobile e desktop


class TestAPIIntegration:
    """Testes de integração para os módulos de API."""
    
    @pytest.fixture
    @patch('os.path.exists')
    @patch('app.apis.GA4APIClient')
    @patch('app.apis.GSCAPIClient')
    @patch('app.apis.PSIAPIClient')
    def integration_manager(self, mock_psi, mock_gsc, mock_ga4, mock_exists):
        """Fixture para testes de integração."""
        mock_exists.return_value = True
        
        with patch.dict(os.environ, {
            'GA4_CREDENTIALS_PATH': '/fake/path/ga4.json',
            'GA4_PROPERTY_ID': '123456789',
            'GSC_SITE_URL': 'https://example.com',
            'GSC_CREDENTIALS_PATH': '/fake/path/gsc.json',
            'PSI_API_KEY': 'fake_api_key'
        }):
            manager = APIManager()
            # Mock dos clientes
            manager.ga4_client = mock_ga4.return_value
            manager.gsc_client = mock_gsc.return_value
            manager.psi_client = mock_psi.return_value
            return manager
    
    def test_environment_variables_loading(self, integration_manager):
        """Testa carregamento de variáveis de ambiente."""
        # Verifica se os clientes foram inicializados
        assert integration_manager.ga4_client is not None
        assert integration_manager.gsc_client is not None
        assert integration_manager.psi_client is not None
    
    def test_missing_environment_variables(self):
        """Testa comportamento com variáveis de ambiente ausentes."""
        with patch.dict(os.environ, {}, clear=True):
            # APIManager deve funcionar mesmo sem todas as variáveis
            manager = APIManager()
            assert manager.ga4_client is None
            assert manager.gsc_client is None
            assert manager.psi_client is None


if __name__ == "__main__":
    # Executa os testes se o arquivo for executado diretamente
    pytest.main([__file__, "-v"])