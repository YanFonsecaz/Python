#!/usr/bin/env python3
"""
Agente de Documentação SEO - Especialista em Comunicação de SEO Técnico

Este módulo implementa um agente especializado que traduz dados brutos de auditoria 
em documentação clara, profissional e acionável para equipes de desenvolvimento e produto.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

# Importar cliente Ollama
from .ollama_client import get_ollama_client
from .prompt_security import security_manager, SAFE_TEMPLATES

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Níveis de severidade dos problemas SEO."""
    HIGH = "ALTA"
    MEDIUM = "MÉDIA"
    LOW = "BAIXA"


@dataclass
class SEOProblem:
    """
    Estrutura de dados para um problema de SEO identificado.
    
    Representa um problema específico encontrado durante a auditoria,
    com todas as informações necessárias para documentação e correção.
    """
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


@dataclass
class DocumentationSection:
    """Seção de documentação gerada para um problema SEO."""
    title: str
    problem_description: str
    evidence_list: str
    impact_analysis: str
    technical_steps: str
    code_snippets: str
    validation_guide: str
    official_references: str
    expected_benefits: str
    timeline_estimate: str


class SEODocumentationAgent:
    """
    Agente Especialista em Comunicação de SEO Técnico.
    
    Responsável por traduzir dados brutos de auditoria em documentação clara,
    profissional e acionável para equipes de desenvolvimento e produto.
    """
    
    def __init__(self):
        """Inicializa o agente de documentação SEO."""
        self.logger = logging.getLogger(__name__)
        self.context7_available = self._check_context7_availability()
        
        # Inicializar cliente Ollama
        self.ollama_client = get_ollama_client()
        
    def _check_context7_availability(self) -> bool:
        """Verifica se o Context7 MCP está disponível para consultas."""
        # TODO: Implementar verificação real do Context7 MCP
        return os.getenv('CONTEXT7_MCP_ENABLED', 'false').lower() == 'true'
    
    def process_audit_problems(self, problems_json: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa uma lista de problemas de SEO e gera documentação completa.
        
        Args:
            problems_json: Lista de problemas em formato JSON
            
        Returns:
            Documentação estruturada com seções para cada problema
        """
        try:
            # Converter JSON para objetos SEOProblem
            problems = [self._parse_seo_problem(problem_data) for problem_data in problems_json]
            
            # Ordenar por severidade e importância da página
            problems_sorted = self._sort_problems_by_priority(problems)
            
            # Gerar documentação para cada problema
            documentation_sections = []
            for problem in problems_sorted:
                section = self._generate_problem_documentation(problem)
                documentation_sections.append(section)
            
            # Compilar documento final
            final_document = self._compile_final_document(documentation_sections)
            
            return {
                'success': True,
                'document': final_document,
                'sections_count': len(documentation_sections),
                'generated_at': datetime.now().isoformat(),
                'problems_processed': len(problems)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar problemas de auditoria: {e}")
            return {
                'success': False,
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def _parse_seo_problem(self, problem_data: Dict[str, Any]) -> SEOProblem:
        """Converte dados JSON em objeto SEOProblem."""
        return SEOProblem(
            url=problem_data.get('url', ''),
            checklist_item_id=problem_data.get('checklist_item_id', ''),
            problem_category=problem_data.get('problem_category', ''),
            problem_summary=problem_data.get('problem_summary', ''),
            severity=problem_data.get('severity', ''),
            page_importance_score=problem_data.get('page_importance_score', 0),
            metrics=problem_data.get('metrics', {}),
            evidence=problem_data.get('evidence', []),
            remediation_steps=problem_data.get('remediation_steps', []),
            validation_procedure=problem_data.get('validation_procedure', '')
        )
    
    def _sort_problems_by_priority(self, problems: List[SEOProblem]) -> List[SEOProblem]:
        """Ordena problemas por severidade e importância da página."""
        severity_order = {'High': 3, 'Medium': 2, 'Low': 1}
        
        return sorted(problems, key=lambda p: (
            severity_order.get(p.severity, 0),
            p.page_importance_score
        ), reverse=True)
    
    def _generate_problem_documentation(self, problem: SEOProblem) -> DocumentationSection:
        """
        Gera documentação completa para um problema específico.
        
        Segue o formato especializado:
        1. PROBLEMA / OPORTUNIDADE
        2. SOLUÇÃO  
        3. IMPACTO ESPERADO
        """
        
        # Tentar usar Ollama para gerar documentação mais rica
        if self.ollama_client and self.ollama_client.is_available:
            try:
                # Preparar contexto para o Ollama
                problem_context = {
                    'url': problem.url,
                    'category': problem.problem_category,
                    'summary': problem.problem_summary,
                    'severity': problem.severity,
                    'metrics': problem.metrics,
                    'evidence': problem.evidence,
                    'remediation_steps': problem.remediation_steps
                }
                
                # Validação de segurança do contexto
                context_str = json.dumps(problem_context, indent=2)
                security_result = security_manager.detect_threats(context_str)
                
                if not security_result.is_safe:
                    self.logger.warning(f"Contexto suspeito detectado para problema {problem.checklist_item_id}")
                    context_str = security_result.sanitized_content
                
                # Criar prompt seguro usando template
                documentation_prompt = security_manager.create_safe_prompt(
                    SAFE_TEMPLATES["seo_documentation"],
                    context=context_str
                )
                
                ollama_documentation = self.ollama_client.generate_seo_documentation(documentation_prompt)
                
                # Se o Ollama gerou documentação, usar como base
                if ollama_documentation and ollama_documentation.strip():
                    # Ainda gerar os campos individuais para compatibilidade
                    title = self._create_problem_title(problem)
                    problem_description = f"[Gerado com Ollama]\n{ollama_documentation}"
                    evidence_list = self._format_evidence_list(problem)
                    impact_analysis = self._analyze_current_impact(problem)
                    technical_steps = self._format_technical_steps(problem)
                    code_snippets = self._generate_code_snippets(problem)
                    validation_guide = self._format_validation_procedure(problem)
                    official_references = self._get_official_references(problem)
                    expected_benefits = self._describe_expected_benefits(problem)
                    timeline_estimate = self._estimate_results_timeline(problem)
                    
                    return DocumentationSection(
                        title=title,
                        problem_description=problem_description,
                        evidence_list=evidence_list,
                        impact_analysis=impact_analysis,
                        technical_steps=technical_steps,
                        code_snippets=code_snippets,
                        validation_guide=validation_guide,
                        official_references=official_references,
                        expected_benefits=expected_benefits,
                        timeline_estimate=timeline_estimate
                    )
                    
            except Exception as e:
                self.logger.warning(f"Erro ao gerar documentação com Ollama: {e}")
        
        # Fallback para geração tradicional
        # 1. PROBLEMA / OPORTUNIDADE
        title = self._create_problem_title(problem)
        problem_description = self._create_technical_description(problem)
        evidence_list = self._format_evidence_list(problem)
        impact_analysis = self._analyze_current_impact(problem)
        
        # 2. SOLUÇÃO
        technical_steps = self._format_technical_steps(problem)
        code_snippets = self._generate_code_snippets(problem)
        validation_guide = self._format_validation_procedure(problem)
        official_references = self._get_official_references(problem)
        
        # 3. IMPACTO ESPERADO
        expected_benefits = self._describe_expected_benefits(problem)
        timeline_estimate = self._estimate_results_timeline(problem)
        
        return DocumentationSection(
            title=title,
            problem_description=problem_description,
            evidence_list=evidence_list,
            impact_analysis=impact_analysis,
            technical_steps=technical_steps,
            code_snippets=code_snippets,
            validation_guide=validation_guide,
            official_references=official_references,
            expected_benefits=expected_benefits,
            timeline_estimate=timeline_estimate
        )
    
    def _create_problem_title(self, problem: SEOProblem) -> str:
        """Cria título padronizado: [SEVERIDADE] Título do problema – URL"""
        severity_map = {
            'High': 'ALTA',
            'Medium': 'MÉDIA', 
            'Low': 'BAIXA'
        }
        
        severity_text = severity_map.get(problem.severity, problem.severity.upper())
        
        return f"[{severity_text}] {problem.problem_summary} – {problem.url} (Importância: {problem.page_importance_score})"
    
    def _create_technical_description(self, problem: SEOProblem) -> str:
        """Cria descrição técnica detalhada do problema."""
        description = f"**Categoria:** {problem.problem_category}\n"
        description += f"**ID do Checklist:** {problem.checklist_item_id}\n\n"
        description += f"**Descrição do Problema:**\n{problem.problem_summary}\n\n"
        
        # Adicionar métricas se disponíveis
        if problem.metrics:
            description += "**Métricas Identificadas:**\n"
            for key, value in problem.metrics.items():
                if key == 'metric_name':
                    description += f"- **Métrica:** {value}\n"
                elif key == 'measured_value':
                    description += f"- **Valor Medido:** {value}\n"
                elif key == 'recommended_threshold':
                    description += f"- **Limite Recomendado:** {value}\n"
                elif key == 'device':
                    description += f"- **Dispositivo:** {value}\n"
                else:
                    description += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            
            # Explicar por que representa uma falha
            if 'measured_value' in problem.metrics and 'recommended_threshold' in problem.metrics:
                description += f"\n**Por que é um problema:**\n"
                description += f"O valor medido ({problem.metrics['measured_value']}) excede o limite recomendado "
                description += f"({problem.metrics['recommended_threshold']}), impactando negativamente a experiência do usuário "
                description += f"e potencialmente o ranking nos resultados de busca.\n"
        
        return description
    
    def _format_evidence_list(self, problem: SEOProblem) -> str:
        """Formata lista de evidências encontradas."""
        if not problem.evidence:
            return "**Evidências:** Nenhuma evidência específica documentada.\n"
        
        evidence_text = "**Evidências Coletadas:**\n"
        for i, evidence in enumerate(problem.evidence, 1):
            source = evidence.get('source', 'Fonte não especificada')
            detail = evidence.get('detail', 'Detalhes não disponíveis')
            evidence_text += f"{i}. **{source}:** {detail}\n"
        
        return evidence_text
    
    def _analyze_current_impact(self, problem: SEOProblem) -> str:
        """Analisa o impacto atual do problema considerando a importância da página."""
        impact_text = "**Impacto Atual:**\n"
        
        # Impacto baseado na categoria do problema
        category_impacts = {
            'Core Web Vitals': 'Afeta diretamente o ranking nos resultados de busca e a experiência do usuário',
            'Technical SEO': 'Pode impedir o crawling e indexação adequados pelo Google',
            'Content': 'Reduz a relevância e qualidade percebida pelo algoritmo de busca',
            'Mobile': 'Prejudica a experiência em dispositivos móveis, priorizados pelo Google',
            'Performance': 'Impacta negativamente as métricas de velocidade e usabilidade'
        }
        
        base_impact = category_impacts.get(problem.problem_category, 
                                         'Impacta negativamente a otimização para mecanismos de busca')
        impact_text += f"- {base_impact}\n"
        
        # Impacto baseado na importância da página
        if problem.page_importance_score >= 90:
            impact_text += "- **CRÍTICO:** Página de alta importância - impacto significativo no tráfego orgânico\n"
        elif problem.page_importance_score >= 70:
            impact_text += "- **ALTO:** Página importante - impacto considerável na visibilidade\n"
        elif problem.page_importance_score >= 50:
            impact_text += "- **MÉDIO:** Página moderadamente importante - impacto localizado\n"
        else:
            impact_text += "- **BAIXO:** Página de menor importância - impacto limitado\n"
        
        # Impacto baseado na severidade
        if problem.severity == 'High':
            impact_text += "- **Severidade Alta:** Requer correção imediata para evitar penalizações\n"
        elif problem.severity == 'Medium':
            impact_text += "- **Severidade Média:** Deve ser corrigido no próximo ciclo de otimizações\n"
        else:
            impact_text += "- **Severidade Baixa:** Pode ser incluído em melhorias futuras\n"
        
        return impact_text
    
    def _format_technical_steps(self, problem: SEOProblem) -> str:
        """Formata passos técnicos executáveis."""
        if not problem.remediation_steps:
            return "**Passos Técnicos:** Nenhum passo específico documentado.\n"
        
        steps_text = "**Passos Técnicos para Correção:**\n"
        for i, step in enumerate(problem.remediation_steps, 1):
            steps_text += f"{i}. {step}\n"
        
        return steps_text
    
    def _generate_code_snippets(self, problem: SEOProblem) -> str:
        """Gera trechos de código ou configuração quando aplicável."""
        code_snippets = "**Trechos de Código/Configuração:**\n"
        
        # Gerar snippets baseados na categoria e tipo do problema
        if 'LCP' in problem.problem_summary or 'Largest Contentful Paint' in problem.problem_summary:
            code_snippets += """
```html
<!-- Pré-carregamento de imagem crítica -->
<link rel="preload" as="image" href="/path/to/hero-image.jpg">

<!-- Otimização de imagem responsiva -->
<img src="/path/to/hero-image.jpg" 
     srcset="/path/to/hero-image-480w.jpg 480w,
             /path/to/hero-image-800w.jpg 800w,
             /path/to/hero-image-1200w.jpg 1200w"
     sizes="(max-width: 480px) 480px,
            (max-width: 800px) 800px,
            1200px"
     alt="Descrição da imagem"
     loading="eager">
```
"""
        
        elif 'CLS' in problem.problem_summary or 'Cumulative Layout Shift' in problem.problem_summary:
            code_snippets += """
```css
/* Reservar espaço para imagens */
.hero-image {
    width: 100%;
    height: 400px; /* Altura fixa para evitar shifts */
    object-fit: cover;
}

/* Dimensões explícitas para elementos dinâmicos */
.ad-container {
    min-height: 250px;
    width: 300px;
}
```
"""
        
        elif 'FID' in problem.problem_summary or 'First Input Delay' in problem.problem_summary:
            code_snippets += """
```javascript
// Otimização de event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Usar delegação de eventos
    document.body.addEventListener('click', function(e) {
        if (e.target.matches('.button-class')) {
            handleButtonClick(e);
        }
    });
});

// Debounce para inputs frequentes
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
```
"""
        
        elif 'meta' in problem.problem_summary.lower() or 'title' in problem.problem_summary.lower():
            code_snippets += """
```html
<!-- Meta tags otimizadas -->
<title>Título Otimizado - Palavra-chave Principal | Marca</title>
<meta name="description" content="Descrição atrativa e informativa com palavra-chave principal, entre 150-160 caracteres.">
<meta name="robots" content="index, follow">

<!-- Open Graph para redes sociais -->
<meta property="og:title" content="Título Otimizado - Palavra-chave Principal">
<meta property="og:description" content="Descrição para compartilhamento social">
<meta property="og:image" content="/path/to/social-image.jpg">
<meta property="og:url" content="https://exemplo.com/pagina">
```
"""
        
        else:
            code_snippets += "Nenhum trecho de código específico aplicável para este tipo de problema.\n"
        
        return code_snippets
    
    def _format_validation_procedure(self, problem: SEOProblem) -> str:
        """Formata procedimento de validação."""
        validation_text = "**Procedimento de Validação:**\n"
        
        if problem.validation_procedure:
            validation_text += f"{problem.validation_procedure}\n\n"
        
        # Adicionar validações padrão baseadas na categoria
        validation_text += "**Validações Adicionais Recomendadas:**\n"
        
        if 'Core Web Vitals' in problem.problem_category:
            validation_text += "1. Executar Google PageSpeed Insights antes e depois da correção\n"
            validation_text += "2. Verificar métricas no Google Search Console (Core Web Vitals)\n"
            validation_text += "3. Testar em dispositivos móveis reais\n"
            validation_text += "4. Monitorar por 28 dias para dados de campo atualizados\n"
        
        elif 'Technical SEO' in problem.problem_category:
            validation_text += "1. Verificar indexação no Google Search Console\n"
            validation_text += "2. Testar crawling com Screaming Frog SEO Spider\n"
            validation_text += "3. Validar robots.txt e sitemap.xml\n"
            validation_text += "4. Confirmar ausência de erros 404 ou redirecionamentos\n"
        
        else:
            validation_text += "1. Verificar implementação em ambiente de desenvolvimento\n"
            validation_text += "2. Testar funcionalidade em diferentes navegadores\n"
            validation_text += "3. Validar em ambiente de produção\n"
            validation_text += "4. Monitorar métricas por período adequado\n"
        
        return validation_text
    
    def _get_official_references(self, problem: SEOProblem) -> str:
        """Obtém referências oficiais do Google Search Central."""
        references_text = "**Referências Oficiais:**\n"
        
        # Referências baseadas na categoria do problema
        category_references = {
            'Core Web Vitals': [
                "https://developers.google.com/search/docs/appearance/core-web-vitals",
                "https://web.dev/vitals/",
                "https://developers.google.com/speed/pagespeed/insights/"
            ],
            'Technical SEO': [
                "https://developers.google.com/search/docs/crawling-indexing",
                "https://developers.google.com/search/docs/crawling-indexing/robots/intro",
                "https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview"
            ],
            'Mobile': [
                "https://developers.google.com/search/mobile-sites/",
                "https://developers.google.com/search/docs/appearance/mobile-friendly",
                "https://web.dev/responsive-web-design-basics/"
            ],
            'Content': [
                "https://developers.google.com/search/docs/appearance/title-link",
                "https://developers.google.com/search/docs/appearance/snippet",
                "https://developers.google.com/search/docs/appearance/structured-data"
            ]
        }
        
        refs = category_references.get(problem.problem_category, [
            "https://developers.google.com/search/docs/",
            "https://support.google.com/webmasters/"
        ])
        
        for i, ref in enumerate(refs, 1):
            references_text += f"{i}. {ref}\n"
        
        # TODO: Integrar com Context7 MCP para obter referências atualizadas
        if self.context7_available:
            references_text += "\n*Referências atualizadas via Context7 MCP*\n"
        
        return references_text
    
    def _describe_expected_benefits(self, problem: SEOProblem) -> str:
        """Descreve benefícios esperados da correção."""
        benefits_text = "**Benefícios Esperados:**\n"
        
        # Benefícios baseados na categoria
        if 'Core Web Vitals' in problem.problem_category:
            benefits_text += "- Melhoria no ranking dos resultados de busca\n"
            benefits_text += "- Redução da taxa de rejeição\n"
            benefits_text += "- Aumento do tempo de permanência na página\n"
            benefits_text += "- Melhor experiência do usuário\n"
            benefits_text += "- Possível aumento nas conversões\n"
        
        elif 'Technical SEO' in problem.problem_category:
            benefits_text += "- Melhor crawling e indexação pelo Google\n"
            benefits_text += "- Aumento da visibilidade nos resultados de busca\n"
            benefits_text += "- Redução de erros no Google Search Console\n"
            benefits_text += "- Otimização do budget de crawling\n"
        
        elif 'Mobile' in problem.problem_category:
            benefits_text += "- Melhor experiência em dispositivos móveis\n"
            benefits_text += "- Conformidade com Mobile-First Indexing\n"
            benefits_text += "- Redução da taxa de abandono mobile\n"
            benefits_text += "- Melhoria nas métricas de usabilidade\n"
        
        else:
            benefits_text += "- Melhoria geral na otimização para mecanismos de busca\n"
            benefits_text += "- Aumento da qualidade técnica do site\n"
            benefits_text += "- Melhor experiência do usuário\n"
        
        # Benefícios baseados na importância da página
        if problem.page_importance_score >= 90:
            benefits_text += "- **Impacto Alto:** Melhoria significativa no tráfego orgânico\n"
        elif problem.page_importance_score >= 70:
            benefits_text += "- **Impacto Moderado:** Melhoria considerável na visibilidade\n"
        
        return benefits_text
    
    def _estimate_results_timeline(self, problem: SEOProblem) -> str:
        """Estima prazo para observar resultados."""
        timeline_text = "**Prazo Estimado para Resultados:**\n"
        
        if 'Core Web Vitals' in problem.problem_category:
            timeline_text += "- **Testes de laboratório:** Imediatamente após implementação\n"
            timeline_text += "- **Dados de campo (CrUX):** 28 dias para atualização completa\n"
            timeline_text += "- **Impacto no ranking:** 2-4 semanas após dados de campo atualizados\n"
        
        elif 'Technical SEO' in problem.problem_category:
            timeline_text += "- **Crawling:** Próxima visita do Googlebot (1-7 dias)\n"
            timeline_text += "- **Indexação:** 1-2 semanas após correção\n"
            timeline_text += "- **Impacto no ranking:** 2-6 semanas\n"
        
        elif problem.severity == 'High':
            timeline_text += "- **Correção urgente:** Implementar em 1-3 dias\n"
            timeline_text += "- **Resultados iniciais:** 1-2 semanas\n"
            timeline_text += "- **Impacto completo:** 4-8 semanas\n"
        
        else:
            timeline_text += "- **Implementação:** Próximo ciclo de desenvolvimento\n"
            timeline_text += "- **Resultados iniciais:** 2-4 semanas\n"
            timeline_text += "- **Impacto completo:** 6-12 semanas\n"
        
        return timeline_text
    
    def _compile_final_document(self, sections: List[DocumentationSection]) -> Dict[str, Any]:
        """Compila documento final com todas as seções."""
        
        # Cabeçalho do documento
        header = f"""# Relatório de Auditoria SEO Técnica

**Data de Geração:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}
**Total de Problemas:** {len(sections)}
**Gerado por:** Agente de Documentação SEO

---

## Resumo Executivo

Este relatório apresenta os problemas de SEO identificados durante a auditoria técnica, 
organizados por prioridade (severidade + importância da página). Cada problema inclui 
análise detalhada, passos de correção e estimativa de impacto.

### Distribuição por Severidade:
"""
        
        # Contar problemas por severidade
        severity_count = {'ALTA': 0, 'MÉDIA': 0, 'BAIXA': 0}
        for section in sections:
            if '[ALTA]' in section.title:
                severity_count['ALTA'] += 1
            elif '[MÉDIA]' in section.title:
                severity_count['MÉDIA'] += 1
            elif '[BAIXA]' in section.title:
                severity_count['BAIXA'] += 1
        
        header += f"- **Alta Prioridade:** {severity_count['ALTA']} problemas\n"
        header += f"- **Média Prioridade:** {severity_count['MÉDIA']} problemas\n"
        header += f"- **Baixa Prioridade:** {severity_count['BAIXA']} problemas\n\n"
        header += "---\n\n"
        
        # Compilar seções
        markdown_content = header
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_problems': len(sections),
                'severity_distribution': severity_count
            },
            'problems': []
        }
        
        for i, section in enumerate(sections, 1):
            # Markdown
            markdown_content += f"## {i}. {section.title}\n\n"
            markdown_content += f"### 🔍 PROBLEMA / OPORTUNIDADE\n\n"
            markdown_content += f"{section.problem_description}\n"
            markdown_content += f"{section.evidence_list}\n"
            markdown_content += f"{section.impact_analysis}\n\n"
            
            markdown_content += f"### 🔧 SOLUÇÃO\n\n"
            markdown_content += f"{section.technical_steps}\n"
            markdown_content += f"{section.code_snippets}\n"
            markdown_content += f"{section.validation_guide}\n"
            markdown_content += f"{section.official_references}\n\n"
            
            markdown_content += f"### 📈 IMPACTO ESPERADO\n\n"
            markdown_content += f"{section.expected_benefits}\n"
            markdown_content += f"{section.timeline_estimate}\n\n"
            markdown_content += "---\n\n"
            
            # JSON
            json_data['problems'].append({
                'id': i,
                'title': section.title,
                'sections': {
                    'problem': {
                        'description': section.problem_description,
                        'evidence': section.evidence_list,
                        'impact': section.impact_analysis
                    },
                    'solution': {
                        'steps': section.technical_steps,
                        'code': section.code_snippets,
                        'validation': section.validation_guide,
                        'references': section.official_references
                    },
                    'expected_impact': {
                        'benefits': section.expected_benefits,
                        'timeline': section.timeline_estimate
                    }
                }
            })
        
        return {
            'markdown': markdown_content,
            'json': json_data,
            'format': 'hybrid',
            'compatible_with': ['Confluence', 'Notion', 'Excel', 'PDF']
        }


def create_seo_documentation_agent() -> SEODocumentationAgent:
    """Factory function para criar instância do agente de documentação."""
    return SEODocumentationAgent()


# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo
    sample_problems = [
        {
            "url": "https://www.dominioexemplo.com.br/categoria/produto-x",
            "checklist_item_id": "CWV-01",
            "problem_category": "Core Web Vitals",
            "problem_summary": "LCP (Largest Contentful Paint) excede o limite recomendado.",
            "severity": "High",
            "page_importance_score": 92,
            "metrics": {
                "metric_name": "LCP",
                "measured_value": "3.8s",
                "recommended_threshold": "< 2.5s",
                "device": "Mobile"
            },
            "evidence": [
                {
                    "source": "PageSpeed Insights API",
                    "detail": "Relatório de campo indica LCP acima de 2.5s"
                }
            ],
            "remediation_steps": [
                "Otimizar a imagem principal",
                "Implementar pré-carregamento no <head>"
            ],
            "validation_procedure": "Executar novamente o PageSpeed Insights. LCP deve ficar abaixo de 2.5s."
        }
    ]
    
    # Criar agente e processar
    agent = create_seo_documentation_agent()
    result = agent.process_audit_problems(sample_problems)
    
    if result['success']:
        print("✅ Documentação gerada com sucesso!")
        print(f"📄 Seções processadas: {result['sections_count']}")
        print(f"🕒 Gerado em: {result['generated_at']}")
    else:
        print(f"❌ Erro: {result['error']}")