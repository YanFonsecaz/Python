"""
Módulo de integração com APIs externas para auditoria SEO.
Integra com Google Analytics 4, Google Search Console e PageSpeed Insights.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuração de logging
logger = logging.getLogger(__name__)


class GA4APIClient:
    """Cliente para integração com Google Analytics 4 API."""
    
    def __init__(self, property_id: str, credentials_path: str):
        """
        Inicializa o cliente GA4.
        
        Args:
            property_id: ID da propriedade GA4
            credentials_path: Caminho para o arquivo de credenciais JSON
        """
        self.property_id = property_id
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Autentica com a API do Google Analytics 4."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
            self.service = build('analyticsdata', 'v1beta', credentials=credentials)
            logger.info("Autenticação GA4 realizada com sucesso")
        except Exception as e:
            logger.error(f"Erro na autenticação GA4: {e}")
            raise
    
    def get_page_metrics(self, url_path: str, days: int = 30) -> Dict[str, Any]:
        """
        Obtém métricas de uma página específica.
        
        Args:
            url_path: Caminho da URL para análise
            days: Número de dias para análise (padrão: 30)
            
        Returns:
            Dicionário com métricas da página
        """
        if not self.service:
            logger.warning("Cliente GA4 não autenticado")
            return {}
            
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            request = {
                'property': f'properties/{self.property_id}',
                'dateRanges': [{
                    'startDate': start_date.strftime('%Y-%m-%d'),
                    'endDate': end_date.strftime('%Y-%m-%d')
                }],
                'dimensions': [
                    {'name': 'pagePath'},
                    {'name': 'pageTitle'}
                ],
                'metrics': [
                    {'name': 'screenPageViews'},
                    {'name': 'sessions'},
                    {'name': 'bounceRate'},
                    {'name': 'averageSessionDuration'},
                    {'name': 'conversions'}
                ],
                'dimensionFilter': {
                    'filter': {
                        'fieldName': 'pagePath',
                        'stringFilter': {
                            'matchType': 'EXACT',
                            'value': url_path
                        }
                    }
                }
            }
            
            response = self.service.properties().runReport(
                property=f'properties/{self.property_id}',
                body=request
            ).execute()
            
            if 'rows' in response and response['rows']:
                row = response['rows'][0]
                return {
                    'page_views': int(row['metricValues'][0]['value']),
                    'sessions': int(row['metricValues'][1]['value']),
                    'bounce_rate': float(row['metricValues'][2]['value']),
                    'avg_session_duration': float(row['metricValues'][3]['value']),
                    'conversions': int(row['metricValues'][4]['value']),
                    'page_title': row['dimensionValues'][1]['value']
                }
            else:
                return {
                    'page_views': 0,
                    'sessions': 0,
                    'bounce_rate': 0.0,
                    'avg_session_duration': 0.0,
                    'conversions': 0,
                    'page_title': 'N/A'
                }
                
        except HttpError as e:
            logger.error(f"Erro na API GA4: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro inesperado GA4: {e}")
            return {}


class GSCAPIClient:
    """Cliente para integração com Google Search Console API."""
    
    def __init__(self, site_url: str, credentials_path: str):
        """
        Inicializa o cliente GSC.
        
        Args:
            site_url: URL do site no GSC
            credentials_path: Caminho para o arquivo de credenciais JSON
        """
        self.site_url = site_url
        self.credentials_path = credentials_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Autentica com a API do Google Search Console."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            self.service = build('searchconsole', 'v1', credentials=credentials)
            logger.info("Autenticação GSC realizada com sucesso")
        except Exception as e:
            logger.error(f"Erro na autenticação GSC: {e}")
            raise
    
    def get_page_performance(self, url: str, days: int = 30) -> Dict[str, Any]:
        """
        Obtém dados de performance de uma página no GSC.
        
        Args:
            url: URL completa da página
            days: Número de dias para análise (padrão: 30)
            
        Returns:
            Dicionário com dados de performance
        """
        if not self.service:
            logger.warning("Cliente GSC não autenticado")
            return {}
            
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            request = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': ['page'],
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'page',
                        'operator': 'equals',
                        'expression': url
                    }]
                }]
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request
            ).execute()
            
            if 'rows' in response and response['rows']:
                row = response['rows'][0]
                return {
                    'clicks': row.get('clicks', 0),
                    'impressions': row.get('impressions', 0),
                    'ctr': row.get('ctr', 0.0),
                    'position': row.get('position', 0.0)
                }
            else:
                return {
                    'clicks': 0,
                    'impressions': 0,
                    'ctr': 0.0,
                    'position': 0.0
                }
                
        except HttpError as e:
            logger.error(f"Erro na API GSC: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro inesperado GSC: {e}")
            return {}
    
    def get_indexing_status(self, url: str) -> Dict[str, Any]:
        """
        Verifica o status de indexação de uma URL.
        
        Args:
            url: URL para verificar
            
        Returns:
            Dicionário com status de indexação
        """
        try:
            response = self.service.urlInspection().index().inspect(
                body={'inspectionUrl': url, 'siteUrl': self.site_url}
            ).execute()
            
            index_status = response.get('indexStatusResult', {})
            return {
                'coverage_state': index_status.get('coverageState', 'UNKNOWN'),
                'indexability_state': index_status.get('indexabilityState', 'UNKNOWN'),
                'last_crawl_time': index_status.get('lastCrawlTime', ''),
                'page_fetch_state': index_status.get('pageFetchState', 'UNKNOWN')
            }
            
        except HttpError as e:
            logger.error(f"Erro na verificação de indexação GSC: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro inesperado na verificação de indexação: {e}")
            return {}


class PSIAPIClient:
    """Cliente para integração com PageSpeed Insights API."""
    
    def __init__(self, api_key: str):
        """
        Inicializa o cliente PSI.
        
        Args:
            api_key: Chave da API do PageSpeed Insights
        """
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    def analyze_page(self, url: str, strategy: str = 'mobile') -> Dict[str, Any]:
        """
        Analisa uma página com PageSpeed Insights.
        
        Args:
            url: URL da página para análise
            strategy: Estratégia de análise ('mobile' ou 'desktop')
            
        Returns:
            Dicionário com métricas de performance
        """
        try:
            params = {
                'url': url,
                'key': self.api_key,
                'strategy': strategy,
                'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO']
            }
            
            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            lighthouse_result = data.get('lighthouseResult', {})
            categories = lighthouse_result.get('categories', {})
            audits = lighthouse_result.get('audits', {})
            
            # Core Web Vitals
            core_web_vitals = {}
            if 'largest-contentful-paint' in audits:
                core_web_vitals['lcp'] = audits['largest-contentful-paint'].get('numericValue', 0) / 1000
            if 'first-input-delay' in audits:
                core_web_vitals['fid'] = audits['first-input-delay'].get('numericValue', 0)
            if 'cumulative-layout-shift' in audits:
                core_web_vitals['cls'] = audits['cumulative-layout-shift'].get('numericValue', 0)
            
            # Função auxiliar para extrair score de forma segura
            def safe_score(category_data, default=0):
                score = category_data.get('score', default)
                if isinstance(score, (int, float)) and score is not None:
                    return score * 100
                return default
            
            return {
                'performance_score': safe_score(categories.get('performance', {})),
                'accessibility_score': safe_score(categories.get('accessibility', {})),
                'best_practices_score': safe_score(categories.get('best-practices', {})),
                'seo_score': safe_score(categories.get('seo', {})),
                'core_web_vitals': core_web_vitals,
                'loading_experience': data.get('loadingExperience', {}),
                'origin_loading_experience': data.get('originLoadingExperience', {}),
                'strategy': strategy
            }
            
        except requests.RequestException as e:
            logger.error(f"Erro na requisição PSI: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro inesperado PSI: {e}")
            return {}


class APIManager:
    """Gerenciador centralizado para todas as APIs."""
    
    def __init__(self):
        """Inicializa o gerenciador de APIs com configurações do ambiente."""
        self.ga4_client = None
        self.gsc_client = None
        self.psi_client = None
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Inicializa todos os clientes de API opcionalmente."""
        # Verificar se está em modo de desenvolvimento
        dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
        
        if dev_mode:
            logger.info("Modo de desenvolvimento ativado - APIs externas desabilitadas")
            return
            
        try:
            # GA4 - Opcional
            ga4_property_id = os.getenv('GA4_PROPERTY_ID')
            ga4_credentials_path = os.getenv('GA4_CREDENTIALS_PATH')
            if ga4_property_id and ga4_credentials_path and os.path.exists(ga4_credentials_path):
                try:
                    self.ga4_client = GA4APIClient(ga4_property_id, ga4_credentials_path)
                    logger.info("Cliente GA4 inicializado com sucesso")
                except Exception as e:
                    logger.warning(f"Falha ao inicializar GA4 (opcional): {e}")
            else:
                logger.info("GA4 não configurado - continuando sem dados do Google Analytics")
            
            # GSC - Opcional
            gsc_site_url = os.getenv('GSC_SITE_URL')
            gsc_credentials_path = os.getenv('GSC_CREDENTIALS_PATH')
            if gsc_site_url and gsc_credentials_path and os.path.exists(gsc_credentials_path):
                try:
                    self.gsc_client = GSCAPIClient(gsc_site_url, gsc_credentials_path)
                    logger.info("Cliente GSC inicializado com sucesso")
                except Exception as e:
                    logger.warning(f"Falha ao inicializar GSC (opcional): {e}")
            else:
                logger.info("GSC não configurado - continuando sem dados do Search Console")
            
            # PSI - Opcional
            psi_api_key = os.getenv('PSI_API_KEY')
            if psi_api_key:
                try:
                    self.psi_client = PSIAPIClient(psi_api_key)
                    logger.info("Cliente PSI inicializado com sucesso")
                except Exception as e:
                    logger.warning(f"Falha ao inicializar PSI (opcional): {e}")
            else:
                logger.info("PSI não configurado - continuando sem dados do PageSpeed Insights")
                
            logger.info("Inicialização de clientes de API concluída")
            
        except Exception as e:
            logger.warning(f"Erro na inicialização dos clientes de API (continuando sem APIs): {e}")
    
    def get_comprehensive_data(self, url: str) -> Dict[str, Any]:
        """
        Obtém dados abrangentes de todas as APIs para uma URL.
        
        Args:
            url: URL para análise
            
        Returns:
            Dicionário com dados de todas as APIs
        """
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'ga4_data': {},
            'gsc_data': {},
            'psi_mobile_data': {},
            'psi_desktop_data': {}
        }
        
        # Extrair path da URL para GA4
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        url_path = parsed_url.path or '/'
        
        # GA4 Data
        if self.ga4_client:
            try:
                result['ga4_data'] = self.ga4_client.get_page_metrics(url_path)
            except Exception as e:
                logger.error(f"Erro ao obter dados GA4 para {url}: {e}")
        
        # GSC Data
        if self.gsc_client:
            try:
                performance_data = self.gsc_client.get_page_performance(url)
                indexing_data = self.gsc_client.get_indexing_status(url)
                result['gsc_data'] = {**performance_data, **indexing_data}
            except Exception as e:
                logger.error(f"Erro ao obter dados GSC para {url}: {e}")
        
        # PSI Data (Mobile e Desktop)
        if self.psi_client:
            try:
                result['psi_mobile_data'] = self.psi_client.analyze_page(url, 'mobile')
                result['psi_desktop_data'] = self.psi_client.analyze_page(url, 'desktop')
            except Exception as e:
                logger.error(f"Erro ao obter dados PSI para {url}: {e}")
        
        return result
    
    def get_ga4_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Coleta dados do Google Analytics 4 (opcional).
        
        Args:
            url: URL para análise
            
        Returns:
            Dados do GA4 ou None se não configurado
        """
        if not self.ga4_client:
            logger.info("GA4 não configurado - pulando coleta de dados")
            return None
            
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            url_path = parsed_url.path or '/'
            
            return self.ga4_client.get_page_metrics(url_path)
        except Exception as e:
            logger.warning(f"Erro ao coletar dados GA4: {str(e)}")
            return None
    
    def get_gsc_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Coleta dados do Google Search Console (opcional).
        
        Args:
            url: URL para análise
            
        Returns:
            Dados do GSC ou None se não configurado
        """
        if not self.gsc_client:
            logger.info("GSC não configurado - pulando coleta de dados")
            return None
            
        try:
            performance_data = self.gsc_client.get_page_performance(url)
            indexing_data = self.gsc_client.get_indexing_status(url)
            return {**performance_data, **indexing_data}
        except Exception as e:
            logger.warning(f"Erro ao coletar dados GSC: {str(e)}")
            return None
    
    def get_psi_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Coleta dados do PageSpeed Insights (opcional).
        
        Args:
            url: URL para análise
            
        Returns:
            Dados do PSI ou None se não configurado
        """
        if not self.psi_client:
            logger.info("PSI não configurado - pulando coleta de dados")
            return None
            
        try:
            mobile_data = self.psi_client.analyze_page(url, 'mobile')
            desktop_data = self.psi_client.analyze_page(url, 'desktop')
            return {
                'mobile': mobile_data,
                'desktop': desktop_data
            }
        except Exception as e:
            logger.warning(f"Erro ao coletar dados PSI: {str(e)}")
            return None