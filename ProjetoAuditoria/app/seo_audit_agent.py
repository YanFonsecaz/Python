#!/usr/bin/env python3
"""
Agente Auditor de SEO Técnico Sênior

Este módulo implementa um agente especializado em performance, Core Web Vitals e análise 
de dados estruturados que opera de forma autônoma e determinística para identificar, 
verificar e detalhar problemas técnicos de SEO.
"""

import os
import logging
import json
import csv
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
from pathlib import Path
import re
import time

# Importar cliente Ollama
from .ollama_client import get_ollama_client
from .prompt_security import security_manager, SAFE_TEMPLATES

logger = logging.getLogger(__name__)


class ProblemCategory(Enum):
    """Categorias de problemas de SEO."""
    CRAWLING = "Rastreio"
    CORE_WEB_VITALS = "Core Web Vitals"
    OTHERS = "Outros"
    OPERATIONAL_ERROR = "Operational Error"


class Severity(Enum):
    """Níveis de severidade dos problemas."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class ChecklistItem:
    """Item do checklist de auditoria."""
    id: str
    category: str
    description: str
    validation_method: str
    expected_result: str
    priority: str


@dataclass
class AuditEvidence:
    """Evidência coletada durante a auditoria."""
    type: str  # screenshot, html_snippet, metric, api_response
    source: str  # playwright, screaming_frog, psi, gsc, ga4
    content: str
    timestamp: str
    metadata: Dict[str, Any]


@dataclass
class AuditProblem:
    """Problema identificado durante a auditoria."""
    url: str
    checklist_item_id: str
    problem_category: str
    problem_summary: str
    severity: str
    page_importance_score: int
    metrics: Dict[str, Any]
    evidence: List[Dict[str, str]]
    remediation_steps: List[str]
    validation_procedure: str
    needs_detailed_documentation: bool


class SEOAuditAgent:
    """
    Agente Auditor de SEO Técnico Sênior.
    
    Especializado em performance, Core Web Vitals e análise de dados estruturados.
    Opera de forma autônoma e determinística para identificar problemas técnicos.
    """
    
    def __init__(self, data_folder: str = "data"):
        """
        Inicializa o agente de auditoria SEO.
        
        Args:
            data_folder: Pasta contendo os arquivos de dados
        """
        self.data_folder = Path(data_folder)
        self.logger = logging.getLogger(__name__)
        
        # Inicializar cliente Ollama
        self.ollama_client = get_ollama_client()
        
        # Verificar disponibilidade de ferramentas
        self.playwright_available = self._check_playwright_availability()
        self.context7_available = self._check_context7_availability()
        
        # Dados carregados
        self.screaming_frog_data = {}
        self.ga4_data = {}
        self.gsc_data = {}
        self.psi_data = {}
        self.checklist_items = []
        
        # Configurações
        self.max_retries = 1
        self.audit_results = []
    
    def _analyze_screaming_frog_problems(self, screaming_frog_data: Dict) -> List[AuditProblem]:
        """Analisa problemas baseados nos dados do Screaming Frog e checklist."""
        problems = []
        
        if 'main_audit' not in screaming_frog_data:
            self.logger.warning("Dados principais de auditoria não encontrados")
            return problems
        
        df = screaming_frog_data['main_audit']
        
        # Mapear problemas do checklist com colunas do Screaming Frog
        problem_mappings = {
            # Problemas de Title
            'Tag Title Vazia': 'Tag Title Vazia',
            'Title Longo > 63': 'Title Longo > 63',
            'Title tags duplicadas': 'Title 1',
            
            # Problemas de Meta Description
            'Meta Description Vazia': 'Meta Description Vazia',
            'Meta Description Longa > 160': 'Meta Description Longa > 160',
            'Meta descriptions duplicadas': 'Meta Description 1',
            
            # Problemas de H1
            'Miss H1': 'Miss H1',
            'H1 tags duplicadas': 'H1-1',
            
            # Problemas de Status Code
            'Páginas com erro 404': 'Status Code',
            'Páginas com erro 5xx': 'Status Code',
            'Redirecionamentos': 'Status Code',
            
            # Problemas de Indexabilidade
            'Páginas não indexáveis': 'Indexability',
            
            # Problemas de Performance
            'Core Web Vitals': 'PSI Overall Category',
            'Velocidade da página': 'PSI Performance Score'
        }
        
        # Analisar cada tipo de problema
        for problem_type, column_name in problem_mappings.items():
            if column_name in df.columns:
                problem_urls = self._identify_problem_urls(df, problem_type, column_name)
                
                if problem_urls:
                    for url in problem_urls[:10]:  # Limitar para performance
                        problem = AuditProblem(
                            url=url,
                            checklist_item_id=f"sf_{problem_type.lower().replace(' ', '_')}",
                            problem_category=self._categorize_problem(problem_type),
                            problem_summary=f"{problem_type} detectado",
                            severity=self._determine_severity(problem_type, len(problem_urls)),
                            page_importance_score=self.calculate_page_importance_score(url),
                            metrics={'total_affected': len(problem_urls)},
                            evidence=[{
                                "source": "Screaming Frog",
                                "detail": f"Problema detectado na coluna {column_name}"
                            }],
                            remediation_steps=self._get_recommendations(problem_type),
                            validation_procedure="Verificar via Screaming Frog ou inspeção manual",
                            needs_detailed_documentation=True
                        )
                        problems.append(problem)
        
        return problems
    
    def _identify_problem_urls(self, df: pd.DataFrame, problem_type: str, column_name: str) -> List[str]:
        """Identifica URLs com problemas específicos."""
        problem_urls = []
        
        try:
            if problem_type == 'Tag Title Vazia':
                mask = df[column_name] == 'TRUE'
            elif problem_type == 'Title Longo > 63':
                mask = df[column_name] == 'TRUE'
            elif problem_type == 'Meta Description Vazia':
                mask = df[column_name] == 'TRUE'
            elif problem_type == 'Meta Description Longa > 160':
                mask = df[column_name] == 'TRUE'
            elif problem_type == 'Miss H1':
                mask = df[column_name] == 'TRUE'
            elif problem_type == 'Páginas com erro 404':
                mask = df[column_name] == 404
            elif problem_type == 'Páginas com erro 5xx':
                mask = (df[column_name] >= 500) & (df[column_name] < 600)
            elif problem_type == 'Redirecionamentos':
                mask = (df[column_name] >= 300) & (df[column_name] < 400)
            elif problem_type == 'Páginas não indexáveis':
                mask = df[column_name] != 'Indexable'
            elif problem_type == 'Core Web Vitals':
                mask = df[column_name] == 'FAIL'
            elif problem_type == 'Velocidade da página':
                mask = pd.to_numeric(df[column_name], errors='coerce') < 70
            else:
                # Para problemas de duplicação, usar lógica diferente
                if 'duplicadas' in problem_type.lower():
                    duplicates = df[df[column_name].duplicated(keep=False)]
                    return duplicates['Address'].tolist() if 'Address' in duplicates.columns else []
                else:
                    mask = df[column_name].notna()
            
            if isinstance(mask, pd.Series):
                problem_urls = df[mask]['Address'].tolist() if 'Address' in df.columns else []
            
        except Exception as e:
            self.logger.error(f"Erro ao identificar URLs para {problem_type}: {e}")
        
        return problem_urls
    
    def _determine_severity(self, problem_type: str, affected_count: int) -> str:
        """Determina a severidade do problema baseado no tipo e quantidade."""
        high_severity_problems = ['Páginas com erro 404', 'Páginas com erro 5xx', 'Core Web Vitals']
        medium_severity_problems = ['Tag Title Vazia', 'Meta Description Vazia', 'Miss H1']
        
        if problem_type in high_severity_problems:
            return 'High'
        elif problem_type in medium_severity_problems:
            return 'Medium' if affected_count > 10 else 'Low'
        else:
            return 'Medium' if affected_count > 20 else 'Low'
    
    def _categorize_problem(self, problem_type: str) -> str:
        """Categoriza o problema baseado no tipo."""
        if any(keyword in problem_type.lower() for keyword in ['title', 'meta', 'h1']):
            return 'Outros'
        elif any(keyword in problem_type.lower() for keyword in ['404', '5xx', 'status']):
            return 'Rastreio'
        elif any(keyword in problem_type.lower() for keyword in ['indexa', 'index']):
            return 'Rastreio'
        elif any(keyword in problem_type.lower() for keyword in ['performance', 'velocidade', 'core web vitals']):
            return 'Core Web Vitals'
        else:
            return 'Outros'
    
    def _get_recommendations(self, problem_type: str) -> List[str]:
        """Retorna recomendações específicas para cada tipo de problema."""
        recommendations_map = {
            'Tag Title Vazia': [
                'Adicionar títulos únicos e descritivos para todas as páginas',
                'Incluir palavras-chave relevantes no título',
                'Manter títulos entre 50-60 caracteres'
            ],
            'Title Longo > 63': [
                'Reduzir o comprimento dos títulos para máximo 60 caracteres',
                'Priorizar palavras-chave mais importantes no início',
                'Remover palavras desnecessárias'
            ],
            'Meta Description Vazia': [
                'Criar meta descriptions únicas para cada página',
                'Incluir call-to-action atrativo',
                'Manter entre 150-160 caracteres'
            ],
            'Meta Description Longa > 160': [
                'Reduzir meta descriptions para máximo 160 caracteres',
                'Focar nas informações mais importantes',
                'Incluir palavras-chave relevantes'
            ],
            'Miss H1': [
                'Adicionar tag H1 única em cada página',
                'Garantir que H1 descreva o conteúdo principal',
                'Usar apenas uma tag H1 por página'
            ],
            'Páginas com erro 404': [
                'Corrigir links quebrados',
                'Implementar redirecionamentos 301 quando apropriado',
                'Criar página 404 personalizada e útil'
            ],
            'Páginas com erro 5xx': [
                'Investigar e corrigir erros do servidor',
                'Verificar configurações do servidor',
                'Implementar monitoramento de uptime'
            ],
            'Core Web Vitals': [
                'Otimizar Largest Contentful Paint (LCP)',
                'Melhorar First Input Delay (FID)',
                'Reduzir Cumulative Layout Shift (CLS)',
                'Otimizar imagens e recursos'
            ],
            'Velocidade da página': [
                'Otimizar imagens (compressão, formato WebP)',
                'Minificar CSS e JavaScript',
                'Implementar cache do navegador',
                'Usar CDN para recursos estáticos'
            ]
        }
        
        return recommendations_map.get(problem_type, ['Revisar e otimizar conforme boas práticas de SEO'])
        
    def _check_playwright_availability(self) -> bool:
        """Verifica se o Playwright MCP está disponível."""
        # TODO: Implementar verificação real do Playwright MCP
        return os.getenv('PLAYWRIGHT_MCP_ENABLED', 'false').lower() == 'true'
    
    def _check_context7_availability(self) -> bool:
        """Verifica se o Context7 MCP está disponível."""
        # TODO: Implementar verificação real do Context7 MCP
        return os.getenv('CONTEXT7_MCP_ENABLED', 'false').lower() == 'true'
    
    def load_data_files(self) -> Dict[str, bool]:
        """
        Carrega todos os arquivos de dados disponíveis.
        
        Returns:
            Status de carregamento de cada fonte de dados
        """
        status = {
            'screaming_frog': False,
            'ga4': False,
            'gsc': False,
            'psi': False,
            'checklist': False
        }
        
        try:
            # Carregar dados do Screaming Frog
            sf_folder = self.data_folder / "screaming_frog"
            if sf_folder.exists():
                status['screaming_frog'] = self._load_screaming_frog_data(sf_folder)
            
            # Carregar dados do GA4
            ga4_file = self.data_folder / "ga4_data.json"
            if ga4_file.exists():
                status['ga4'] = self._load_ga4_data(ga4_file)
            
            # Carregar dados do GSC
            gsc_file = self.data_folder / "gsc_data.json"
            if gsc_file.exists():
                status['gsc'] = self._load_gsc_data(gsc_file)
            
            # Carregar dados do PSI
            psi_file = self.data_folder / "psi_data.json"
            if psi_file.exists():
                status['psi'] = self._load_psi_data(psi_file)
            
            # Carregar checklist
            checklist_file = self.data_folder / "checklist.csv"
            if checklist_file.exists():
                status['checklist'] = self._load_checklist(checklist_file)
            
            self.logger.info(f"Status de carregamento dos dados: {status}")
            return status
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivos de dados: {e}")
            return status
    
    def _load_screaming_frog_data(self, folder_path: Union[str, Path]) -> bool:
        """Carrega dados do Screaming Frog."""
        try:
            # Converter para Path se for string
            if isinstance(folder_path, str):
                folder_path = Path(folder_path)
            
            # Procurar por arquivos CSV do Screaming Frog
            csv_files = list(folder_path.glob("*.csv"))
            
            for csv_file in csv_files:
                df = pd.read_csv(csv_file)
                file_type = csv_file.stem.lower()
                
                # Arquivo principal de auditoria do Screaming Frog
                if 'screaming_frog_audit' in file_type or 'internal' in file_type:
                    self.screaming_frog_data['main_audit'] = df
                    self.logger.info(f"Carregado arquivo principal de auditoria: {len(df)} URLs")
                    
                    # Extrair dados específicos do arquivo principal
                    self._extract_screaming_frog_sections(df)
                    
                elif 'response_codes' in file_type:
                    self.screaming_frog_data['response_codes'] = df
                elif 'page_titles' in file_type:
                    self.screaming_frog_data['page_titles'] = df
                elif 'meta_description' in file_type:
                    self.screaming_frog_data['meta_descriptions'] = df
                else:
                    self.screaming_frog_data[file_type] = df
            
            return len(self.screaming_frog_data) > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados do Screaming Frog: {e}")
            return False
    
    def _extract_screaming_frog_sections(self, df: pd.DataFrame) -> None:
        """Extrai seções específicas do arquivo principal do Screaming Frog."""
        try:
            # Extrair dados de títulos
            if 'Title 1' in df.columns:
                title_issues = df[
                    (df['Title 1'].isna()) | 
                    (df['Title 1'] == '') |
                    (df['Title 1 Length'] < 30) |
                    (df['Title 1 Length'] > 63)
                ].copy()
                self.screaming_frog_data['title_issues'] = title_issues
            
            # Extrair dados de meta descriptions
            if 'Meta Description 1' in df.columns:
                meta_desc_issues = df[
                    (df['Meta Description 1'].isna()) | 
                    (df['Meta Description 1'] == '') |
                    (df['Meta Description 1 Length'] < 70) |
                    (df['Meta Description 1 Length'] > 155)
                ].copy()
                self.screaming_frog_data['meta_desc_issues'] = meta_desc_issues
            
            # Extrair dados de H1
            if 'H1-1' in df.columns:
                h1_issues = df[
                    (df['H1-1'].isna()) | 
                    (df['H1-1'] == '')
                ].copy()
                self.screaming_frog_data['h1_issues'] = h1_issues
            
            # Extrair dados de performance (PSI)
            if 'Performance Score' in df.columns:
                performance_issues = df[
                    (df['Performance Score'] < 70) |
                    (df['Performance Score'].isna())
                ].copy()
                self.screaming_frog_data['performance_issues'] = performance_issues
            
            # Extrair dados de Core Web Vitals
            if 'Core Web Vitals Assessment' in df.columns:
                cwv_issues = df[
                    df['Core Web Vitals Assessment'] == 'Fail'
                ].copy()
                self.screaming_frog_data['cwv_issues'] = cwv_issues
            
            # Extrair dados de status codes
            if 'Status Code' in df.columns:
                status_issues = df[
                    ~df['Status Code'].isin([200, 301, 302])
                ].copy()
                self.screaming_frog_data['status_issues'] = status_issues
            
            # Extrair dados de indexabilidade
            if 'Indexability' in df.columns:
                indexability_issues = df[
                    df['Indexability'] != 'Indexable'
                ].copy()
                self.screaming_frog_data['indexability_issues'] = indexability_issues
                
            self.logger.info("Seções extraídas do Screaming Frog com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair seções do Screaming Frog: {e}")
    
    def _load_ga4_data(self, file_path: Path) -> bool:
        """Carrega dados do Google Analytics 4."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.ga4_data = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados do GA4: {e}")
            return False
    
    def _load_gsc_data(self, file_path: Path) -> bool:
        """Carrega dados do Google Search Console."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.gsc_data = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados do GSC: {e}")
            return False
    
    def _load_psi_data(self, file_path: Path) -> bool:
        """Carrega dados do PageSpeed Insights."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.psi_data = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados do PSI: {e}")
            return False
    
    def _load_checklist(self, file_path: Path) -> bool:
        """Carrega checklist de auditoria."""
        try:
            # Primeiro, tentar carregar o checklist de problemas personalizado
            checklist_problemas_path = self.data_folder / "checklist_problemas.csv"
            if checklist_problemas_path.exists():
                with open(checklist_problemas_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Processar checklist de problemas
                checklist_items = []
                current_category = ""
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line or line.startswith('#ERROR!'):
                        continue
                    
                    # Detectar categoria (linhas que não têm vírgulas ou são títulos)
                    if ',' not in line and line and not line.startswith('"'):
                        current_category = line
                        continue
                    
                    # Processar item do checklist
                    if line and current_category:
                        item = ChecklistItem(
                            id=f"item_{i}",
                            category=current_category,
                            description=line.replace('"', ''),
                            validation_method="screaming_frog_analysis",
                            expected_result="compliant",
                            priority="medium"
                        )
                        checklist_items.append(item)
                
                self.checklist_items = checklist_items
                self.logger.info(f"Carregado checklist personalizado: {len(checklist_items)} itens")
                return True
            
            # Fallback para checklist padrão se existir
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        item = ChecklistItem(
                            id=row.get('id', ''),
                            category=row.get('category', ''),
                            description=row.get('description', ''),
                            validation_method=row.get('validation_method', ''),
                            expected_result=row.get('expected_result', ''),
                            priority=row.get('priority', 'Medium')
                        )
                        self.checklist_items.append(item)
                
                return len(self.checklist_items) > 0
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar checklist: {e}")
            return False
    
    def calculate_page_importance_score(self, url: str) -> int:
        """
        Calcula o score de importância da página.
        
        Score = (Erros_GSC_Rastreio * 10) + (Status_Nao_200_Screaming_Frog * 5) + 
                (Casos_LCP_Ruim_GSC * 3) + (Engajamento_GA4 * 2)
        
        Args:
            url: URL da página
            
        Returns:
            Score de importância (0-100)
        """
        score = 0
        
        try:
            # Erros GSC de Rastreio (peso 10)
            if 'crawl_errors' in self.gsc_data:
                crawl_errors = sum(1 for error in self.gsc_data['crawl_errors'] 
                                 if error.get('url') == url)
                score += crawl_errors * 10
            
            # Status não-200 no Screaming Frog (peso 5)
            if 'response_codes' in self.screaming_frog_data:
                df = self.screaming_frog_data['response_codes']
                non_200_count = len(df[(df['Address'] == url) & (df['Status Code'] != 200)])
                score += non_200_count * 5
            
            # Casos LCP ruins no GSC (peso 3)
            if 'core_web_vitals' in self.gsc_data:
                cwv_data = self.gsc_data['core_web_vitals']
                lcp_issues = sum(1 for metric in cwv_data 
                               if metric.get('url') == url and 
                               metric.get('lcp_status') == 'poor')
                score += lcp_issues * 3
            
            # Engajamento GA4 (peso 2)
            if 'engagement' in self.ga4_data:
                engagement_data = self.ga4_data['engagement']
                page_engagement = next((e for e in engagement_data 
                                      if e.get('page') == url), {})
                engagement_score = page_engagement.get('engagement_rate', 0)
                score += int(engagement_score * 2)
            
            # Normalizar para 0-100
            return min(score, 100)
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular score de importância para {url}: {e}")
            return 0
    
    def define_audit_scope(self, priority_urls: Optional[List[str]] = None) -> List[str]:
        """
        Define o escopo de URLs para auditoria.
        
        Args:
            priority_urls: URLs prioritárias fornecidas pelo usuário
            
        Returns:
            Lista de URLs para auditar
        """
        if priority_urls:
            return priority_urls
        
        # Extrair URLs principais dos dados disponíveis
        urls = set()
        
        # URLs do Screaming Frog
        if 'internal_links' in self.screaming_frog_data:
            df = self.screaming_frog_data['internal_links']
            urls.update(df['Address'].unique()[:50])  # Limitar a 50 URLs principais
        
        # URLs do GSC com problemas
        if 'pages' in self.gsc_data:
            gsc_urls = [page['url'] for page in self.gsc_data['pages'][:20]]
            urls.update(gsc_urls)
        
        # URLs do GA4 com maior tráfego
        if 'top_pages' in self.ga4_data:
            ga4_urls = [page['url'] for page in self.ga4_data['top_pages'][:20]]
            urls.update(ga4_urls)
        
        # Calcular score de importância e ordenar
        url_scores = [(url, self.calculate_page_importance_score(url)) for url in urls]
        url_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [url for url, score in url_scores[:30]]  # Top 30 URLs
    
    def classify_checklist_item(self, item: ChecklistItem) -> ProblemCategory:
        """
        Classifica item do checklist em categoria.
        
        Args:
            item: Item do checklist
            
        Returns:
            Categoria do problema
        """
        description_lower = item.description.lower()
        category_lower = item.category.lower()
        
        # Classificação por palavras-chave
        if any(keyword in description_lower or keyword in category_lower 
               for keyword in ['crawl', 'rastreio', 'index', 'robots', 'sitemap', '404', '500']):
            return ProblemCategory.CRAWLING
        
        elif any(keyword in description_lower or keyword in category_lower 
                for keyword in ['lcp', 'fid', 'cls', 'core web vitals', 'performance', 'speed']):
            return ProblemCategory.CORE_WEB_VITALS
        
        else:
            return ProblemCategory.OTHERS
    
    async def validate_checklist_item(self, url: str, item: ChecklistItem) -> Optional[AuditProblem]:
        """
        Valida um item do checklist para uma URL específica.
        
        Args:
            url: URL a ser auditada
            item: Item do checklist
            
        Returns:
            Problema identificado ou None se não houver problema
        """
        try:
            category = self.classify_checklist_item(item)
            
            # Validar baseado na categoria
            if category == ProblemCategory.CRAWLING:
                return await self._validate_crawling_item(url, item)
            elif category == ProblemCategory.CORE_WEB_VITALS:
                return await self._validate_cwv_item(url, item)
            else:
                return await self._validate_other_item(url, item)
                
        except Exception as e:
            self.logger.error(f"Erro ao validar item {item.id} para {url}: {e}")
            
            # Retornar erro operacional
            return AuditProblem(
                url=url,
                checklist_item_id=item.id,
                problem_category=ProblemCategory.OPERATIONAL_ERROR.value,
                problem_summary=f"Erro operacional ao validar item: {str(e)}",
                severity=Severity.MEDIUM.value,
                page_importance_score=self.calculate_page_importance_score(url),
                metrics={},
                evidence=[{
                    "source": "audit_agent",
                    "detail": f"Erro durante validação: {str(e)}"
                }],
                remediation_steps=["Verificar configuração do agente de auditoria"],
                validation_procedure="Executar novamente a auditoria após correção",
                needs_detailed_documentation=False
            )
    
    async def _validate_crawling_item(self, url: str, item: ChecklistItem) -> Optional[AuditProblem]:
        """Valida itens relacionados a rastreio."""
        evidence = []
        metrics = {}
        problems = []
        
        # Verificar status HTTP no Screaming Frog
        if 'response_codes' in self.screaming_frog_data:
            df = self.screaming_frog_data['response_codes']
            url_data = df[df['Address'] == url]
            
            if not url_data.empty:
                status_code = url_data.iloc[0]['Status Code']
                metrics['status_code'] = status_code
                
                if status_code != 200:
                    problems.append(f"Status HTTP {status_code} detectado")
                    evidence.append({
                        "source": "Screaming Frog",
                        "detail": f"URL retorna status {status_code}"
                    })
        
        # Verificar erros de rastreio no GSC
        if 'crawl_errors' in self.gsc_data:
            url_errors = [error for error in self.gsc_data['crawl_errors'] 
                         if error.get('url') == url]
            
            if url_errors:
                for error in url_errors:
                    problems.append(f"Erro GSC: {error.get('error_type', 'Desconhecido')}")
                    evidence.append({
                        "source": "Google Search Console",
                        "detail": f"Erro de rastreio: {error.get('description', 'Sem descrição')}"
                    })
        
        # Se houver problemas, criar objeto AuditProblem
        if problems:
            severity = Severity.CRITICAL if any('404' in p or '500' in p for p in problems) else Severity.HIGH
            
            return AuditProblem(
                url=url,
                checklist_item_id=item.id,
                problem_category=ProblemCategory.CRAWLING.value,
                problem_summary=f"Problemas de rastreio detectados: {'; '.join(problems)}",
                severity=severity.value,
                page_importance_score=self.calculate_page_importance_score(url),
                metrics=metrics,
                evidence=evidence,
                remediation_steps=[
                    "Verificar e corrigir status HTTP da página",
                    "Analisar logs do servidor para identificar causa",
                    "Atualizar sitemap.xml se necessário",
                    "Verificar redirecionamentos"
                ],
                validation_procedure="Verificar status HTTP via curl ou browser, confirmar indexação no GSC",
                needs_detailed_documentation=True
            )
        
        return None
    
    async def _validate_cwv_item(self, url: str, item: ChecklistItem) -> Optional[AuditProblem]:
        """Valida itens relacionados a Core Web Vitals."""
        evidence = []
        metrics = {}
        problems = []
        
        # Verificar dados do PageSpeed Insights
        if url in self.psi_data:
            psi_result = self.psi_data[url]
            
            # Extrair métricas CWV
            if 'lighthouseResult' in psi_result:
                audits = psi_result['lighthouseResult'].get('audits', {})
                
                # LCP
                if 'largest-contentful-paint' in audits:
                    lcp_value = audits['largest-contentful-paint'].get('numericValue', 0) / 1000
                    metrics['lcp'] = f"{lcp_value:.2f}s"
                    
                    if lcp_value > 2.5:
                        problems.append(f"LCP alto: {lcp_value:.2f}s (recomendado: < 2.5s)")
                        evidence.append({
                            "source": "PageSpeed Insights",
                            "detail": f"LCP medido: {lcp_value:.2f}s"
                        })
                
                # FID (via TBT como proxy)
                if 'total-blocking-time' in audits:
                    tbt_value = audits['total-blocking-time'].get('numericValue', 0)
                    metrics['tbt'] = f"{tbt_value}ms"
                    
                    if tbt_value > 300:
                        problems.append(f"TBT alto: {tbt_value}ms (recomendado: < 300ms)")
                        evidence.append({
                            "source": "PageSpeed Insights",
                            "detail": f"Total Blocking Time: {tbt_value}ms"
                        })
                
                # CLS
                if 'cumulative-layout-shift' in audits:
                    cls_value = audits['cumulative-layout-shift'].get('numericValue', 0)
                    metrics['cls'] = cls_value
                    
                    if cls_value > 0.1:
                        problems.append(f"CLS alto: {cls_value} (recomendado: < 0.1)")
                        evidence.append({
                            "source": "PageSpeed Insights",
                            "detail": f"Cumulative Layout Shift: {cls_value}"
                        })
        
        # Verificar dados do GSC
        if 'core_web_vitals' in self.gsc_data:
            cwv_data = [metric for metric in self.gsc_data['core_web_vitals'] 
                       if metric.get('url') == url]
            
            for metric in cwv_data:
                if metric.get('lcp_status') == 'poor':
                    problems.append("LCP classificado como 'poor' no GSC")
                    evidence.append({
                        "source": "Google Search Console",
                        "detail": f"LCP status: {metric.get('lcp_status')}"
                    })
                
                if metric.get('fid_status') == 'poor':
                    problems.append("FID classificado como 'poor' no GSC")
                    evidence.append({
                        "source": "Google Search Console", 
                        "detail": f"FID status: {metric.get('fid_status')}"
                    })
                
                if metric.get('cls_status') == 'poor':
                    problems.append("CLS classificado como 'poor' no GSC")
                    evidence.append({
                        "source": "Google Search Console",
                        "detail": f"CLS status: {metric.get('cls_status')}"
                    })
        
        # Se houver problemas, criar objeto AuditProblem
        if problems:
            return AuditProblem(
                url=url,
                checklist_item_id=item.id,
                problem_category=ProblemCategory.CORE_WEB_VITALS.value,
                problem_summary=f"Problemas de Core Web Vitals: {'; '.join(problems)}",
                severity=Severity.HIGH.value,
                page_importance_score=self.calculate_page_importance_score(url),
                metrics=metrics,
                evidence=evidence,
                remediation_steps=[
                    "Otimizar imagens e recursos críticos",
                    "Implementar lazy loading",
                    "Minimizar JavaScript bloqueante",
                    "Otimizar CSS crítico",
                    "Usar CDN para recursos estáticos"
                ],
                validation_procedure="Executar PageSpeed Insights, verificar métricas no GSC após 28 dias",
                needs_detailed_documentation=True
            )
        
        return None
    
    async def _validate_other_item(self, url: str, item: ChecklistItem) -> Optional[AuditProblem]:
        """Valida outros itens do checklist."""
        evidence = []
        metrics = {}
        problems = []
        
        # Verificar títulos e meta descriptions no Screaming Frog
        if 'page_titles' in self.screaming_frog_data:
            df = self.screaming_frog_data['page_titles']
            url_data = df[df['Address'] == url]
            
            if not url_data.empty:
                title = url_data.iloc[0].get('Title 1', '')
                metrics['title'] = title
                
                if not title:
                    problems.append("Título da página ausente")
                    evidence.append({
                        "source": "Screaming Frog",
                        "detail": "Tag <title> não encontrada"
                    })
                elif len(title) > 60:
                    problems.append(f"Título muito longo: {len(title)} caracteres")
                    evidence.append({
                        "source": "Screaming Frog",
                        "detail": f"Título com {len(title)} caracteres: {title[:100]}..."
                    })
        
        if 'meta_descriptions' in self.screaming_frog_data:
            df = self.screaming_frog_data['meta_descriptions']
            url_data = df[df['Address'] == url]
            
            if not url_data.empty:
                description = url_data.iloc[0].get('Meta Description 1', '')
                metrics['meta_description'] = description
                
                if not description:
                    problems.append("Meta description ausente")
                    evidence.append({
                        "source": "Screaming Frog",
                        "detail": "Meta description não encontrada"
                    })
                elif len(description) > 160:
                    problems.append(f"Meta description muito longa: {len(description)} caracteres")
                    evidence.append({
                        "source": "Screaming Frog",
                        "detail": f"Meta description com {len(description)} caracteres"
                    })
        
        # Se houver problemas, criar objeto AuditProblem
        if problems:
            return AuditProblem(
                url=url,
                checklist_item_id=item.id,
                problem_category=ProblemCategory.OTHERS.value,
                problem_summary=f"Problemas de conteúdo: {'; '.join(problems)}",
                severity=Severity.MEDIUM.value,
                page_importance_score=self.calculate_page_importance_score(url),
                metrics=metrics,
                evidence=evidence,
                remediation_steps=[
                    "Adicionar ou otimizar título da página",
                    "Criar meta description atrativa e informativa",
                    "Verificar comprimento dos elementos",
                    "Incluir palavras-chave relevantes"
                ],
                validation_procedure="Verificar elementos via view-source, validar no GSC",
                needs_detailed_documentation=True
            )
        
        return None
    
    async def run_audit(self, priority_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Executa auditoria completa de SEO.
        
        Args:
            priority_urls: URLs prioritárias para auditoria
            
        Returns:
            Resultado da auditoria com problemas identificados
        """
        start_time = time.time()
        
        try:
            # Fase 1: Configuração e Escopo
            self.logger.info("Iniciando Fase 1: Configuração e Escopo")
            
            # Carregar dados
            data_status = self.load_data_files()
            if not any(data_status.values()):
                return {
                    'success': False,
                    'error': 'Nenhum arquivo de dados foi carregado com sucesso',
                    'data_status': data_status
                }
            
            # Definir escopo
            audit_urls = self.define_audit_scope(priority_urls)
            if not audit_urls:
                return {
                    'success': False,
                    'error': 'Nenhuma URL foi definida para auditoria',
                    'data_status': data_status
                }
            
            self.logger.info(f"Escopo definido: {len(audit_urls)} URLs, {len(self.checklist_items)} itens do checklist")
            
            # Fase 2: Auditoria Iterativa
            self.logger.info("Iniciando Fase 2: Auditoria Iterativa")
            
            problems = []
            total_validations = len(audit_urls) * len(self.checklist_items)
            completed_validations = 0
            
            for url in audit_urls:
                self.logger.info(f"Auditando URL: {url}")
                
                # Verificar se URL é acessível
                if not await self._check_url_accessibility(url):
                    # Gerar problema de acesso
                    problem = AuditProblem(
                        url=url,
                        checklist_item_id="URL_ACCESS",
                        problem_category=ProblemCategory.CRAWLING.value,
                        problem_summary=f"URL inacessível ou retorna erro HTTP",
                        severity=Severity.CRITICAL.value,
                        page_importance_score=self.calculate_page_importance_score(url),
                        metrics={'accessible': False},
                        evidence=[{
                            "source": "audit_agent",
                            "detail": "URL não pôde ser acessada durante a auditoria"
                        }],
                        remediation_steps=[
                            "Verificar se a URL está correta",
                            "Verificar conectividade de rede",
                            "Verificar se o servidor está respondendo"
                        ],
                        validation_procedure="Testar acesso via browser ou curl",
                        needs_detailed_documentation=True
                    )
                    problems.append(problem)
                    continue
                
                # Iterar sobre checklist
                for item in self.checklist_items:
                    try:
                        problem = await self.validate_checklist_item(url, item)
                        if problem:
                            problems.append(problem)
                        
                        completed_validations += 1
                        
                        # Log de progresso
                        if completed_validations % 10 == 0:
                            progress = (completed_validations / total_validations) * 100
                            self.logger.info(f"Progresso: {progress:.1f}% ({completed_validations}/{total_validations})")
                    
                    except Exception as e:
                        self.logger.error(f"Erro ao validar {item.id} para {url}: {e}")
                        continue
            
            # Fase 3: Geração de Saída Estruturada
            self.logger.info("Iniciando Fase 3: Geração de Saída Estruturada")
            
            # Converter para JSON
            problems_json = [asdict(problem) for problem in problems]
            
            # Fase 4: Análise e Priorização com Ollama
            self.logger.info("Iniciando Fase 4: Análise e Priorização com Ollama")
            
            # Analisar problemas com Ollama se disponível
            if self.ollama_client and self.ollama_client.is_available:
                try:
                    # Preparar dados para análise
                    problems_summary = {
                        'total_problems': len(problems_json),
                        'critical_problems': len([p for p in problems_json if p.get('severity') == 'Critical']),
                        'high_problems': len([p for p in problems_json if p.get('severity') == 'High']),
                        'categories': {}
                    }
                    
                    for problem in problems_json:
                        category = problem.get('problem_category', 'Unknown')
                        if category not in problems_summary['categories']:
                            problems_summary['categories'][category] = 0
                        problems_summary['categories'][category] += 1
                    
                    # Validação de segurança dos dados de entrada
                    summary_str = json.dumps(problems_summary, indent=2)
                    problems_str = json.dumps(problems_json[:5], indent=2)
                    
                    security_result_summary = security_manager.detect_threats(summary_str)
                    security_result_problems = security_manager.detect_threats(problems_str)
                    
                    if not security_result_summary.is_safe or not security_result_problems.is_safe:
                        self.logger.warning("Dados suspeitos detectados na análise SEO")
                        summary_str = security_result_summary.sanitized_content
                        problems_str = security_result_problems.sanitized_content
                    
                    # Criar prompt seguro usando template
                    analysis_prompt = security_manager.create_safe_prompt(
                        SAFE_TEMPLATES["seo_analysis"],
                        summary=summary_str,
                        problems=problems_str
                    )
                    
                    ollama_analysis = await self.ollama_client.analyze_seo_content("audit_analysis", analysis_prompt)
                    
                except Exception as e:
                    self.logger.warning(f"Erro na análise com Ollama: {e}")
                    ollama_analysis = 'Análise não disponível'
            else:
                ollama_analysis = 'Ollama não disponível'
            
            # Ordenar problemas
            sorted_problems = self._sort_problems_by_priority(problems_json)
            
            # Estatísticas
            stats = self._generate_audit_statistics(sorted_problems)
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'problems': sorted_problems,
                'statistics': stats,
                'metadata': {
                    'audit_urls': audit_urls,
                    'checklist_items_count': len(self.checklist_items),
                    'total_validations': total_validations,
                    'execution_time_seconds': round(execution_time, 2),
                    'data_sources_loaded': data_status,
                    'generated_at': datetime.now().isoformat(),
                    'ollama_analysis': ollama_analysis
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro durante auditoria: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time_seconds': time.time() - start_time
            }
    
    async def _check_url_accessibility(self, url: str) -> bool:
        """
        Verifica se uma URL é acessível.
        
        Args:
            url: URL para verificar
            
        Returns:
            True se acessível, False caso contrário
        """
        try:
            # TODO: Implementar verificação real via HTTP request ou Playwright
            # Por enquanto, assumir que URLs são acessíveis
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar acessibilidade de {url}: {e}")
            return False
    
    def _sort_problems_by_priority(self, problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ordena problemas por prioridade.
        
        Ordem: Categoria > Severidade > page_importance_score
        """
        category_order = {
            ProblemCategory.CRAWLING.value: 4,
            ProblemCategory.CORE_WEB_VITALS.value: 3,
            ProblemCategory.OTHERS.value: 2,
            ProblemCategory.OPERATIONAL_ERROR.value: 1
        }
        
        severity_order = {
            Severity.CRITICAL.value: 4,
            Severity.HIGH.value: 3,
            Severity.MEDIUM.value: 2,
            Severity.LOW.value: 1
        }
        
        return sorted(problems, key=lambda p: (
            category_order.get(p['problem_category'], 0),
            severity_order.get(p['severity'], 0),
            p['page_importance_score']
        ), reverse=True)
    
    def _generate_audit_statistics(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera estatísticas da auditoria."""
        stats = {
            'total_problems': len(problems),
            'by_category': {},
            'by_severity': {},
            'high_importance_pages': 0,
            'needs_documentation': 0
        }
        
        for problem in problems:
            # Por categoria
            category = problem['problem_category']
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            # Por severidade
            severity = problem['severity']
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            # Páginas de alta importância
            if problem['page_importance_score'] >= 80:
                stats['high_importance_pages'] += 1
            
            # Necessita documentação
            if problem.get('needs_detailed_documentation', False):
                stats['needs_documentation'] += 1
        
        return stats


def create_seo_audit_agent(data_folder: str = "data") -> SEOAuditAgent:
    """Factory function para criar instância do agente de auditoria."""
    return SEOAuditAgent(data_folder)


# Exemplo de uso
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Criar agente
        agent = create_seo_audit_agent()
        
        # URLs de exemplo
        test_urls = [
            "https://renirfonseca.blogspot.com/",
            "https://renirfonseca.blogspot.com/2024/01/exemplo.html"
        ]
        
        # Executar auditoria
        result = await agent.run_audit(test_urls)
        
        if result['success']:
            print("✅ Auditoria concluída com sucesso!")
            print(f"📊 Problemas encontrados: {result['statistics']['total_problems']}")
            print(f"⏱️ Tempo de execução: {result['metadata']['execution_time_seconds']}s")
            
            # Mostrar primeiros problemas
            for i, problem in enumerate(result['problems'][:3], 1):
                print(f"\n{i}. [{problem['severity']}] {problem['problem_summary']}")
                print(f"   URL: {problem['url']}")
                print(f"   Categoria: {problem['problem_category']}")
        else:
            print(f"❌ Erro na auditoria: {result['error']}")
    
    # Executar exemplo
    asyncio.run(main())