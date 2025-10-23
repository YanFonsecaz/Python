"""
Agente Auditor para validação técnica de SEO.

Este módulo implementa o Agente Auditor que executa validações sequenciais
usando dados de múltiplas fontes (GA4, GSC, PSI, Screaming Frog, Chrome DevTools).
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from .apis import APIManager
from .crawler import CrawlerManager

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado de uma validação específica."""
    validation_type: str
    status: str  # 'passed', 'failed', 'warning', 'error'
    score: float  # 0-100
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AuditReport:
    """Relatório completo de auditoria."""
    url: str
    audit_timestamp: datetime
    overall_score: float
    validations: List[ValidationResult]
    summary: Dict[str, Any]
    raw_data: Dict[str, Any] = field(default_factory=dict)


class ValidationError(Exception):
    """Exceção para erros durante validação."""
    pass


class ValidatorAgent:
    """
    Agente Auditor responsável por executar validações técnicas de SEO.
    
    Coordena a coleta de dados de múltiplas fontes e executa validações
    sequenciais para gerar um relatório completo de auditoria.
    """
    
    def __init__(self, api_manager: APIManager, crawler_manager: CrawlerManager):
        """
        Inicializa o Agente Auditor.
        
        Args:
            api_manager: Gerenciador de APIs externas.
            crawler_manager: Gerenciador de crawling.
        """
        self.api_manager = api_manager
        self.crawler_manager = crawler_manager
        self.logger = logging.getLogger(__name__)
        
        # Configurações de validação
        self.validation_config = {
            'performance_threshold': 75,  # Score mínimo PageSpeed
            'crawl_timeout': 600,  # 10 minutos
            'max_issues_per_type': 50,
            'critical_response_codes': ['404', '500', '503'],
            'warning_response_codes': ['301', '302']
        }
        
        # Pesos para cálculo do score geral
        self.validation_weights = {
            'performance': 0.25,
            'technical_seo': 0.25,
            'content_quality': 0.20,
            'crawlability': 0.15,
            'analytics_health': 0.15
        }
    
    async def execute_full_audit(self, url: str, include_chrome_devtools: bool = True) -> AuditReport:
        """
        Executa uma auditoria completa do website.
        
        Args:
            url: URL do website para auditar.
            include_chrome_devtools: Se deve incluir validações com Chrome DevTools.
        
        Returns:
            Relatório completo de auditoria.
        
        Raises:
            ValidationError: Se houver erro crítico durante a auditoria.
        """
        self.logger.info(f"Iniciando auditoria completa de {url}")
        
        try:
            # Coleta dados de todas as fontes
            audit_data = await self._collect_audit_data(url, include_chrome_devtools)
            
            # Executa validações sequenciais
            validations = await self._execute_validations(url, audit_data)
            
            # Calcula score geral
            overall_score = self._calculate_overall_score(validations)
            
            # Gera resumo
            summary = self._generate_summary(validations, audit_data)
            
            # Cria relatório final
            report = AuditReport(
                url=url,
                audit_timestamp=datetime.now(),
                overall_score=overall_score,
                validations=validations,
                summary=summary,
                raw_data=audit_data
            )
            
            self.logger.info(f"Auditoria concluída. Score geral: {overall_score:.1f}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Erro durante auditoria: {str(e)}")
            raise ValidationError(f"Falha na auditoria: {str(e)}")
    
    async def _collect_audit_data(self, url: str, include_chrome_devtools: bool) -> Dict[str, Any]:
        """
        Coleta dados de todas as fontes para auditoria.
        
        Args:
            url: URL do website.
            include_chrome_devtools: Se deve incluir dados do Chrome DevTools.
        
        Returns:
            Dicionário com dados coletados de todas as fontes.
        """
        audit_data = {}
        
        # Coleta dados em paralelo quando possível
        tasks = []
        
        # PageSpeed Insights
        if self.api_manager.psi_client:
            tasks.append(self._collect_psi_data(url))
        
        # Google Search Console (se disponível)
        if self.api_manager.gsc_client:
            tasks.append(self._collect_gsc_data(url))
        
        # Google Analytics 4 (se disponível)
        if self.api_manager.ga4_client:
            tasks.append(self._collect_ga4_data(url))
        
        # Executa tarefas paralelas
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.warning(f"Erro na coleta de dados da tarefa {i}: {str(result)}")
                else:
                    audit_data.update(result)
        
        # Screaming Frog (sequencial devido à natureza do processo)
        if self.crawler_manager.is_available():
            try:
                crawl_data = self.crawler_manager.execute_full_audit_crawl(url)
                audit_data['screaming_frog'] = crawl_data
            except Exception as e:
                self.logger.warning(f"Erro no crawl Screaming Frog: {str(e)}")
        
        # Chrome DevTools (se solicitado)
        if include_chrome_devtools:
            try:
                chrome_data = await self._collect_chrome_devtools_data(url)
                audit_data['chrome_devtools'] = chrome_data
            except Exception as e:
                self.logger.warning(f"Erro na coleta Chrome DevTools: {str(e)}")
        
        return audit_data
    
    async def _collect_psi_data(self, url: str) -> Dict[str, Any]:
        """Coleta dados do PageSpeed Insights."""
        try:
            mobile_data = self.api_manager.psi_client.analyze_page(url, strategy='mobile')
            desktop_data = self.api_manager.psi_client.analyze_page(url, strategy='desktop')
            
            return {
                'pagespeed': {
                    'mobile': mobile_data,
                    'desktop': desktop_data
                }
            }
        except Exception as e:
            self.logger.warning(f"Erro ao coletar dados PSI: {str(e)}")
            return {}
    
    async def _collect_gsc_data(self, url: str) -> Dict[str, Any]:
        """Coleta dados do Google Search Console."""
        try:
            # Últimos 30 dias
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            search_analytics = self.api_manager.gsc_client.get_search_analytics(
                site_url=url,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            return {
                'search_console': {
                    'search_analytics': search_analytics
                }
            }
        except Exception as e:
            self.logger.warning(f"Erro ao coletar dados GSC: {str(e)}")
            return {}
    
    async def _collect_ga4_data(self, url: str) -> Dict[str, Any]:
        """Coleta dados do Google Analytics 4."""
        try:
            # Últimos 30 dias de dados básicos
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            basic_report = self.api_manager.ga4_client.get_basic_report(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            return {
                'analytics': {
                    'basic_report': basic_report
                }
            }
        except Exception as e:
            self.logger.warning(f"Erro ao coletar dados GA4: {str(e)}")
            return {}
    
    async def _collect_chrome_devtools_data(self, url: str) -> Dict[str, Any]:
        """
        Coleta dados usando Chrome DevTools MCP.
        
        Args:
            url: URL para analisar.
        
        Returns:
            Dados coletados do Chrome DevTools.
        """
        # Nota: Esta implementação seria expandida com as ferramentas MCP Chrome DevTools
        # Por enquanto, retorna estrutura básica
        return {
            'performance_trace': {},
            'network_requests': [],
            'console_messages': [],
            'lighthouse_audit': {}
        }
    
    async def _execute_validations(self, url: str, audit_data: Dict[str, Any]) -> List[ValidationResult]:
        """
        Executa todas as validações sequenciais.
        
        Args:
            url: URL do website.
            audit_data: Dados coletados para auditoria.
        
        Returns:
            Lista de resultados de validação.
        """
        validations = []
        
        # Validações de Performance
        validations.extend(await self._validate_performance(audit_data))
        
        # Validações de SEO Técnico
        validations.extend(await self._validate_technical_seo(audit_data))
        
        # Validações de Qualidade de Conteúdo
        validations.extend(await self._validate_content_quality(audit_data))
        
        # Validações de Crawlability
        validations.extend(await self._validate_crawlability(audit_data))
        
        # Validações de Saúde do Analytics
        validations.extend(await self._validate_analytics_health(audit_data))
        
        return validations
    
    async def _validate_performance(self, audit_data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida aspectos de performance do website."""
        validations = []
        
        psi_data = audit_data.get('pagespeed', {})
        
        # Validação PageSpeed Mobile
        if 'mobile' in psi_data:
            mobile_score_raw = psi_data['mobile'].get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0)
            # Garante que o score é um número válido
            if isinstance(mobile_score_raw, (int, float)) and mobile_score_raw is not None:
                mobile_score = mobile_score_raw * 100
            else:
                mobile_score = 0
            
            if mobile_score >= self.validation_config['performance_threshold']:
                status = 'passed'
                message = f"Performance mobile excelente: {mobile_score:.1f}/100"
            elif mobile_score >= 50:
                status = 'warning'
                message = f"Performance mobile precisa melhorar: {mobile_score:.1f}/100"
            else:
                status = 'failed'
                message = f"Performance mobile crítica: {mobile_score:.1f}/100"
            
            validations.append(ValidationResult(
                validation_type='performance_mobile',
                status=status,
                score=mobile_score,
                message=message,
                details={'raw_score': mobile_score},
                recommendations=self._get_performance_recommendations(psi_data['mobile'])
            ))
        
        # Validação PageSpeed Desktop
        if 'desktop' in psi_data:
            desktop_score_raw = psi_data['desktop'].get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0)
            # Garante que o score é um número válido
            if isinstance(desktop_score_raw, (int, float)) and desktop_score_raw is not None:
                desktop_score = desktop_score_raw * 100
            else:
                desktop_score = 0
            
            if desktop_score >= self.validation_config['performance_threshold']:
                status = 'passed'
                message = f"Performance desktop excelente: {desktop_score:.1f}/100"
            elif desktop_score >= 50:
                status = 'warning'
                message = f"Performance desktop precisa melhorar: {desktop_score:.1f}/100"
            else:
                status = 'failed'
                message = f"Performance desktop crítica: {desktop_score:.1f}/100"
            
            validations.append(ValidationResult(
                validation_type='performance_desktop',
                status=status,
                score=desktop_score,
                message=message,
                details={'raw_score': desktop_score},
                recommendations=self._get_performance_recommendations(psi_data['desktop'])
            ))
        
        return validations
    
    async def _validate_technical_seo(self, audit_data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida aspectos técnicos de SEO."""
        validations = []
        
        crawl_data = audit_data.get('screaming_frog', {})
        
        if crawl_data:
            summary = crawl_data.get('summary', {})
            issues = crawl_data.get('technical_issues', [])
            
            # Validação de códigos de resposta
            error_codes = {k: v for k, v in summary.get('response_codes_count', {}).items() 
                          if k in self.validation_config['critical_response_codes']}
            
            if not error_codes:
                validations.append(ValidationResult(
                    validation_type='response_codes',
                    status='passed',
                    score=100,
                    message="Nenhum código de erro crítico encontrado",
                    details={'error_codes': error_codes}
                ))
            else:
                total_errors = sum(error_codes.values())
                score = max(0, 100 - (total_errors * 5))  # -5 pontos por erro
                
                validations.append(ValidationResult(
                    validation_type='response_codes',
                    status='failed' if score < 70 else 'warning',
                    score=score,
                    message=f"{total_errors} páginas com códigos de erro encontradas",
                    details={'error_codes': error_codes},
                    recommendations=["Corrigir páginas com códigos de erro HTTP", "Implementar redirecionamentos adequados"]
                ))
            
            # Validação de títulos
            missing_titles = summary.get('pages_without_title', 0)
            total_pages = summary.get('total_urls', 0)
            
            if total_pages > 0:
                title_score = max(0, 100 - ((missing_titles / total_pages) * 100))
            else:
                title_score = 0
            
            validations.append(ValidationResult(
                validation_type='page_titles',
                status='failed' if total_pages == 0 else ('passed' if missing_titles == 0 else ('warning' if title_score > 70 else 'failed')),
                score=title_score,
                message=f"{missing_titles} páginas sem título de {total_pages} páginas" if total_pages > 0 else "Nenhuma página encontrada para análise",
                details={'missing_titles': missing_titles, 'total_pages': total_pages},
                recommendations=["Verificar se o site está acessível", "Verificar robots.txt e sitemap"] if total_pages == 0 else (["Adicionar títulos únicos e descritivos para todas as páginas"] if missing_titles > 0 else [])
            ))
            
            # Validação de meta descriptions
            missing_meta = summary.get('pages_without_meta_description', 0)
            
            if total_pages > 0:
                meta_score = max(0, 100 - ((missing_meta / total_pages) * 100))
            else:
                meta_score = 0
            
            validations.append(ValidationResult(
                validation_type='meta_descriptions',
                status='passed' if missing_meta == 0 else ('warning' if meta_score > 70 else 'failed'),
                score=meta_score,
                message=f"{missing_meta} páginas sem meta description de {total_pages} páginas",
                details={'missing_meta': missing_meta, 'total_pages': total_pages},
                recommendations=["Adicionar meta descriptions únicas e atrativas"] if missing_meta > 0 else []
            ))
        
        return validations
    
    async def _validate_content_quality(self, audit_data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida qualidade do conteúdo."""
        validations = []
        
        crawl_data = audit_data.get('screaming_frog', {})
        
        if crawl_data:
            summary = crawl_data.get('summary', {})
            
            # Validação de H1
            missing_h1 = summary.get('pages_without_h1', 0)
            total_pages = summary.get('total_urls', 0)
            
            if total_pages > 0:
                h1_score = max(0, 100 - ((missing_h1 / total_pages) * 100))
            else:
                h1_score = 0
            
            validations.append(ValidationResult(
                validation_type='h1_tags',
                status='passed' if missing_h1 == 0 else ('warning' if h1_score > 70 else 'failed'),
                score=h1_score,
                message=f"{missing_h1} páginas sem H1 de {total_pages} páginas",
                details={'missing_h1': missing_h1, 'total_pages': total_pages},
                recommendations=["Adicionar tags H1 únicas para todas as páginas"] if missing_h1 > 0 else []
            ))
        
        return validations
    
    async def _validate_crawlability(self, audit_data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida aspectos de crawlability."""
        validations = []
        
        crawl_data = audit_data.get('screaming_frog', {})
        
        if crawl_data:
            summary = crawl_data.get('summary', {})
            total_urls = summary.get('total_urls', 0)
            
            # Validação básica de crawlability
            if total_urls > 0:
                validations.append(ValidationResult(
                    validation_type='crawlability',
                    status='passed',
                    score=100,
                    message=f"Website crawlável: {total_urls} URLs descobertas",
                    details={'total_urls': total_urls}
                ))
            else:
                validations.append(ValidationResult(
                    validation_type='crawlability',
                    status='failed',
                    score=0,
                    message="Nenhuma URL foi descoberta durante o crawl",
                    details={'total_urls': total_urls},
                    recommendations=["Verificar robots.txt", "Verificar sitemap.xml", "Verificar estrutura de links internos"]
                ))
        
        return validations
    
    async def _validate_analytics_health(self, audit_data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida saúde do analytics."""
        validations = []
        
        ga4_data = audit_data.get('analytics', {})
        gsc_data = audit_data.get('search_console', {})
        
        # Validação GA4
        if ga4_data:
            validations.append(ValidationResult(
                validation_type='ga4_integration',
                status='passed',
                score=100,
                message="Google Analytics 4 configurado e coletando dados",
                details={'has_data': bool(ga4_data)}
            ))
        else:
            validations.append(ValidationResult(
                validation_type='ga4_integration',
                status='warning',
                score=50,
                message="Google Analytics 4 não configurado ou sem dados",
                recommendations=["Configurar Google Analytics 4", "Verificar código de tracking"]
            ))
        
        # Validação GSC
        if gsc_data:
            validations.append(ValidationResult(
                validation_type='gsc_integration',
                status='passed',
                score=100,
                message="Google Search Console configurado e coletando dados",
                details={'has_data': bool(gsc_data)}
            ))
        else:
            validations.append(ValidationResult(
                validation_type='gsc_integration',
                status='warning',
                score=50,
                message="Google Search Console não configurado ou sem dados",
                recommendations=["Configurar Google Search Console", "Verificar propriedade do site"]
            ))
        
        return validations
    
    def _calculate_overall_score(self, validations: List[ValidationResult]) -> float:
        """
        Calcula o score geral baseado nos pesos das validações.
        
        Args:
            validations: Lista de resultados de validação.
        
        Returns:
            Score geral (0-100).
        """
        # Se não há validações, retorna 0
        if not validations:
            return 0
            
        category_scores = {}
        category_counts = {}
        
        # Agrupa validações por categoria
        for validation in validations:
            category = self._get_validation_category(validation.validation_type)
            
            if category not in category_scores:
                category_scores[category] = 0
                category_counts[category] = 0
            
            category_scores[category] += validation.score
            category_counts[category] += 1
        
        # Calcula média por categoria
        weighted_score = 0
        total_weight = 0
        
        for category, weight in self.validation_weights.items():
            if category in category_scores and category_counts[category] > 0:
                avg_score = category_scores[category] / category_counts[category]
                weighted_score += avg_score * weight
                total_weight += weight
        
        # Normaliza se nem todas as categorias estão presentes
        if total_weight > 0:
            return weighted_score / total_weight
        
        return 0
    
    def _get_validation_category(self, validation_type: str) -> str:
        """Mapeia tipo de validação para categoria."""
        mapping = {
            'performance_mobile': 'performance',
            'performance_desktop': 'performance',
            'response_codes': 'technical_seo',
            'page_titles': 'technical_seo',
            'meta_descriptions': 'technical_seo',
            'h1_tags': 'content_quality',
            'crawlability': 'crawlability',
            'ga4_integration': 'analytics_health',
            'gsc_integration': 'analytics_health'
        }
        
        return mapping.get(validation_type, 'technical_seo')
    
    def _get_performance_recommendations(self, psi_data: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos dados do PageSpeed."""
        recommendations = []
        
        lighthouse_result = psi_data.get('lighthouseResult', {})
        audits = lighthouse_result.get('audits', {})
        
        # Verifica principais métricas
        if audits.get('largest-contentful-paint', {}).get('score', 1) < 0.5:
            recommendations.append("Otimizar Largest Contentful Paint (LCP)")
        
        if audits.get('first-input-delay', {}).get('score', 1) < 0.5:
            recommendations.append("Melhorar First Input Delay (FID)")
        
        if audits.get('cumulative-layout-shift', {}).get('score', 1) < 0.5:
            recommendations.append("Reduzir Cumulative Layout Shift (CLS)")
        
        if audits.get('unused-css-rules', {}).get('score', 1) < 0.5:
            recommendations.append("Remover CSS não utilizado")
        
        if audits.get('render-blocking-resources', {}).get('score', 1) < 0.5:
            recommendations.append("Eliminar recursos que bloqueiam a renderização")
        
        return recommendations
    
    def _generate_summary(self, validations: List[ValidationResult], audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera resumo da auditoria.
        
        Args:
            validations: Lista de validações executadas.
            audit_data: Dados brutos da auditoria.
        
        Returns:
            Dicionário com resumo da auditoria.
        """
        # Conta validações por status
        status_counts = {'passed': 0, 'warning': 0, 'failed': 0, 'error': 0}
        for validation in validations:
            status_counts[validation.status] = status_counts.get(validation.status, 0) + 1
        
        # Identifica principais problemas
        critical_issues = [v for v in validations if v.status == 'failed']
        warnings = [v for v in validations if v.status == 'warning']
        
        # Coleta todas as recomendações
        all_recommendations = []
        for validation in validations:
            all_recommendations.extend(validation.recommendations)
        
        return {
            'total_validations': len(validations),
            'status_counts': status_counts,
            'critical_issues_count': len(critical_issues),
            'warnings_count': len(warnings),
            'top_critical_issues': [issue.message for issue in critical_issues[:5]],
            'top_recommendations': list(set(all_recommendations))[:10],
            'data_sources': list(audit_data.keys()),
            'audit_completeness': len(audit_data) / 5 * 100  # Assumindo 5 fontes possíveis
        }