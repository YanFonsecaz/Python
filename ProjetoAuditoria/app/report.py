"""
Módulo de Geração de Relatórios de Auditoria SEO.

Este módulo fornece funcionalidades específicas para formatação,
exportação e apresentação de relatórios de auditoria técnica de SEO
em diferentes formatos (JSON, HTML, PDF).
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict
import base64
from io import BytesIO

from .validator_agent import AuditReport, ValidationResult
from .consolidate import ConsolidatedMetrics, ConsolidatedInsight

logger = logging.getLogger(__name__)


class ReportFormatter:
    """
    Formatador de relatórios em diferentes formatos.
    
    Converte relatórios de auditoria para JSON, HTML e outros formatos
    de apresentação e exportação.
    """
    
    def __init__(self):
        """Inicializa o formatador de relatórios."""
        self.logger = logging.getLogger(__name__)
    
    def format_json_report(self, audit_report: AuditReport, 
                          include_raw_data: bool = False) -> Dict[str, Any]:
        """
        Formata relatório em JSON estruturado.
        
        Args:
            audit_report: Relatório de auditoria.
            include_raw_data: Se deve incluir dados brutos.
        
        Returns:
            Relatório formatado em JSON.
        """
        try:
            # Converte validações para dicionários
            validations_data = []
            for validation in audit_report.validations:
                validation_dict = {
                    'validation_type': validation.validation_type,
                    'status': validation.status,
                    'score': validation.score,
                    'message': validation.message,
                    'recommendations': validation.recommendations,
                    'timestamp': validation.timestamp.isoformat() if hasattr(validation, 'timestamp') else None,
                    'details': validation.details if hasattr(validation, 'details') else {}
                }
                validations_data.append(validation_dict)
            
            # Estrutura principal do relatório
            report_data = {
                'audit_info': {
                    'url': audit_report.url,
                    'overall_score': audit_report.overall_score,
                    'audit_timestamp': audit_report.audit_timestamp.isoformat(),
                    'report_version': '1.0'
                },
                'summary': audit_report.summary,
                'validations': validations_data,
                'metadata': {
                    'total_validations': len(audit_report.validations),
                    'generation_timestamp': datetime.now().isoformat(),
                    'data_sources_used': audit_report.summary.get('data_sources', [])
                }
            }
            
            # Inclui dados brutos se solicitado
            if include_raw_data and audit_report.raw_data:
                report_data['raw_data'] = audit_report.raw_data
            
            self.logger.info(f"Relatório JSON formatado para {audit_report.url}")
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Erro ao formatar relatório JSON: {str(e)}")
            raise
    
    def format_html_report(self, audit_report: AuditReport) -> str:
        """
        Formata relatório em HTML para visualização web.
        
        Args:
            audit_report: Relatório de auditoria.
        
        Returns:
            HTML do relatório.
        """
        try:
            # Template HTML base
            html_template = self._get_html_template()
            
            # Dados para o template
            template_data = {
                'url': audit_report.url,
                'overall_score': audit_report.overall_score,
                'audit_date': audit_report.audit_timestamp.strftime('%d/%m/%Y às %H:%M'),
                'summary': audit_report.summary,
                'validations': audit_report.validations,
                'score_color': self._get_score_color(audit_report.overall_score),
                'generation_time': datetime.now().strftime('%d/%m/%Y às %H:%M')
            }
            
            # Renderiza template
            html_content = html_template.format(**template_data)
            
            # Adiciona seções específicas
            html_content = self._add_validations_section(html_content, audit_report.validations)
            html_content = self._add_recommendations_section(html_content, audit_report.validations)
            
            self.logger.info(f"Relatório HTML formatado para {audit_report.url}")
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"Erro ao formatar relatório HTML: {str(e)}")
            raise
    
    def format_summary_report(self, audit_report: AuditReport) -> Dict[str, Any]:
        """
        Formata relatório resumido para dashboards.
        
        Args:
            audit_report: Relatório de auditoria.
        
        Returns:
            Relatório resumido.
        """
        try:
            # Calcula estatísticas rápidas
            validations_by_status = {}
            for validation in audit_report.validations:
                status = validation.status
                validations_by_status[status] = validations_by_status.get(status, 0) + 1
            
            # Identifica top 3 problemas críticos
            critical_issues = [
                v.message for v in audit_report.validations 
                if v.status == 'failed'
            ][:3]
            
            # Calcula scores por categoria
            category_scores = self._calculate_category_scores(audit_report.validations)
            
            summary_report = {
                'url': audit_report.url,
                'overall_score': audit_report.overall_score,
                'audit_date': audit_report.audit_timestamp.isoformat(),
                'status_summary': {
                    'passed': validations_by_status.get('passed', 0),
                    'warning': validations_by_status.get('warning', 0),
                    'failed': validations_by_status.get('failed', 0),
                    'error': validations_by_status.get('error', 0)
                },
                'category_scores': category_scores,
                'top_critical_issues': critical_issues,
                'data_completeness': audit_report.summary.get('audit_completeness', 0),
                'confidence_level': audit_report.summary.get('confidence_level', 0)
            }
            
            self.logger.info(f"Relatório resumido formatado para {audit_report.url}")
            
            return summary_report
            
        except Exception as e:
            self.logger.error(f"Erro ao formatar relatório resumido: {str(e)}")
            raise
    
    def _get_html_template(self) -> str:
        """Retorna template HTML base."""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria SEO - {url}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        .score-circle {{
            display: inline-block;
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: {score_color};
            color: white;
            font-size: 24px;
            font-weight: bold;
            line-height: 120px;
            text-align: center;
            margin: 20px 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .validation-item {{
            margin: 15px 0;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        .status-passed {{ border-left-color: #28a745; background: #d4edda; }}
        .status-warning {{ border-left-color: #ffc107; background: #fff3cd; }}
        .status-failed {{ border-left-color: #dc3545; background: #f8d7da; }}
        .status-error {{ border-left-color: #6c757d; background: #e2e3e5; }}
        .recommendations {{
            background: #e7f3ff;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Auditoria Técnica de SEO</h1>
            <h2>{url}</h2>
            <div class="score-circle">{overall_score:.1f}</div>
            <p>Auditoria realizada em {audit_date}</p>
        </div>
        
        <div class="summary-grid">
            <!-- Seções serão adicionadas dinamicamente -->
        </div>
        
        <div id="validations-section">
            <!-- Validações serão adicionadas aqui -->
        </div>
        
        <div id="recommendations-section">
            <!-- Recomendações serão adicionadas aqui -->
        </div>
        
        <div class="footer">
            <p>Relatório gerado em {generation_time}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_score_color(self, score: float) -> str:
        """Retorna cor baseada no score."""
        if score >= 80:
            return '#28a745'  # Verde
        elif score >= 60:
            return '#ffc107'  # Amarelo
        else:
            return '#dc3545'  # Vermelho
    
    def _add_validations_section(self, html_content: str, 
                               validations: List[ValidationResult]) -> str:
        """Adiciona seção de validações ao HTML."""
        validations_html = '<h3>Detalhamento das Validações</h3>'
        
        for validation in validations:
            status_class = f"status-{validation.status}"
            status_icon = self._get_status_icon(validation.status)
            
            validations_html += f"""
            <div class="validation-item {status_class}">
                <strong>{status_icon} {validation.message}</strong>
                <p>Score: {validation.score:.1f}/100 | Fonte: {validation.data_source}</p>
                {self._format_recommendations_html(validation.recommendations)}
            </div>
            """
        
        return html_content.replace('<!-- Validações serão adicionadas aqui -->', validations_html)
    
    def _add_recommendations_section(self, html_content: str,
                                   validations: List[ValidationResult]) -> str:
        """Adiciona seção de recomendações ao HTML."""
        # Coleta todas as recomendações
        all_recommendations = []
        for validation in validations:
            if validation.status in ['failed', 'warning']:
                all_recommendations.extend(validation.recommendations)
        
        # Remove duplicatas
        unique_recommendations = list(set(all_recommendations))
        
        recommendations_html = """
        <div class="recommendations">
            <h3>Recomendações Prioritárias</h3>
            <ol>
        """
        
        for rec in unique_recommendations[:10]:  # Top 10 recomendações
            recommendations_html += f"<li>{rec}</li>"
        
        recommendations_html += """
            </ol>
        </div>
        """
        
        return html_content.replace('<!-- Recomendações serão adicionadas aqui -->', recommendations_html)
    
    def _get_status_icon(self, status: str) -> str:
        """Retorna ícone baseado no status."""
        icons = {
            'passed': '✅',
            'warning': '⚠️',
            'failed': '❌',
            'error': '🔴'
        }
        return icons.get(status, '❓')
    
    def _format_recommendations_html(self, recommendations: List[str]) -> str:
        """Formata recomendações em HTML."""
        if not recommendations:
            return ""
        
        html = "<ul>"
        for rec in recommendations[:3]:  # Máximo 3 recomendações por validação
            html += f"<li>{rec}</li>"
        html += "</ul>"
        
        return html
    
    def _calculate_category_scores(self, validations: List[ValidationResult]) -> Dict[str, float]:
        """Calcula scores por categoria."""
        from .consolidate import DataConsolidator
        
        consolidator = DataConsolidator()
        category_scores = {}
        
        # Agrupa validações por categoria
        for category in ['performance', 'seo_health', 'technical', 'content_quality', 'analytics_health']:
            category_validations = [
                v for v in validations 
                if consolidator.VALIDATION_CATEGORIES.get(v.validation_type) == category
            ]
            
            if category_validations:
                avg_score = sum(v.score for v in category_validations) / len(category_validations)
                category_scores[category] = avg_score
            else:
                category_scores[category] = 0
        
        return category_scores


class ReportExporter:
    """
    Exportador de relatórios para diferentes formatos e destinos.
    
    Gerencia a exportação de relatórios para arquivos locais,
    armazenamento em nuvem e integração com sistemas externos.
    """
    
    def __init__(self, export_directory: str = "data/reports"):
        """
        Inicializa o exportador de relatórios.
        
        Args:
            export_directory: Diretório para salvar relatórios exportados.
        """
        self.export_directory = export_directory
        self.logger = logging.getLogger(__name__)
        
        # Cria diretório se não existir
        os.makedirs(export_directory, exist_ok=True)
    
    def export_json_report(self, audit_report: AuditReport, 
                          filename: Optional[str] = None,
                          include_raw_data: bool = False) -> str:
        """
        Exporta relatório em formato JSON.
        
        Args:
            audit_report: Relatório de auditoria.
            filename: Nome do arquivo (opcional).
            include_raw_data: Se deve incluir dados brutos.
        
        Returns:
            Caminho do arquivo exportado.
        """
        try:
            # Gera nome do arquivo se não fornecido
            if not filename:
                timestamp = audit_report.audit_timestamp.strftime('%Y%m%d_%H%M%S')
                safe_url = audit_report.url.replace('https://', '').replace('http://', '').replace('/', '_')
                filename = f"audit_{safe_url}_{timestamp}.json"
            
            filepath = os.path.join(self.export_directory, filename)
            
            # Formata relatório
            formatter = ReportFormatter()
            report_data = formatter.format_json_report(audit_report, include_raw_data)
            
            # Salva arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Relatório JSON exportado: {filepath}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório JSON: {str(e)}")
            raise
    
    def export_html_report(self, audit_report: AuditReport,
                          filename: Optional[str] = None) -> str:
        """
        Exporta relatório em formato HTML.
        
        Args:
            audit_report: Relatório de auditoria.
            filename: Nome do arquivo (opcional).
        
        Returns:
            Caminho do arquivo exportado.
        """
        try:
            # Gera nome do arquivo se não fornecido
            if not filename:
                timestamp = audit_report.audit_timestamp.strftime('%Y%m%d_%H%M%S')
                safe_url = audit_report.url.replace('https://', '').replace('http://', '').replace('/', '_')
                filename = f"audit_{safe_url}_{timestamp}.html"
            
            filepath = os.path.join(self.export_directory, filename)
            
            # Formata relatório
            formatter = ReportFormatter()
            html_content = formatter.format_html_report(audit_report)
            
            # Salva arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Relatório HTML exportado: {filepath}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório HTML: {str(e)}")
            raise
    
    def export_csv_summary(self, audit_reports: List[AuditReport],
                          filename: Optional[str] = None) -> str:
        """
        Exporta resumo de múltiplos relatórios em CSV.
        
        Args:
            audit_reports: Lista de relatórios de auditoria.
            filename: Nome do arquivo (opcional).
        
        Returns:
            Caminho do arquivo exportado.
        """
        try:
            import csv
            
            # Gera nome do arquivo se não fornecido
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"audit_summary_{timestamp}.csv"
            
            filepath = os.path.join(self.export_directory, filename)
            
            # Prepara dados para CSV
            formatter = ReportFormatter()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'url', 'overall_score', 'audit_date', 'passed_count',
                    'warning_count', 'failed_count', 'critical_issues_count',
                    'data_completeness', 'confidence_level'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for report in audit_reports:
                    summary = formatter.format_summary_report(report)
                    
                    row = {
                        'url': report.url,
                        'overall_score': report.overall_score,
                        'audit_date': report.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'passed_count': summary['status_summary']['passed'],
                        'warning_count': summary['status_summary']['warning'],
                        'failed_count': summary['status_summary']['failed'],
                        'critical_issues_count': len(summary['top_critical_issues']),
                        'data_completeness': summary['data_completeness'],
                        'confidence_level': summary['confidence_level']
                    }
                    
                    writer.writerow(row)
            
            self.logger.info(f"Resumo CSV exportado: {filepath}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar resumo CSV: {str(e)}")
            raise
    
    def create_archive(self, audit_reports: List[AuditReport],
                      archive_name: Optional[str] = None) -> str:
        """
        Cria arquivo compactado com múltiplos relatórios.
        
        Args:
            audit_reports: Lista de relatórios de auditoria.
            archive_name: Nome do arquivo (opcional).
        
        Returns:
            Caminho do arquivo compactado.
        """
        try:
            import zipfile
            
            # Gera nome do arquivo se não fornecido
            if not archive_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archive_name = f"audit_reports_{timestamp}.zip"
            
            archive_path = os.path.join(self.export_directory, archive_name)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adiciona relatórios individuais
                for i, report in enumerate(audit_reports):
                    # JSON
                    json_filename = f"report_{i+1}_{report.url.replace('https://', '').replace('http://', '').replace('/', '_')}.json"
                    json_path = self.export_json_report(report, json_filename)
                    zipf.write(json_path, json_filename)
                    
                    # HTML
                    html_filename = f"report_{i+1}_{report.url.replace('https://', '').replace('http://', '').replace('/', '_')}.html"
                    html_path = self.export_html_report(report, html_filename)
                    zipf.write(html_path, html_filename)
                
                # Adiciona resumo CSV
                csv_path = self.export_csv_summary(audit_reports, "summary.csv")
                zipf.write(csv_path, "summary.csv")
            
            self.logger.info(f"Arquivo compactado criado: {archive_path}")
            
            return archive_path
            
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo compactado: {str(e)}")
            raise


class ReportManager:
    """
    Gerenciador principal de relatórios.
    
    Coordena formatação, exportação e distribuição de relatórios
    de auditoria SEO.
    """
    
    def __init__(self, export_directory: str = "data/reports"):
        """
        Inicializa o gerenciador de relatórios.
        
        Args:
            export_directory: Diretório para exportação.
        """
        self.formatter = ReportFormatter()
        self.exporter = ReportExporter(export_directory)
        self.logger = logging.getLogger(__name__)
    
    def generate_complete_report_package(self, audit_report: AuditReport,
                                       export_formats: List[str] = None) -> Dict[str, str]:
        """
        Gera pacote completo de relatórios em múltiplos formatos.
        
        Args:
            audit_report: Relatório de auditoria.
            export_formats: Formatos desejados ['json', 'html', 'summary'].
        
        Returns:
            Dicionário com caminhos dos arquivos gerados.
        """
        if export_formats is None:
            export_formats = ['json', 'html', 'summary']
        
        try:
            self.logger.info(f"Gerando pacote completo de relatórios para {audit_report.url}")
            
            generated_files = {}
            
            # Gera relatório JSON
            if 'json' in export_formats:
                json_path = self.exporter.export_json_report(audit_report, include_raw_data=True)
                generated_files['json'] = json_path
            
            # Gera relatório HTML
            if 'html' in export_formats:
                html_path = self.exporter.export_html_report(audit_report)
                generated_files['html'] = html_path
            
            # Gera resumo JSON
            if 'summary' in export_formats:
                summary_data = self.formatter.format_summary_report(audit_report)
                
                timestamp = audit_report.audit_timestamp.strftime('%Y%m%d_%H%M%S')
                safe_url = audit_report.url.replace('https://', '').replace('http://', '').replace('/', '_')
                summary_filename = f"summary_{safe_url}_{timestamp}.json"
                summary_path = os.path.join(self.exporter.export_directory, summary_filename)
                
                with open(summary_path, 'w', encoding='utf-8') as f:
                    json.dump(summary_data, f, indent=2, ensure_ascii=False)
                
                generated_files['summary'] = summary_path
            
            self.logger.info(f"Pacote de relatórios gerado: {len(generated_files)} arquivos")
            
            return generated_files
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar pacote de relatórios: {str(e)}")
            raise
    
    def generate_batch_reports(self, audit_reports: List[AuditReport],
                             create_archive: bool = True) -> Dict[str, Any]:
        """
        Gera relatórios em lote para múltiplas auditorias.
        
        Args:
            audit_reports: Lista de relatórios de auditoria.
            create_archive: Se deve criar arquivo compactado.
        
        Returns:
            Informações dos arquivos gerados.
        """
        try:
            self.logger.info(f"Gerando relatórios em lote para {len(audit_reports)} auditorias")
            
            batch_info = {
                'total_reports': len(audit_reports),
                'generated_files': [],
                'summary_file': None,
                'archive_file': None,
                'generation_timestamp': datetime.now().isoformat()
            }
            
            # Gera relatórios individuais
            for report in audit_reports:
                files = self.generate_complete_report_package(report)
                batch_info['generated_files'].append({
                    'url': report.url,
                    'files': files
                })
            
            # Gera resumo CSV
            csv_path = self.exporter.export_csv_summary(audit_reports)
            batch_info['summary_file'] = csv_path
            
            # Cria arquivo compactado se solicitado
            if create_archive:
                archive_path = self.exporter.create_archive(audit_reports)
                batch_info['archive_file'] = archive_path
            
            self.logger.info(f"Relatórios em lote gerados com sucesso")
            
            return batch_info
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatórios em lote: {str(e)}")
            raise
    
    def get_report_statistics(self, audit_reports: List[AuditReport]) -> Dict[str, Any]:
        """
        Calcula estatísticas dos relatórios.
        
        Args:
            audit_reports: Lista de relatórios de auditoria.
        
        Returns:
            Estatísticas dos relatórios.
        """
        try:
            if not audit_reports:
                return {'error': 'Nenhum relatório fornecido'}
            
            # Calcula estatísticas básicas
            scores = [report.overall_score for report in audit_reports]
            
            statistics_data = {
                'total_reports': len(audit_reports),
                'score_statistics': {
                    'average': sum(scores) / len(scores),
                    'min': min(scores),
                    'max': max(scores),
                    'median': sorted(scores)[len(scores) // 2]
                },
                'date_range': {
                    'earliest': min(report.audit_timestamp for report in audit_reports).isoformat(),
                    'latest': max(report.audit_timestamp for report in audit_reports).isoformat()
                },
                'websites': [report.url for report in audit_reports],
                'total_validations': sum(len(report.validations) for report in audit_reports),
                'average_validations_per_report': sum(len(report.validations) for report in audit_reports) / len(audit_reports)
            }
            
            # Analisa distribuição de scores
            score_distribution = {
                'excellent': len([s for s in scores if s >= 90]),
                'good': len([s for s in scores if 80 <= s < 90]),
                'fair': len([s for s in scores if 60 <= s < 80]),
                'poor': len([s for s in scores if s < 60])
            }
            
            statistics_data['score_distribution'] = score_distribution
            
            return statistics_data
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular estatísticas: {str(e)}")
            raise