"""
Módulo de Consolidação de Dados de Auditoria SEO.

Este módulo processa e integra dados de múltiplas fontes (GA4, GSC, PSI, 
Screaming Frog, Chrome DevTools) para gerar insights consolidados e 
relatórios unificados de auditoria técnica de SEO.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

from .validator_agent import ValidationResult, AuditReport

logger = logging.getLogger(__name__)


@dataclass
class ConsolidatedMetrics:
    """
    Métricas consolidadas de múltiplas fontes.
    
    Attributes:
        performance_score: Score consolidado de performance (0-100).
        seo_health_score: Score de saúde SEO (0-100).
        technical_score: Score técnico geral (0-100).
        content_quality_score: Score de qualidade do conteúdo (0-100).
        analytics_health_score: Score de saúde do analytics (0-100).
        overall_score: Score geral consolidado (0-100).
        critical_issues_count: Número de problemas críticos.
        warning_issues_count: Número de avisos.
        data_completeness: Percentual de completude dos dados (0-100).
        confidence_level: Nível de confiança da análise (0-100).
    """
    performance_score: float
    seo_health_score: float
    technical_score: float
    content_quality_score: float
    analytics_health_score: float
    overall_score: float
    critical_issues_count: int
    warning_issues_count: int
    data_completeness: float
    confidence_level: float


@dataclass
class DataSourceStatus:
    """
    Status de disponibilidade das fontes de dados.
    
    Attributes:
        ga4_available: Google Analytics 4 disponível.
        gsc_available: Google Search Console disponível.
        psi_available: PageSpeed Insights disponível.
        screaming_frog_available: Screaming Frog disponível.
        chrome_devtools_available: Chrome DevTools disponível.
        data_sources_count: Número total de fontes disponíveis.
        completeness_percentage: Percentual de completude das fontes.
    """
    ga4_available: bool
    gsc_available: bool
    psi_available: bool
    screaming_frog_available: bool
    chrome_devtools_available: bool
    data_sources_count: int
    completeness_percentage: float


@dataclass
class ConsolidatedInsight:
    """
    Insight consolidado baseado em múltiplas fontes.
    
    Attributes:
        insight_type: Tipo do insight (performance, seo, technical, etc.).
        title: Título do insight.
        description: Descrição detalhada.
        severity: Severidade (critical, warning, info).
        confidence: Nível de confiança (0-100).
        supporting_data: Dados que suportam o insight.
        recommendations: Lista de recomendações.
        affected_pages: Páginas afetadas (se aplicável).
        data_sources: Fontes de dados que contribuíram.
    """
    insight_type: str
    title: str
    description: str
    severity: str
    confidence: float
    supporting_data: Dict[str, Any]
    recommendations: List[str]
    affected_pages: List[str]
    data_sources: List[str]


class DataConsolidator:
    """
    Consolidador de dados de múltiplas fontes.
    
    Processa e integra dados de diferentes APIs e ferramentas para
    gerar uma visão unificada da auditoria SEO.
    """
    
    # Pesos para cálculo de scores consolidados
    SCORE_WEIGHTS = {
        'performance': 0.25,
        'seo_health': 0.25,
        'technical': 0.20,
        'content_quality': 0.15,
        'analytics_health': 0.15
    }
    
    # Mapeamento de tipos de validação para categorias
    VALIDATION_CATEGORIES = {
        'performance_mobile': 'performance',
        'performance_desktop': 'performance',
        'core_web_vitals': 'performance',
        'page_speed': 'performance',
        
        'response_codes': 'technical',
        'crawlability': 'technical',
        'robots_txt': 'technical',
        'sitemap_xml': 'technical',
        'ssl_certificate': 'technical',
        'redirects': 'technical',
        
        'page_titles': 'seo_health',
        'meta_descriptions': 'seo_health',
        'canonical_tags': 'seo_health',
        'structured_data': 'seo_health',
        'internal_linking': 'seo_health',
        
        'h1_tags': 'content_quality',
        'content_length': 'content_quality',
        'keyword_density': 'content_quality',
        'image_alt_tags': 'content_quality',
        
        'ga4_integration': 'analytics_health',
        'gsc_integration': 'analytics_health',
        'tracking_codes': 'analytics_health'
    }
    
    def __init__(self):
        """Inicializa o consolidador de dados."""
        self.logger = logging.getLogger(__name__)
    
    def consolidate_audit_data(self, raw_data: Dict[str, Any], 
                             validations: List[ValidationResult]) -> Tuple[ConsolidatedMetrics, List[ConsolidatedInsight]]:
        """
        Consolida dados de auditoria de múltiplas fontes.
        
        Args:
            raw_data: Dados brutos de todas as fontes.
            validations: Lista de validações executadas.
        
        Returns:
            Tupla com métricas consolidadas e insights.
        """
        try:
            self.logger.info("Iniciando consolidação de dados de auditoria")
            
            # Analisa disponibilidade das fontes
            data_source_status = self._analyze_data_sources(raw_data)
            
            # Calcula métricas consolidadas
            consolidated_metrics = self._calculate_consolidated_metrics(
                validations, data_source_status
            )
            
            # Gera insights consolidados
            consolidated_insights = self._generate_consolidated_insights(
                raw_data, validations, consolidated_metrics
            )
            
            self.logger.info(f"Consolidação concluída: {len(consolidated_insights)} insights gerados")
            
            return consolidated_metrics, consolidated_insights
            
        except Exception as e:
            self.logger.error(f"Erro na consolidação de dados: {str(e)}")
            raise
    
    def consolidate_multiple_audits(self, audits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolida dados de múltiplas auditorias para análise comparativa.
        
        Args:
            audits: Lista de auditorias com seus dados completos.
            
        Returns:
            Dicionário com dados consolidados de múltiplas auditorias.
        """
        try:
            self.logger.info(f"Consolidando dados de {len(audits)} auditorias")
            
            if not audits:
                return {
                    'total_audits': 0,
                    'metrics_summary': {},
                    'trends': [],
                    'common_issues': []
                }
            
            # Agregar métricas de todas as auditorias
            all_scores = []
            category_scores = defaultdict(list)
            all_issues = []
            status_counts = defaultdict(int)
            
            for audit in audits:
                # Coletar scores
                if audit.get('overall_score'):
                    all_scores.append(audit['overall_score'])
                
                # Coletar scores por categoria (se disponível)
                if audit.get('category_scores'):
                    for category, score in audit['category_scores'].items():
                        category_scores[category].append(score)
                
                # Coletar problemas
                if audit.get('validation_results'):
                    for validation in audit['validation_results']:
                        if validation.get('status') == 'failed':
                            all_issues.append({
                                'type': validation.get('validation_type', 'Unknown'),
                                'severity': validation.get('severity', 'medium'),
                                'audit_id': audit.get('audit_id'),
                                'url': audit.get('url')
                            })
                
                # Contar status
                status = audit.get('status', 'unknown')
                status_counts[status] += 1
            
            # Calcular estatísticas consolidadas
            metrics_summary = {
                'average_score': statistics.mean(all_scores) if all_scores else 0,
                'median_score': statistics.median(all_scores) if all_scores else 0,
                'min_score': min(all_scores) if all_scores else 0,
                'max_score': max(all_scores) if all_scores else 0,
                'score_std_dev': statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
                'total_issues': len(all_issues),
                'status_distribution': dict(status_counts)
            }
            
            # Calcular médias por categoria
            for category, scores in category_scores.items():
                metrics_summary[f'{category}_average'] = statistics.mean(scores)
            
            # Identificar problemas mais comuns
            from collections import Counter
            issue_counts = Counter([issue['type'] for issue in all_issues])
            common_issues = [
                {
                    'issue_type': issue_type,
                    'count': count,
                    'percentage': (count / len(audits)) * 100,
                    'severity_distribution': self._analyze_issue_severity(all_issues, issue_type)
                }
                for issue_type, count in issue_counts.most_common(10)
            ]
            
            # Analisar tendências temporais (se houver timestamps)
            trends = self._analyze_temporal_trends(audits)
            
            consolidated_data = {
                'total_audits': len(audits),
                'metrics_summary': metrics_summary,
                'common_issues': common_issues,
                'trends': trends,
                'audit_distribution': {
                    'by_status': dict(status_counts),
                    'by_score_range': self._categorize_by_score_range(all_scores)
                }
            }
            
            self.logger.info(f"Consolidação de múltiplas auditorias concluída")
            return consolidated_data
            
        except Exception as e:
            self.logger.error(f"Erro na consolidação de múltiplas auditorias: {str(e)}")
            raise

    def _analyze_issue_severity(self, all_issues: List[Dict], issue_type: str) -> Dict[str, int]:
        """Analisa a distribuição de severidade para um tipo de problema específico."""
        severity_counts = defaultdict(int)
        for issue in all_issues:
            if issue['type'] == issue_type:
                severity_counts[issue['severity']] += 1
        return dict(severity_counts)

    def _categorize_by_score_range(self, scores: List[float]) -> Dict[str, int]:
        """Categoriza auditorias por faixas de score."""
        if not scores:
            return {}
        
        ranges = {
            'excellent': 0,  # 90-100
            'good': 0,       # 70-89
            'needs_improvement': 0,  # 50-69
            'poor': 0        # 0-49
        }
        
        for score in scores:
            if score >= 90:
                ranges['excellent'] += 1
            elif score >= 70:
                ranges['good'] += 1
            elif score >= 50:
                ranges['needs_improvement'] += 1
            else:
                ranges['poor'] += 1
        
        return ranges

    def _analyze_temporal_trends(self, audits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisa tendências temporais nas auditorias."""
        try:
            # Filtrar auditorias com timestamp válido
            audits_with_time = []
            for audit in audits:
                timestamp = audit.get('timestamp')
                if timestamp:
                    try:
                        # Tentar diferentes formatos de data
                        if isinstance(timestamp, str):
                            # Formato ISO
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        else:
                            dt = timestamp
                        audits_with_time.append({
                            'date': dt.date(),
                            'score': audit.get('overall_score', 0),
                            'audit': audit
                        })
                    except:
                        continue
            
            if len(audits_with_time) < 2:
                return []
            
            # Ordenar por data
            audits_with_time.sort(key=lambda x: x['date'])
            
            # Calcular tendências
            trends = []
            
            # Tendência de score ao longo do tempo
            dates = [audit['date'] for audit in audits_with_time]
            scores = [audit['score'] for audit in audits_with_time]
            
            if len(scores) > 1:
                # Calcular tendência linear simples
                first_half_avg = statistics.mean(scores[:len(scores)//2])
                second_half_avg = statistics.mean(scores[len(scores)//2:])
                
                trend_direction = 'improving' if second_half_avg > first_half_avg else 'declining'
                trend_magnitude = abs(second_half_avg - first_half_avg)
                
                trends.append({
                    'metric': 'overall_score',
                    'direction': trend_direction,
                    'magnitude': round(trend_magnitude, 2),
                    'confidence': 'medium' if len(scores) > 5 else 'low'
                })
            
            return trends
            
        except Exception as e:
            self.logger.warning(f"Erro ao analisar tendências temporais: {str(e)}")
            return []

    def consolidate_data_sources(self, url: str, api_data: Dict, 
                               crawler_data: Dict, chrome_data: Dict) -> Dict[str, Any]:
        """
        Consolida dados de múltiplas fontes para uma URL específica.
        
        Args:
            url: URL sendo auditada
            api_data: Dados das APIs (GA4, GSC, PSI)
            crawler_data: Dados do Screaming Frog
            chrome_data: Dados do Chrome DevTools
            
        Returns:
            Dicionário com dados consolidados
        """
        try:
            self.logger.info(f"Consolidando dados para {url}")
            
            # Estrutura os dados brutos
            raw_data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'ga4_data': api_data.get('ga4', {}),
                'gsc_data': api_data.get('gsc', {}),
                'psi_data': api_data.get('psi', {}),
                'screaming_frog_data': crawler_data,
                'chrome_devtools_data': chrome_data
            }
            
            # Cria validações fictícias para compatibilidade
            validations = []
            
            # Analisa disponibilidade das fontes
            data_source_status = self._analyze_data_sources(raw_data)
            
            # Calcula métricas consolidadas
            consolidated_metrics = self._calculate_consolidated_metrics(
                validations, data_source_status
            )
            
            # Gera insights consolidados
            consolidated_insights = self._generate_consolidated_insights(
                raw_data, validations, consolidated_metrics
            )
            
            return {
                'success': True,
                'url': url,
                'metrics': asdict(consolidated_metrics),
                'insights': [asdict(insight) for insight in consolidated_insights],
                'data_sources': asdict(data_source_status),
                'raw_data': raw_data
            }
            
        except Exception as e:
            self.logger.error(f"Erro na consolidação de dados: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def _analyze_data_sources(self, raw_data: Dict[str, Any]) -> DataSourceStatus:
        """
        Analisa disponibilidade e qualidade das fontes de dados.
        
        Args:
            raw_data: Dados brutos de todas as fontes.
        
        Returns:
            Status das fontes de dados.
        """
        # Verifica disponibilidade de cada fonte
        ga4_available = bool(raw_data.get('ga4_data') and 
                           raw_data['ga4_data'].get('success', False))
        
        gsc_available = bool(raw_data.get('gsc_data') and 
                           raw_data['gsc_data'].get('success', False))
        
        psi_available = bool(raw_data.get('psi_data') and 
                           raw_data['psi_data'].get('success', False))
        
        screaming_frog_available = bool(raw_data.get('screaming_frog_data') and 
                                      raw_data['screaming_frog_data'].get('success', False))
        
        chrome_devtools_available = bool(raw_data.get('chrome_devtools_data') and 
                                       raw_data['chrome_devtools_data'].get('success', False))
        
        # Conta fontes disponíveis
        available_sources = sum([
            ga4_available, gsc_available, psi_available,
            screaming_frog_available, chrome_devtools_available
        ])
        
        total_sources = 5
        completeness_percentage = (available_sources / total_sources) * 100
        
        return DataSourceStatus(
            ga4_available=ga4_available,
            gsc_available=gsc_available,
            psi_available=psi_available,
            screaming_frog_available=screaming_frog_available,
            chrome_devtools_available=chrome_devtools_available,
            data_sources_count=available_sources,
            completeness_percentage=completeness_percentage
        )
    
    def _calculate_consolidated_metrics(self, validations: List[ValidationResult], 
                                      data_source_status: DataSourceStatus) -> ConsolidatedMetrics:
        """
        Calcula métricas consolidadas baseadas nas validações.
        
        Args:
            validations: Lista de validações executadas.
            data_source_status: Status das fontes de dados.
        
        Returns:
            Métricas consolidadas.
        """
        # Agrupa validações por categoria
        category_scores = defaultdict(list)
        
        for validation in validations:
            category = self.VALIDATION_CATEGORIES.get(
                validation.validation_type, 'technical'
            )
            category_scores[category].append(validation.score)
        
        # Calcula scores médios por categoria
        performance_score = statistics.mean(category_scores['performance']) if category_scores['performance'] else 0
        seo_health_score = statistics.mean(category_scores['seo_health']) if category_scores['seo_health'] else 0
        technical_score = statistics.mean(category_scores['technical']) if category_scores['technical'] else 0
        content_quality_score = statistics.mean(category_scores['content_quality']) if category_scores['content_quality'] else 0
        analytics_health_score = statistics.mean(category_scores['analytics_health']) if category_scores['analytics_health'] else 0
        
        # Calcula score geral ponderado
        overall_score = (
            performance_score * self.SCORE_WEIGHTS['performance'] +
            seo_health_score * self.SCORE_WEIGHTS['seo_health'] +
            technical_score * self.SCORE_WEIGHTS['technical'] +
            content_quality_score * self.SCORE_WEIGHTS['content_quality'] +
            analytics_health_score * self.SCORE_WEIGHTS['analytics_health']
        )
        
        # Conta problemas por severidade
        critical_issues = sum(1 for v in validations if v.status == 'failed')
        warning_issues = sum(1 for v in validations if v.status == 'warning')
        
        # Calcula nível de confiança baseado na completude dos dados
        confidence_level = min(100, data_source_status.completeness_percentage + 20)
        
        return ConsolidatedMetrics(
            performance_score=performance_score,
            seo_health_score=seo_health_score,
            technical_score=technical_score,
            content_quality_score=content_quality_score,
            analytics_health_score=analytics_health_score,
            overall_score=overall_score,
            critical_issues_count=critical_issues,
            warning_issues_count=warning_issues,
            data_completeness=data_source_status.completeness_percentage,
            confidence_level=confidence_level
        )
    
    def _generate_consolidated_insights(self, raw_data: Dict[str, Any], 
                                      validations: List[ValidationResult],
                                      metrics: ConsolidatedMetrics) -> List[ConsolidatedInsight]:
        """
        Gera insights consolidados baseados em múltiplas fontes.
        
        Args:
            raw_data: Dados brutos de todas as fontes.
            validations: Lista de validações executadas.
            metrics: Métricas consolidadas.
        
        Returns:
            Lista de insights consolidados.
        """
        insights = []
        
        # Insight de performance geral
        if metrics.performance_score < 70:
            insights.append(self._create_performance_insight(raw_data, validations, metrics))
        
        # Insight de problemas técnicos críticos
        if metrics.critical_issues_count > 0:
            insights.append(self._create_critical_issues_insight(validations, metrics))
        
        # Insight de saúde do SEO
        if metrics.seo_health_score < 80:
            insights.append(self._create_seo_health_insight(raw_data, validations, metrics))
        
        # Insight de qualidade do conteúdo
        if metrics.content_quality_score < 75:
            insights.append(self._create_content_quality_insight(validations, metrics))
        
        # Insight de completude dos dados
        if metrics.data_completeness < 80:
            insights.append(self._create_data_completeness_insight(raw_data, metrics))
        
        # Insights específicos baseados em correlações
        correlation_insights = self._generate_correlation_insights(raw_data, validations)
        insights.extend(correlation_insights)
        
        return insights
    
    def _create_performance_insight(self, raw_data: Dict[str, Any], 
                                  validations: List[ValidationResult],
                                  metrics: ConsolidatedMetrics) -> ConsolidatedInsight:
        """Cria insight de performance."""
        performance_validations = [
            v for v in validations 
            if self.VALIDATION_CATEGORIES.get(v.validation_type) == 'performance'
        ]
        
        # Identifica principais problemas de performance
        main_issues = []
        for validation in performance_validations:
            if validation.status in ['failed', 'warning']:
                main_issues.append(validation.message)
        
        # Recomendações específicas
        recommendations = []
        if any('mobile' in v.validation_type for v in performance_validations if v.status == 'failed'):
            recommendations.append("Otimizar performance mobile com foco em Core Web Vitals")
        
        if any('desktop' in v.validation_type for v in performance_validations if v.status == 'failed'):
            recommendations.append("Melhorar velocidade de carregamento desktop")
        
        recommendations.extend([
            "Implementar lazy loading para imagens",
            "Minificar CSS e JavaScript",
            "Otimizar imagens (WebP, compressão)",
            "Configurar cache do navegador"
        ])
        
        return ConsolidatedInsight(
            insight_type='performance',
            title='Performance Abaixo do Esperado',
            description=f'O score de performance ({metrics.performance_score:.1f}/100) está abaixo do recomendado. '
                       f'Foram identificados {len(main_issues)} problemas que impactam a velocidade do site.',
            severity='critical' if metrics.performance_score < 50 else 'warning',
            confidence=85.0,
            supporting_data={
                'performance_score': metrics.performance_score,
                'main_issues': main_issues[:3],
                'failed_validations': len([v for v in performance_validations if v.status == 'failed'])
            },
            recommendations=recommendations[:5],
            affected_pages=[],
            data_sources=['PageSpeed Insights', 'Chrome DevTools']
        )
    
    def _create_critical_issues_insight(self, validations: List[ValidationResult],
                                      metrics: ConsolidatedMetrics) -> ConsolidatedInsight:
        """Cria insight de problemas críticos."""
        critical_validations = [v for v in validations if v.status == 'failed']
        
        # Agrupa por categoria
        issues_by_category = defaultdict(list)
        for validation in critical_validations:
            category = self.VALIDATION_CATEGORIES.get(validation.validation_type, 'technical')
            issues_by_category[category].append(validation.message)
        
        # Identifica categoria mais problemática
        most_problematic_category = max(issues_by_category.keys(), 
                                      key=lambda k: len(issues_by_category[k]))
        
        recommendations = []
        for validation in critical_validations[:5]:  # Top 5 problemas
            recommendations.extend(validation.recommendations[:2])
        
        # Remove duplicatas
        recommendations = list(set(recommendations))
        
        return ConsolidatedInsight(
            insight_type='critical_issues',
            title='Problemas Críticos Identificados',
            description=f'Foram encontrados {metrics.critical_issues_count} problemas críticos que requerem '
                       f'atenção imediata. A categoria mais afetada é "{most_problematic_category}" '
                       f'com {len(issues_by_category[most_problematic_category])} problemas.',
            severity='critical',
            confidence=95.0,
            supporting_data={
                'critical_count': metrics.critical_issues_count,
                'most_problematic_category': most_problematic_category,
                'issues_by_category': dict(issues_by_category)
            },
            recommendations=recommendations[:8],
            affected_pages=[],
            data_sources=['Screaming Frog', 'Chrome DevTools', 'PageSpeed Insights']
        )
    
    def _create_seo_health_insight(self, raw_data: Dict[str, Any],
                                 validations: List[ValidationResult],
                                 metrics: ConsolidatedMetrics) -> ConsolidatedInsight:
        """Cria insight de saúde SEO."""
        seo_validations = [
            v for v in validations 
            if self.VALIDATION_CATEGORIES.get(v.validation_type) == 'seo_health'
        ]
        
        # Identifica problemas específicos de SEO
        seo_issues = []
        for validation in seo_validations:
            if validation.status in ['failed', 'warning']:
                seo_issues.append(validation.message)
        
        # Recomendações baseadas nos problemas encontrados
        recommendations = [
            "Revisar e otimizar títulos das páginas",
            "Melhorar meta descriptions para aumentar CTR",
            "Implementar dados estruturados (Schema.org)",
            "Otimizar estrutura de links internos",
            "Verificar e corrigir tags canônicas"
        ]
        
        return ConsolidatedInsight(
            insight_type='seo_health',
            title='Oportunidades de Melhoria em SEO',
            description=f'O score de saúde SEO ({metrics.seo_health_score:.1f}/100) indica oportunidades '
                       f'de otimização. Foram identificados {len(seo_issues)} aspectos que podem '
                       f'melhorar a visibilidade nos mecanismos de busca.',
            severity='warning',
            confidence=80.0,
            supporting_data={
                'seo_health_score': metrics.seo_health_score,
                'seo_issues': seo_issues[:5],
                'gsc_data_available': bool(raw_data.get('gsc_data', {}).get('success'))
            },
            recommendations=recommendations,
            affected_pages=[],
            data_sources=['Google Search Console', 'Screaming Frog']
        )
    
    def _create_content_quality_insight(self, validations: List[ValidationResult],
                                      metrics: ConsolidatedMetrics) -> ConsolidatedInsight:
        """Cria insight de qualidade do conteúdo."""
        content_validations = [
            v for v in validations 
            if self.VALIDATION_CATEGORIES.get(v.validation_type) == 'content_quality'
        ]
        
        content_issues = []
        for validation in content_validations:
            if validation.status in ['failed', 'warning']:
                content_issues.append(validation.message)
        
        recommendations = [
            "Otimizar estrutura de cabeçalhos (H1, H2, H3)",
            "Adicionar texto alternativo em todas as imagens",
            "Melhorar densidade e distribuição de palavras-chave",
            "Aumentar qualidade e relevância do conteúdo",
            "Implementar estratégia de conteúdo estruturado"
        ]
        
        return ConsolidatedInsight(
            insight_type='content_quality',
            title='Qualidade do Conteúdo Pode Ser Melhorada',
            description=f'O score de qualidade do conteúdo ({metrics.content_quality_score:.1f}/100) '
                       f'sugere oportunidades de melhoria na estrutura e otimização do conteúdo.',
            severity='warning',
            confidence=75.0,
            supporting_data={
                'content_quality_score': metrics.content_quality_score,
                'content_issues': content_issues
            },
            recommendations=recommendations,
            affected_pages=[],
            data_sources=['Screaming Frog', 'Chrome DevTools']
        )
    
    def _create_data_completeness_insight(self, raw_data: Dict[str, Any],
                                        metrics: ConsolidatedMetrics) -> ConsolidatedInsight:
        """Cria insight de completude dos dados."""
        missing_sources = []
        
        if not raw_data.get('ga4_data', {}).get('success'):
            missing_sources.append('Google Analytics 4')
        
        if not raw_data.get('gsc_data', {}).get('success'):
            missing_sources.append('Google Search Console')
        
        if not raw_data.get('psi_data', {}).get('success'):
            missing_sources.append('PageSpeed Insights')
        
        if not raw_data.get('screaming_frog_data', {}).get('success'):
            missing_sources.append('Screaming Frog')
        
        if not raw_data.get('chrome_devtools_data', {}).get('success'):
            missing_sources.append('Chrome DevTools')
        
        recommendations = [
            "Configurar integração com Google Analytics 4",
            "Verificar acesso ao Google Search Console",
            "Validar configuração do PageSpeed Insights API",
            "Instalar e configurar Screaming Frog CLI",
            "Verificar configuração do Chrome DevTools MCP"
        ]
        
        # Filtra recomendações baseadas nas fontes em falta
        filtered_recommendations = []
        if 'Google Analytics 4' in missing_sources:
            filtered_recommendations.append(recommendations[0])
        if 'Google Search Console' in missing_sources:
            filtered_recommendations.append(recommendations[1])
        if 'PageSpeed Insights' in missing_sources:
            filtered_recommendations.append(recommendations[2])
        if 'Screaming Frog' in missing_sources:
            filtered_recommendations.append(recommendations[3])
        if 'Chrome DevTools' in missing_sources:
            filtered_recommendations.append(recommendations[4])
        
        return ConsolidatedInsight(
            insight_type='data_completeness',
            title='Fontes de Dados Incompletas',
            description=f'A completude dos dados está em {metrics.data_completeness:.1f}%. '
                       f'Algumas fontes não estão disponíveis: {", ".join(missing_sources)}. '
                       f'Isso pode afetar a precisão da auditoria.',
            severity='warning',
            confidence=90.0,
            supporting_data={
                'data_completeness': metrics.data_completeness,
                'missing_sources': missing_sources,
                'available_sources_count': 5 - len(missing_sources)
            },
            recommendations=filtered_recommendations,
            affected_pages=[],
            data_sources=['System Check']
        )
    
    def _generate_correlation_insights(self, raw_data: Dict[str, Any],
                                     validations: List[ValidationResult]) -> List[ConsolidatedInsight]:
        """
        Gera insights baseados em correlações entre diferentes fontes.
        
        Args:
            raw_data: Dados brutos de todas as fontes.
            validations: Lista de validações executadas.
        
        Returns:
            Lista de insights de correlação.
        """
        insights = []
        
        # Correlação entre performance e SEO
        performance_validations = [
            v for v in validations 
            if self.VALIDATION_CATEGORIES.get(v.validation_type) == 'performance'
        ]
        
        seo_validations = [
            v for v in validations 
            if self.VALIDATION_CATEGORIES.get(v.validation_type) == 'seo_health'
        ]
        
        if performance_validations and seo_validations:
            avg_performance = statistics.mean([v.score for v in performance_validations])
            avg_seo = statistics.mean([v.score for v in seo_validations])
            
            # Se ambos estão baixos, há correlação
            if avg_performance < 70 and avg_seo < 70:
                insights.append(ConsolidatedInsight(
                    insight_type='correlation',
                    title='Correlação entre Performance e SEO',
                    description='Baixa performance está impactando negativamente o SEO. '
                               'Melhorias na velocidade do site podem beneficiar ambos os aspectos.',
                    severity='warning',
                    confidence=70.0,
                    supporting_data={
                        'performance_score': avg_performance,
                        'seo_score': avg_seo
                    },
                    recommendations=[
                        'Priorizar otimizações que beneficiem performance e SEO',
                        'Implementar Core Web Vitals como prioridade',
                        'Otimizar imagens para melhorar velocidade e experiência'
                    ],
                    affected_pages=[],
                    data_sources=['PageSpeed Insights', 'Google Search Console']
                ))
        
        return insights


class ReportGenerator:
    """
    Gerador de relatórios consolidados.
    
    Cria relatórios estruturados baseados nos dados consolidados
    e insights gerados pelo DataConsolidator.
    """
    
    def __init__(self):
        """Inicializa o gerador de relatórios."""
        self.logger = logging.getLogger(__name__)
    
    def generate_consolidated_report(self, audits: List[Dict[str, Any]], 
                                   consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera relatório consolidado para múltiplas auditorias.
        
        Args:
            audits: Lista de auditorias.
            consolidated_data: Dados consolidados das auditorias.
            
        Returns:
            Relatório consolidado formatado.
        """
        try:
            self.logger.info(f"Gerando relatório consolidado para {len(audits)} auditorias")
            
            # Extrair métricas dos dados consolidados
            metrics_summary = consolidated_data.get('metrics_summary', {})
            common_issues = consolidated_data.get('common_issues', [])
            trends = consolidated_data.get('trends', [])
            
            # Gerar insights consolidados
            insights = self._generate_multi_audit_insights(audits, consolidated_data)
            
            # Criar sumário do relatório
            report_summary = {
                'total_audits_analyzed': len(audits),
                'average_score': round(metrics_summary.get('average_score', 0), 2),
                'score_range': {
                    'min': round(metrics_summary.get('min_score', 0), 2),
                    'max': round(metrics_summary.get('max_score', 0), 2),
                    'median': round(metrics_summary.get('median_score', 0), 2)
                },
                'total_issues_found': metrics_summary.get('total_issues', 0),
                'most_common_issues': common_issues[:5],
                'audit_success_rate': self._calculate_success_rate(audits),
                'data_completeness': self._calculate_data_completeness(audits)
            }
            
            # Análise de tendências
            trend_analysis = {
                'score_trends': trends,
                'improvement_opportunities': self._identify_improvement_opportunities(common_issues),
                'performance_patterns': self._analyze_performance_patterns(audits)
            }
            
            # Recomendações consolidadas
            recommendations = self._generate_consolidated_recommendations(common_issues, metrics_summary)
            
            consolidated_report = {
                'report_type': 'consolidated_multi_audit',
                'generated_at': datetime.now().isoformat(),
                'summary': report_summary,
                'metrics': metrics_summary,
                'insights': insights,
                'trends': trend_analysis,
                'recommendations': recommendations,
                'audit_distribution': consolidated_data.get('audit_distribution', {}),
                'data_sources_used': self._identify_data_sources_from_audits(audits)
            }
            
            self.logger.info("Relatório consolidado gerado com sucesso")
            return consolidated_report
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório consolidado: {str(e)}")
            raise

    def _generate_multi_audit_insights(self, audits: List[Dict[str, Any]], 
                                     consolidated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera insights específicos para análise de múltiplas auditorias."""
        insights = []
        
        metrics_summary = consolidated_data.get('metrics_summary', {})
        common_issues = consolidated_data.get('common_issues', [])
        
        # Insight sobre consistência de performance
        if metrics_summary.get('score_std_dev', 0) > 20:
            insights.append({
                'type': 'performance_consistency',
                'title': 'Inconsistência na Performance',
                'description': f'Há uma grande variação nos scores das auditorias (desvio padrão: {metrics_summary.get("score_std_dev", 0):.1f}), '
                              'indicando inconsistência na qualidade entre diferentes URLs ou períodos.',
                'severity': 'warning',
                'recommendations': [
                    'Identificar URLs com performance baixa para otimização prioritária',
                    'Implementar monitoramento contínuo de qualidade',
                    'Padronizar práticas de SEO técnico em todo o site'
                ]
            })
        
        # Insight sobre problemas recorrentes
        if common_issues:
            most_common = common_issues[0]
            if most_common['percentage'] > 50:
                insights.append({
                    'type': 'recurring_issues',
                    'title': 'Problema Sistemático Identificado',
                    'description': f'O problema "{most_common["issue_type"]}" aparece em {most_common["percentage"]:.1f}% '
                                  f'das auditorias ({most_common["count"]} ocorrências), indicando um problema sistemático.',
                    'severity': 'critical' if most_common['percentage'] > 80 else 'warning',
                    'recommendations': [
                        'Priorizar correção deste problema em todo o site',
                        'Implementar verificações automáticas para prevenir recorrência',
                        'Revisar processos de desenvolvimento para evitar este tipo de problema'
                    ]
                })
        
        # Insight sobre oportunidades de melhoria
        avg_score = metrics_summary.get('average_score', 0)
        if avg_score < 70:
            insights.append({
                'type': 'improvement_opportunity',
                'title': 'Grande Oportunidade de Melhoria',
                'description': f'O score médio das auditorias ({avg_score:.1f}) está abaixo do recomendado (70+), '
                              'indicando potencial significativo de melhoria.',
                'severity': 'warning',
                'recommendations': [
                    'Focar nos problemas mais comuns identificados',
                    'Implementar plano de otimização técnica',
                    'Estabelecer metas de melhoria progressiva'
                ]
            })
        
        return insights

    def _calculate_success_rate(self, audits: List[Dict[str, Any]]) -> float:
        """Calcula taxa de sucesso das auditorias."""
        if not audits:
            return 0.0
        
        successful = len([a for a in audits if a.get('status') == 'completed'])
        return round((successful / len(audits)) * 100, 2)

    def _calculate_data_completeness(self, audits: List[Dict[str, Any]]) -> float:
        """Calcula completude média dos dados das auditorias."""
        if not audits:
            return 0.0
        
        completeness_scores = []
        for audit in audits:
            # Verificar presença de diferentes tipos de dados
            data_points = 0
            total_points = 5  # api_data, crawler_data, chrome_data, validation_results, audit_report
            
            if audit.get('api_data'):
                data_points += 1
            if audit.get('crawler_data'):
                data_points += 1
            if audit.get('chrome_data'):
                data_points += 1
            if audit.get('validation_results'):
                data_points += 1
            if audit.get('audit_report'):
                data_points += 1
            
            completeness_scores.append((data_points / total_points) * 100)
        
        return round(statistics.mean(completeness_scores), 2)

    def _identify_improvement_opportunities(self, common_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica oportunidades de melhoria baseadas nos problemas comuns."""
        opportunities = []
        
        for issue in common_issues[:3]:  # Top 3 problemas
            impact_level = 'high' if issue['percentage'] > 70 else 'medium' if issue['percentage'] > 40 else 'low'
            
            opportunities.append({
                'issue_type': issue['issue_type'],
                'impact_level': impact_level,
                'affected_percentage': issue['percentage'],
                'estimated_improvement': self._estimate_score_improvement(issue['issue_type']),
                'priority': 'high' if impact_level == 'high' else 'medium'
            })
        
        return opportunities

    def _estimate_score_improvement(self, issue_type: str) -> float:
        """Estima melhoria de score ao corrigir um tipo de problema."""
        # Estimativas baseadas no impacto típico de cada tipo de problema
        impact_estimates = {
            'performance_mobile': 15.0,
            'performance_desktop': 12.0,
            'core_web_vitals': 18.0,
            'page_titles': 8.0,
            'meta_descriptions': 5.0,
            'ssl_certificate': 10.0,
            'robots_txt': 6.0,
            'sitemap_xml': 7.0,
            'structured_data': 9.0,
            'image_alt_tags': 4.0,
            'h1_tags': 6.0,
            'canonical_tags': 8.0
        }
        
        return impact_estimates.get(issue_type, 5.0)  # Default 5 pontos

    def _analyze_performance_patterns(self, audits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa padrões de performance nas auditorias."""
        patterns = {
            'score_distribution': {},
            'common_failure_points': [],
            'best_performing_aspects': []
        }
        
        # Analisar distribuição de scores
        scores = [audit.get('overall_score', 0) for audit in audits if audit.get('overall_score')]
        if scores:
            patterns['score_distribution'] = {
                'mean': round(statistics.mean(scores), 2),
                'median': round(statistics.median(scores), 2),
                'std_dev': round(statistics.stdev(scores) if len(scores) > 1 else 0, 2),
                'range': {
                    'min': min(scores),
                    'max': max(scores)
                }
            }
        
        return patterns

    def _generate_consolidated_recommendations(self, common_issues: List[Dict[str, Any]], 
                                            metrics_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera recomendações consolidadas baseadas na análise."""
        recommendations = []
        
        # Recomendações baseadas nos problemas mais comuns
        for issue in common_issues[:3]:
            recommendations.append({
                'category': 'issue_resolution',
                'priority': 'high' if issue['percentage'] > 70 else 'medium',
                'title': f'Corrigir {issue["issue_type"]}',
                'description': f'Este problema afeta {issue["percentage"]:.1f}% das auditorias',
                'estimated_impact': f'+{self._estimate_score_improvement(issue["issue_type"]):.1f} pontos no score',
                'effort_level': 'medium'
            })
        
        # Recomendações baseadas no score médio
        avg_score = metrics_summary.get('average_score', 0)
        if avg_score < 50:
            recommendations.append({
                'category': 'general_improvement',
                'priority': 'critical',
                'title': 'Implementar Plano de Melhoria Urgente',
                'description': 'Score médio muito baixo requer ação imediata',
                'estimated_impact': 'Melhoria significativa esperada',
                'effort_level': 'high'
            })
        elif avg_score < 70:
            recommendations.append({
                'category': 'general_improvement',
                'priority': 'high',
                'title': 'Otimizar Aspectos Técnicos Fundamentais',
                'description': 'Focar em melhorias técnicas básicas',
                'estimated_impact': 'Melhoria moderada esperada',
                'effort_level': 'medium'
            })
        
        return recommendations

    def _identify_data_sources_from_audits(self, audits: List[Dict[str, Any]]) -> List[str]:
        """Identifica fontes de dados utilizadas nas auditorias."""
        data_sources = set()
        
        for audit in audits:
            if audit.get('api_data'):
                data_sources.update(['Google Analytics 4', 'Google Search Console', 'PageSpeed Insights'])
            if audit.get('crawler_data'):
                data_sources.add('Screaming Frog')
            if audit.get('chrome_data'):
                data_sources.add('Chrome DevTools')
        
        return list(data_sources)

    def generate_consolidated_report(self, url: str, 
                                   consolidated_metrics: ConsolidatedMetrics,
                                   consolidated_insights: List[ConsolidatedInsight],
                                   raw_data: Dict[str, Any],
                                   validations: List[ValidationResult]) -> AuditReport:
        """
        Gera relatório consolidado de auditoria.
        
        Args:
            url: URL auditada.
            consolidated_metrics: Métricas consolidadas.
            consolidated_insights: Insights consolidados.
            raw_data: Dados brutos originais.
            validations: Lista de validações executadas.
        
        Returns:
            Relatório de auditoria consolidado.
        """
        try:
            self.logger.info(f"Gerando relatório consolidado para {url}")
            
            # Cria resumo do relatório
            summary = self._create_report_summary(
                consolidated_metrics, consolidated_insights, validations
            )
            
            # Adiciona insights ao resumo
            summary['consolidated_insights'] = [asdict(insight) for insight in consolidated_insights]
            summary['data_sources'] = self._identify_data_sources(raw_data)
            summary['audit_completeness'] = consolidated_metrics.data_completeness
            summary['confidence_level'] = consolidated_metrics.confidence_level
            
            # Cria relatório final
            audit_report = AuditReport(
                url=url,
                overall_score=consolidated_metrics.overall_score,
                validations=validations,
                summary=summary,
                audit_timestamp=datetime.now(),
                raw_data=raw_data
            )
            
            self.logger.info(f"Relatório consolidado gerado com score {consolidated_metrics.overall_score:.1f}")
            
            return audit_report
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório consolidado: {str(e)}")
            raise
    
    def _create_report_summary(self, metrics: ConsolidatedMetrics,
                             insights: List[ConsolidatedInsight],
                             validations: List[ValidationResult]) -> Dict[str, Any]:
        """
        Cria resumo do relatório consolidado.
        
        Args:
            metrics: Métricas consolidadas.
            insights: Insights consolidados.
            validations: Lista de validações.
        
        Returns:
            Dicionário com resumo do relatório.
        """
        # Conta validações por status
        status_counts = defaultdict(int)
        for validation in validations:
            status_counts[validation.status] += 1
        
        # Identifica principais problemas críticos
        critical_issues = [
            v.message for v in validations 
            if v.status == 'failed'
        ]
        
        # Identifica insights críticos
        critical_insights = [
            insight.title for insight in insights 
            if insight.severity == 'critical'
        ]
        
        return {
            'total_validations': len(validations),
            'status_counts': dict(status_counts),
            'performance_score': metrics.performance_score,
            'seo_health_score': metrics.seo_health_score,
            'technical_score': metrics.technical_score,
            'content_quality_score': metrics.content_quality_score,
            'analytics_health_score': metrics.analytics_health_score,
            'critical_issues_count': metrics.critical_issues_count,
            'warning_issues_count': metrics.warning_issues_count,
            'top_critical_issues': critical_issues[:5],
            'critical_insights': critical_insights,
            'total_insights': len(insights),
            'insights_by_severity': {
                'critical': len([i for i in insights if i.severity == 'critical']),
                'warning': len([i for i in insights if i.severity == 'warning']),
                'info': len([i for i in insights if i.severity == 'info'])
            }
        }
    
    def _identify_data_sources(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Identifica fontes de dados utilizadas.
        
        Args:
            raw_data: Dados brutos de todas as fontes.
        
        Returns:
            Lista de fontes de dados disponíveis.
        """
        sources = []
        
        if raw_data.get('ga4_data', {}).get('success'):
            sources.append('Google Analytics 4')
        
        if raw_data.get('gsc_data', {}).get('success'):
            sources.append('Google Search Console')
        
        if raw_data.get('psi_data', {}).get('success'):
            sources.append('PageSpeed Insights')
        
        if raw_data.get('screaming_frog_data', {}).get('success'):
            sources.append('Screaming Frog')
        
        if raw_data.get('chrome_devtools_data', {}).get('success'):
            sources.append('Chrome DevTools')
        
        return sources
    
    def generate_comparison_report(self, audit_reports: List[AuditReport]) -> Dict[str, Any]:
        """
        Gera relatório comparativo entre múltiplas auditorias.
        
        Args:
            audit_reports: Lista de relatórios de auditoria.
        
        Returns:
            Relatório comparativo.
        """
        if not audit_reports:
            raise ValueError("Nenhum relatório fornecido para comparação")
        
        try:
            self.logger.info(f"Gerando relatório comparativo de {len(audit_reports)} auditorias")
            
            # Calcula estatísticas comparativas
            scores = [report.overall_score for report in audit_reports]
            
            comparison_data = {
                'total_audits': len(audit_reports),
                'date_range': {
                    'start': min(report.audit_timestamp for report in audit_reports).isoformat(),
                    'end': max(report.audit_timestamp for report in audit_reports).isoformat()
                },
                'score_statistics': {
                    'average': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0
                },
                'websites': [
                    {
                        'url': report.url,
                        'score': report.overall_score,
                        'audit_date': report.audit_timestamp.isoformat(),
                        'critical_issues': report.summary.get('critical_issues_count', 0)
                    }
                    for report in audit_reports
                ],
                'trends': self._analyze_trends(audit_reports),
                'common_issues': self._identify_common_issues(audit_reports)
            }
            
            self.logger.info("Relatório comparativo gerado com sucesso")
            
            return comparison_data
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório comparativo: {str(e)}")
            raise
    
    def _analyze_trends(self, audit_reports: List[AuditReport]) -> Dict[str, Any]:
        """Analisa tendências nos relatórios."""
        if len(audit_reports) < 2:
            return {'trend_analysis': 'Insuficientes dados para análise de tendência'}
        
        # Ordena por data
        sorted_reports = sorted(audit_reports, key=lambda r: r.audit_timestamp)
        
        # Analisa tendência de scores
        scores = [report.overall_score for report in sorted_reports]
        
        if len(scores) >= 2:
            trend = 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable'
        else:
            trend = 'stable'
        
        return {
            'score_trend': trend,
            'score_change': scores[-1] - scores[0] if len(scores) >= 2 else 0,
            'trend_analysis': f'Score trend is {trend} over time period'
        }
    
    def _identify_common_issues(self, audit_reports: List[AuditReport]) -> List[Dict[str, Any]]:
        """Identifica problemas comuns entre relatórios."""
        issue_frequency = defaultdict(int)
        
        for report in audit_reports:
            critical_issues = report.summary.get('top_critical_issues', [])
            for issue in critical_issues:
                issue_frequency[issue] += 1
        
        # Retorna problemas que aparecem em pelo menos 50% dos relatórios
        threshold = len(audit_reports) * 0.5
        common_issues = [
            {'issue': issue, 'frequency': count, 'percentage': (count / len(audit_reports)) * 100}
            for issue, count in issue_frequency.items()
            if count >= threshold
        ]
        
        return sorted(common_issues, key=lambda x: x['frequency'], reverse=True)