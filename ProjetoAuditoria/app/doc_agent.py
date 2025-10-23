"""
Agente Documentador SEO - Especialista em Comunicação de SEO Técnico

**Atue como um Especialista em Comunicação de SEO Técnico**, responsável por 
traduzir dados brutos de auditoria em documentação clara, profissional e 
acionável para equipes de desenvolvimento e produto.

Este módulo implementa o Agente Documentador que processa problemas de SEO 
em formato JSON e gera documentação técnica bem estruturada, enriquecida 
com referências oficiais do Google Search Central.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .validator_agent import AuditReport, ValidationResult

logger = logging.getLogger(__name__)


class DocumentationError(Exception):
    """Exceção para erros durante geração de documentação."""
    pass


class GoogleDocsClient:
    """
    Cliente para integração com Google Docs API.
    
    Gerencia autenticação e operações de criação/edição de documentos.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Inicializa o cliente Google Docs.
        
        Args:
            credentials_path: Caminho para arquivo de credenciais OAuth2.
            token_path: Caminho para arquivo de token salvo.
        """
        self.credentials_path = credentials_path or os.getenv('GOOGLE_DOCS_CREDENTIALS_PATH')
        self.token_path = token_path or os.getenv('GOOGLE_DOCS_TOKEN_PATH', 'data/token.json')
        
        if not self.credentials_path:
            raise DocumentationError("Caminho das credenciais Google Docs não configurado")
        
        self.service = None
        self.drive_service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Autentica com Google APIs."""
        creds = None
        
        # Carrega token existente
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # Se não há credenciais válidas, solicita autorização
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Salva credenciais para próxima execução
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Constrói serviços
        self.service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
    
    def create_document(self, title: str) -> str:
        """
        Cria um novo documento Google Docs.
        
        Args:
            title: Título do documento.
        
        Returns:
            ID do documento criado.
        
        Raises:
            DocumentationError: Se houver erro na criação.
        """
        try:
            document = {
                'title': title
            }
            
            doc = self.service.documents().create(body=document).execute()
            document_id = doc.get('documentId')
            
            logger.info(f"Documento criado: {title} (ID: {document_id})")
            
            return document_id
            
        except HttpError as e:
            raise DocumentationError(f"Erro ao criar documento: {str(e)}")
    
    def update_document(self, document_id: str, requests: List[Dict[str, Any]]) -> None:
        """
        Atualiza um documento com uma lista de requests.
        
        Args:
            document_id: ID do documento.
            requests: Lista de requests para atualizar o documento.
        
        Raises:
            DocumentationError: Se houver erro na atualização.
        """
        try:
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
        except HttpError as e:
            raise DocumentationError(f"Erro ao atualizar documento: {str(e)}")
    
    def get_document_url(self, document_id: str) -> str:
        """
        Retorna URL pública do documento.
        
        Args:
            document_id: ID do documento.
        
        Returns:
            URL do documento.
        """
        return f"https://docs.google.com/document/d/{document_id}/edit"
    
    def share_document(self, document_id: str, email: str, role: str = 'reader') -> None:
        """
        Compartilha documento com um usuário.
        
        Args:
            document_id: ID do documento.
            email: Email do usuário.
            role: Papel do usuário ('reader', 'writer', 'owner').
        
        Raises:
            DocumentationError: Se houver erro no compartilhamento.
        """
        try:
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            self.drive_service.permissions().create(
                fileId=document_id,
                body=permission,
                sendNotificationEmail=True
            ).execute()
            
            logger.info(f"Documento compartilhado com {email} como {role}")
            
        except HttpError as e:
            raise DocumentationError(f"Erro ao compartilhar documento: {str(e)}")


class DocumentGenerator:
    """
    Gerador de documentos de auditoria SEO.
    
    Converte relatórios de auditoria em documentos Google Docs estruturados.
    """
    
    def __init__(self, docs_client: GoogleDocsClient):
        """
        Inicializa o gerador de documentos.
        
        Args:
            docs_client: Cliente Google Docs autenticado.
        """
        self.docs_client = docs_client
        self.logger = logging.getLogger(__name__)
    
    def generate_audit_document(self, audit_report: AuditReport, template_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Gera documento completo de auditoria SEO.
        
        Args:
            audit_report: Relatório de auditoria.
            template_config: Configurações do template.
        
        Returns:
            ID do documento criado.
        
        Raises:
            DocumentationError: Se houver erro na geração.
        """
        try:
            # Cria documento
            title = f"Auditoria SEO - {audit_report.url} - {audit_report.audit_timestamp.strftime('%d/%m/%Y')}"
            document_id = self.docs_client.create_document(title)
            
            # Gera conteúdo
            requests = self._build_document_requests(audit_report, template_config or {})
            
            # Atualiza documento
            self.docs_client.update_document(document_id, requests)
            
            self.logger.info(f"Documento de auditoria gerado: {document_id}")
            
            return document_id
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar documento: {str(e)}")
            raise DocumentationError(f"Falha na geração do documento: {str(e)}")
    
    def _build_document_requests(self, audit_report: AuditReport, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Constrói requests para estruturar o documento.
        
        Args:
            audit_report: Relatório de auditoria.
            config: Configurações do template.
        
        Returns:
            Lista de requests para o Google Docs API.
        """
        requests = []
        
        # Título principal
        requests.extend(self._create_title_requests(audit_report))
        
        # Resumo executivo
        requests.extend(self._create_executive_summary_requests(audit_report))
        
        # Detalhes das validações
        requests.extend(self._create_validations_section_requests(audit_report))
        
        # Recomendações
        requests.extend(self._create_recommendations_section_requests(audit_report))
        
        # Dados técnicos (se solicitado)
        if config.get('include_technical_data', False):
            requests.extend(self._create_technical_data_section_requests(audit_report))
        
        # Apêndices
        requests.extend(self._create_appendix_requests(audit_report))
        
        return requests
    
    def _create_title_requests(self, audit_report: AuditReport) -> List[Dict[str, Any]]:
        """Cria seção de título do documento."""
        requests = []
        
        # Título principal
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f"AUDITORIA TÉCNICA DE SEO\n\n"
            }
        })
        
        # Informações básicas
        info_text = (
            f"Website: {audit_report.url}\n"
            f"Data da Auditoria: {audit_report.audit_timestamp.strftime('%d/%m/%Y às %H:%M')}\n"
            f"Score Geral: {audit_report.overall_score:.1f}/100\n\n"
        )
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': info_text
            }
        })
        
        return requests
    
    def _create_executive_summary_requests(self, audit_report: AuditReport) -> List[Dict[str, Any]]:
        """Cria seção de resumo executivo."""
        requests = []
        
        # Título da seção
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': "RESUMO EXECUTIVO\n\n"
            }
        })
        
        # Conteúdo do resumo
        summary = audit_report.summary
        
        summary_text = (
            f"Esta auditoria analisou {summary['total_validations']} aspectos técnicos do website {audit_report.url}.\n\n"
            f"Resultados:\n"
            f"• ✅ Validações aprovadas: {summary['status_counts'].get('passed', 0)}\n"
            f"• ⚠️ Avisos: {summary['status_counts'].get('warning', 0)}\n"
            f"• ❌ Problemas críticos: {summary['status_counts'].get('failed', 0)}\n\n"
        )
        
        if summary['top_critical_issues']:
            summary_text += "Principais problemas identificados:\n"
            for issue in summary['top_critical_issues'][:3]:
                summary_text += f"• {issue}\n"
            summary_text += "\n"
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': summary_text
            }
        })
        
        return requests
    
    def _create_validations_section_requests(self, audit_report: AuditReport) -> List[Dict[str, Any]]:
        """Cria seção detalhada das validações."""
        requests = []
        
        # Título da seção
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': "DETALHAMENTO DAS VALIDAÇÕES\n\n"
            }
        })
        
        # Agrupa validações por categoria
        categories = self._group_validations_by_category(audit_report.validations)
        
        for category, validations in categories.items():
            # Título da categoria
            category_title = self._get_category_title(category)
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': f"{category_title}\n"
                }
            })
            
            # Validações da categoria
            for validation in validations:
                status_icon = self._get_status_icon(validation.status)
                validation_text = (
                    f"{status_icon} {validation.message} (Score: {validation.score:.1f}/100)\n"
                )
                
                if validation.recommendations:
                    validation_text += "  Recomendações:\n"
                    for rec in validation.recommendations[:3]:  # Máximo 3 recomendações
                        validation_text += f"  - {rec}\n"
                
                validation_text += "\n"
                
                requests.append({
                    'insertText': {
                        'location': {'index': 1},
                        'text': validation_text
                    }
                })
        
        return requests
    
    def _create_recommendations_section_requests(self, audit_report: AuditReport) -> List[Dict[str, Any]]:
        """Cria seção de recomendações consolidadas."""
        requests = []
        
        # Título da seção
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': "RECOMENDAÇÕES PRIORITÁRIAS\n\n"
            }
        })
        
        # Coleta todas as recomendações
        all_recommendations = []
        for validation in audit_report.validations:
            all_recommendations.extend(validation.recommendations)
        
        # Remove duplicatas e prioriza
        unique_recommendations = list(set(all_recommendations))
        
        # Prioriza recomendações de validações com status 'failed'
        priority_recommendations = []
        for validation in audit_report.validations:
            if validation.status == 'failed':
                priority_recommendations.extend(validation.recommendations)
        
        priority_recommendations = list(set(priority_recommendations))
        
        # Adiciona recomendações prioritárias
        if priority_recommendations:
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': "Ações Críticas (Alta Prioridade):\n"
                }
            })
            
            for i, rec in enumerate(priority_recommendations[:5], 1):
                requests.append({
                    'insertText': {
                        'location': {'index': 1},
                        'text': f"{i}. {rec}\n"
                    }
                })
            
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': "\n"
                }
            })
        
        # Outras recomendações
        other_recommendations = [rec for rec in unique_recommendations if rec not in priority_recommendations]
        
        if other_recommendations:
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': "Melhorias Adicionais:\n"
                }
            })
            
            for i, rec in enumerate(other_recommendations[:10], 1):
                requests.append({
                    'insertText': {
                        'location': {'index': 1},
                        'text': f"{i}. {rec}\n"
                    }
                })
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': "\n"
            }
        })
        
        return requests
    
    def _create_technical_data_section_requests(self, audit_report: AuditReport) -> List[Dict[str, Any]]:
        """Cria seção com dados técnicos detalhados."""
        requests = []
        
        # Título da seção
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': "DADOS TÉCNICOS DETALHADOS\n\n"
            }
        })
        
        # Fontes de dados utilizadas
        data_sources = audit_report.summary.get('data_sources', [])
        if data_sources:
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': f"Fontes de dados utilizadas: {', '.join(data_sources)}\n\n"
                }
            })
        
        # Completude da auditoria
        completeness = audit_report.summary.get('audit_completeness', 0)
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f"Completude da auditoria: {completeness:.1f}%\n\n"
            }
        })
        
        return requests
    
    def _create_appendix_requests(self, audit_report: AuditReport) -> List[Dict[str, Any]]:
        """Cria seção de apêndices."""
        requests = []
        
        # Título da seção
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': "APÊNDICES\n\n"
            }
        })
        
        # Metodologia
        methodology_text = (
            "Metodologia da Auditoria:\n"
            "Esta auditoria foi realizada utilizando múltiplas fontes de dados:\n"
            "• Google PageSpeed Insights para análise de performance\n"
            "• Google Search Console para dados de busca orgânica\n"
            "• Google Analytics 4 para métricas de comportamento\n"
            "• Screaming Frog SEO Spider para análise técnica\n"
            "• Chrome DevTools para validações adicionais\n\n"
            "Os scores são calculados com base em pesos específicos para cada categoria de validação.\n\n"
        )
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': methodology_text
            }
        })
        
        # Timestamp da geração
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f"Documento gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n"
            }
        })
        
        return requests
    
    def _group_validations_by_category(self, validations: List[ValidationResult]) -> Dict[str, List[ValidationResult]]:
        """Agrupa validações por categoria."""
        categories = {}
        
        category_mapping = {
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
        
        for validation in validations:
            category = category_mapping.get(validation.validation_type, 'other')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(validation)
        
        return categories
    
    def _get_category_title(self, category: str) -> str:
        """Retorna título formatado da categoria."""
        titles = {
            'performance': 'Performance e Velocidade',
            'technical_seo': 'SEO Técnico',
            'content_quality': 'Qualidade do Conteúdo',
            'crawlability': 'Crawlability e Indexação',
            'analytics_health': 'Saúde do Analytics',
            'other': 'Outras Validações'
        }
        
        return titles.get(category, category.title())
    
    def _get_status_icon(self, status: str) -> str:
        """Retorna ícone baseado no status."""
        icons = {
            'passed': '✅',
            'warning': '⚠️',
            'failed': '❌',
            'error': '🔴'
        }
        
        return icons.get(status, '❓')


class DocumentorAgent:
    """
    Agente Documentador principal.
    
    Coordena a geração de documentação de auditoria SEO.
    """
    
    def __init__(self):
        """Inicializa o Agente Documentador."""
        self.logger = logging.getLogger(__name__)
        
        # Verificar se está em modo de desenvolvimento
        dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
        
        if dev_mode:
            self.logger.info("Modo de desenvolvimento ativado - Google Docs desabilitado")
            self.docs_client = None
            self.document_generator = None
            self.is_available = False
        else:
            try:
                self.docs_client = GoogleDocsClient()
                self.document_generator = DocumentGenerator(self.docs_client)
                self.is_available = True
            except DocumentationError as e:
                self.logger.warning(f"Google Docs não disponível: {str(e)}")
                self.is_available = False
    
    def generate_audit_documentation(self, audit_report: AuditReport, 
                                   share_with: Optional[List[str]] = None,
                                   template_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gera documentação completa da auditoria.
        
        Args:
            audit_report: Relatório de auditoria.
            share_with: Lista de emails para compartilhar o documento.
            template_config: Configurações do template.
        
        Returns:
            Informações do documento gerado.
        
        Raises:
            DocumentationError: Se houver erro na geração.
        """
        if not self.is_available:
            # Em modo de desenvolvimento, retorna documentação simulada
            self.logger.info("Modo de desenvolvimento: gerando documentação simulada")
            return {
                'document_id': f'dev-doc-{audit_report.url.replace("https://", "").replace("/", "-")}',
                'document_url': f'file://dev-documentation-{audit_report.url.replace("https://", "").replace("/", "-")}.html',
                'created_at': datetime.now().isoformat(),
                'audit_url': audit_report.url,
                'audit_score': audit_report.overall_score,
                'shared_with': share_with or [],
                'dev_mode': True,
                'summary': f'Documentação simulada para auditoria de {audit_report.url} com {len(audit_report.validations)} validações'
            }
        
        try:
            self.logger.info(f"Gerando documentação para auditoria de {audit_report.url}")
            
            # Gera documento
            document_id = self.document_generator.generate_audit_document(
                audit_report, template_config
            )
            
            # Compartilha documento se solicitado
            if share_with:
                for email in share_with:
                    try:
                        self.docs_client.share_document(document_id, email, 'reader')
                    except DocumentationError as e:
                        self.logger.warning(f"Erro ao compartilhar com {email}: {str(e)}")
            
            # Retorna informações do documento
            document_info = {
                'document_id': document_id,
                'document_url': self.docs_client.get_document_url(document_id),
                'created_at': datetime.now().isoformat(),
                'audit_url': audit_report.url,
                'audit_score': audit_report.overall_score,
                'shared_with': share_with or []
            }
            
            self.logger.info(f"Documentação gerada com sucesso: {document_id}")
            
            return document_info
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar documentação: {str(e)}")
            raise DocumentationError(f"Falha na geração da documentação: {str(e)}")
    
    def create_summary_document(self, audit_reports: List[AuditReport]) -> Dict[str, Any]:
        """
        Cria documento resumo de múltiplas auditorias.
        
        Args:
            audit_reports: Lista de relatórios de auditoria.
        
        Returns:
            Informações do documento resumo.
        
        Raises:
            DocumentationError: Se houver erro na geração.
        """
        if not self.is_available:
            raise DocumentationError("Google Docs não está disponível")
        
        if not audit_reports:
            raise DocumentationError("Nenhum relatório fornecido para resumo")
        
        try:
            # Cria documento resumo
            title = f"Resumo de Auditorias SEO - {datetime.now().strftime('%d/%m/%Y')}"
            document_id = self.docs_client.create_document(title)
            
            # Gera conteúdo do resumo
            requests = self._build_summary_requests(audit_reports)
            
            # Atualiza documento
            self.docs_client.update_document(document_id, requests)
            
            document_info = {
                'document_id': document_id,
                'document_url': self.docs_client.get_document_url(document_id),
                'created_at': datetime.now().isoformat(),
                'audit_count': len(audit_reports),
                'websites': [report.url for report in audit_reports]
            }
            
            self.logger.info(f"Documento resumo gerado: {document_id}")
            
            return document_info
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo: {str(e)}")
            raise DocumentationError(f"Falha na geração do resumo: {str(e)}")
    
    def _build_summary_requests(self, audit_reports: List[AuditReport]) -> List[Dict[str, Any]]:
        """Constrói requests para documento resumo."""
        requests = []
        
        # Título
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f"RESUMO DE AUDITORIAS SEO\n\n"
            }
        })
        
        # Informações gerais
        avg_score = sum(report.overall_score for report in audit_reports) / len(audit_reports)
        
        summary_text = (
            f"Total de websites auditados: {len(audit_reports)}\n"
            f"Score médio geral: {avg_score:.1f}/100\n"
            f"Data do resumo: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        )
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': summary_text
            }
        })
        
        # Lista de websites
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': "WEBSITES AUDITADOS:\n\n"
            }
        })
        
        for i, report in enumerate(audit_reports, 1):
            website_text = (
                f"{i}. {report.url}\n"
                f"   Score: {report.overall_score:.1f}/100\n"
                f"   Data: {report.audit_timestamp.strftime('%d/%m/%Y')}\n"
                f"   Problemas críticos: {report.summary['critical_issues_count']}\n\n"
            )
            
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': website_text
                }
            })
        
        return requests