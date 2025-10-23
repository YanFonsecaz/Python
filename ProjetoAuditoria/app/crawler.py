"""
Módulo de integração com Screaming Frog CLI para auditoria técnica de SEO.

Este módulo fornece funcionalidades para executar crawls automatizados
usando o Screaming Frog SEO Spider via linha de comando.
"""

import os
import subprocess
import json
import csv
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ScreamingFrogError(Exception):
    """Exceção customizada para erros do Screaming Frog."""
    pass


class ScreamingFrogCrawler:
    """
    Cliente para integração com Screaming Frog SEO Spider CLI.
    
    Permite executar crawls automatizados e extrair dados técnicos
    para auditoria de SEO.
    """
    
    def __init__(self, executable_path: Optional[str] = None):
        """
        Inicializa o crawler do Screaming Frog.
        
        Args:
            executable_path: Caminho para o executável do Screaming Frog.
                           Se None, usa o valor da variável de ambiente.
        """
        self.executable_path = executable_path or os.getenv('SCREAMING_FROG_PATH')
        if not self.executable_path:
            raise ScreamingFrogError("Caminho do Screaming Frog não configurado")
        
        self.output_dir = Path("data/screaming_frog")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações padrão do crawler
        self.default_config = {
            'max_crawl_depth': 3,
            'max_urls': 1000,
            'timeout': 300,  # 5 minutos
            'user_agent': 'ScreamingFrogSEOSpider/18.0',
            'respect_robots_txt': True,
            'follow_redirects': True
        }
    
    def validate_executable(self) -> bool:
        """
        Valida se o executável do Screaming Frog está disponível.
        
        Returns:
            True se o executável está disponível, False caso contrário.
        """
        try:
            result = subprocess.run(
                [self.executable_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def crawl_website(self, url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa um crawl completo de um website.
        
        Args:
            url: URL do website para fazer crawl.
            config: Configurações específicas para o crawl.
        
        Returns:
            Dicionário com os resultados do crawl.
        
        Raises:
            ScreamingFrogError: Se houver erro durante o crawl.
        """
        if not self.validate_executable():
            raise ScreamingFrogError("Screaming Frog não está disponível")
        
        # Mescla configurações padrão com as fornecidas
        crawl_config = {**self.default_config, **(config or {})}
        
        # Gera nome único para os arquivos de saída
        timestamp = int(time.time())
        output_prefix = f"crawl_{timestamp}"
        
        try:
            # Constrói comando do Screaming Frog
            command = self._build_crawl_command(url, output_prefix, crawl_config)
            
            logger.info(f"Iniciando crawl de {url}")
            
            # Executa o crawl
            result = subprocess.run(
                command,
                cwd=str(self.output_dir),
                capture_output=True,
                text=True,
                timeout=crawl_config['timeout']
            )
            
            if result.returncode != 0:
                raise ScreamingFrogError(f"Erro no crawl: {result.stderr}")
            
            # Processa os resultados
            crawl_results = self._process_crawl_results(output_prefix)
            
            logger.info(f"Crawl concluído: {len(crawl_results.get('urls', []))} URLs encontradas")
            
            return {
                'url': url,
                'timestamp': timestamp,
                'config': crawl_config,
                'results': crawl_results,
                'output_files': self._get_output_files(output_prefix)
            }
            
        except subprocess.TimeoutExpired:
            raise ScreamingFrogError(f"Timeout no crawl após {crawl_config['timeout']} segundos")
        except Exception as e:
            raise ScreamingFrogError(f"Erro inesperado no crawl: {str(e)}")
    
    def _build_crawl_command(self, url: str, output_prefix: str, config: Dict[str, Any]) -> List[str]:
        """
        Constrói o comando para executar o Screaming Frog.
        
        Args:
            url: URL para fazer crawl.
            output_prefix: Prefixo para arquivos de saída.
            config: Configurações do crawl.
        
        Returns:
            Lista com o comando e argumentos.
        """
        command = [
            self.executable_path,
            '--headless',
            '--crawl', url,
            '--output-folder', str(self.output_dir),
            '--bulk-export', 'Internal:All',
            '--bulk-export', 'Response Codes:All',
            '--bulk-export', 'Page Titles:All',
            '--bulk-export', 'Meta Description:All',
            '--bulk-export', 'H1:All',
            '--bulk-export', 'Images:All',
            '--bulk-export', 'External Links:All'
        ]
        
        # Adiciona configurações específicas
        if config.get('max_crawl_depth'):
            command.extend(['--crawl-depth', str(config['max_crawl_depth'])])
        
        if config.get('max_urls'):
            command.extend(['--max-crawl-urls', str(config['max_urls'])])
        
        if config.get('user_agent'):
            command.extend(['--user-agent', config['user_agent']])
        
        if not config.get('respect_robots_txt', True):
            command.append('--ignore-robots-txt')
        
        return command
    
    def _process_crawl_results(self, output_prefix: str) -> Dict[str, Any]:
        """
        Processa os arquivos de resultado do crawl.
        
        Args:
            output_prefix: Prefixo dos arquivos de saída.
        
        Returns:
            Dicionário com dados processados.
        """
        results = {
            'urls': [],
            'response_codes': [],
            'page_titles': [],
            'meta_descriptions': [],
            'h1_tags': [],
            'images': [],
            'external_links': [],
            'summary': {}
        }
        
        # Mapeia tipos de arquivo para chaves de resultado
        file_mappings = {
            'internal_all.csv': 'urls',
            'response_codes_all.csv': 'response_codes',
            'page_titles_all.csv': 'page_titles',
            'meta_description_all.csv': 'meta_descriptions',
            'h1_all.csv': 'h1_tags',
            'images_all.csv': 'images',
            'external_links_all.csv': 'external_links'
        }
        
        for filename, result_key in file_mappings.items():
            file_path = self.output_dir / filename
            if file_path.exists():
                try:
                    data = self._read_csv_file(file_path)
                    results[result_key] = data
                except Exception as e:
                    logger.warning(f"Erro ao processar {filename}: {str(e)}")
        
        # Gera resumo dos resultados
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _read_csv_file(self, file_path: Path) -> List[Dict[str, str]]:
        """
        Lê um arquivo CSV e retorna os dados como lista de dicionários.
        
        Args:
            file_path: Caminho para o arquivo CSV.
        
        Returns:
            Lista de dicionários com os dados do CSV.
        """
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
        except UnicodeDecodeError:
            # Tenta com encoding alternativo
            with open(file_path, 'r', encoding='latin-1') as file:
                reader = csv.DictReader(file)
                data = list(reader)
        
        return data
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera um resumo dos resultados do crawl.
        
        Args:
            results: Dados do crawl.
        
        Returns:
            Dicionário com resumo estatístico.
        """
        summary = {
            'total_urls': len(results.get('urls', [])),
            'response_codes_count': {},
            'images_count': len(results.get('images', [])),
            'external_links_count': len(results.get('external_links', [])),
            'pages_without_title': 0,
            'pages_without_meta_description': 0,
            'pages_without_h1': 0
        }
        
        # Conta códigos de resposta
        for response in results.get('response_codes', []):
            code = response.get('Status Code', 'Unknown')
            summary['response_codes_count'][code] = summary['response_codes_count'].get(code, 0) + 1
        
        # Conta páginas sem elementos importantes
        for title in results.get('page_titles', []):
            if not title.get('Title 1', '').strip():
                summary['pages_without_title'] += 1
        
        for meta in results.get('meta_descriptions', []):
            if not meta.get('Meta Description 1', '').strip():
                summary['pages_without_meta_description'] += 1
        
        for h1 in results.get('h1_tags', []):
            if not h1.get('H1-1', '').strip():
                summary['pages_without_h1'] += 1
        
        return summary
    
    def _get_output_files(self, output_prefix: str) -> List[str]:
        """
        Retorna lista de arquivos de saída gerados pelo crawl.
        
        Args:
            output_prefix: Prefixo dos arquivos.
        
        Returns:
            Lista com caminhos dos arquivos gerados.
        """
        output_files = []
        for file_path in self.output_dir.glob("*.csv"):
            output_files.append(str(file_path))
        
        return output_files
    
    def get_crawl_history(self) -> List[Dict[str, Any]]:
        """
        Retorna histórico de crawls realizados.
        
        Returns:
            Lista com informações dos crawls anteriores.
        """
        history = []
        
        # Procura por arquivos de resultado no diretório
        for csv_file in self.output_dir.glob("*.csv"):
            try:
                stat = csv_file.stat()
                history.append({
                    'file': str(csv_file),
                    'created_at': stat.st_ctime,
                    'size': stat.st_size
                })
            except OSError:
                continue
        
        # Ordena por data de criação (mais recente primeiro)
        history.sort(key=lambda x: x['created_at'], reverse=True)
        
        return history
    
    def cleanup_old_files(self, days_old: int = 7) -> int:
        """
        Remove arquivos de crawl antigos.
        
        Args:
            days_old: Idade em dias para considerar arquivos como antigos.
        
        Returns:
            Número de arquivos removidos.
        """
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        removed_count = 0
        
        for file_path in self.output_dir.glob("*.csv"):
            try:
                if file_path.stat().st_ctime < cutoff_time:
                    file_path.unlink()
                    removed_count += 1
            except OSError:
                continue
        
        logger.info(f"Removidos {removed_count} arquivos antigos de crawl")
        return removed_count


class CrawlerManager:
    """
    Gerenciador centralizado para operações de crawling.
    
    Fornece interface simplificada para executar crawls e gerenciar resultados.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de crawler."""
        self.crawler = ScreamingFrogCrawler()
        self.logger = logging.getLogger(__name__)
    
    def execute_full_audit_crawl(self, url: str) -> Dict[str, Any]:
        """
        Executa um crawl completo otimizado para auditoria de SEO.
        
        Args:
            url: URL do website para auditar.
        
        Returns:
            Resultados do crawl formatados para auditoria.
        
        Raises:
            ScreamingFrogError: Se houver erro durante o crawl.
        """
        # Configuração otimizada para auditoria de SEO
        audit_config = {
            'max_crawl_depth': 5,
            'max_urls': 2000,
            'timeout': 600,  # 10 minutos
            'respect_robots_txt': True,
            'follow_redirects': True
        }
        
        try:
            self.logger.info(f"Iniciando auditoria completa de {url}")
            
            # Executa o crawl
            crawl_results = self.crawler.crawl_website(url, audit_config)
            
            # Processa resultados para auditoria
            audit_data = self._format_for_audit(crawl_results)
            
            self.logger.info("Auditoria de crawl concluída com sucesso")
            
            return audit_data
            
        except Exception as e:
            self.logger.error(f"Erro na auditoria de crawl: {str(e)}")
            raise
    
    def _format_for_audit(self, crawl_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formata os resultados do crawl para auditoria de SEO.
        
        Args:
            crawl_results: Resultados brutos do crawl.
        
        Returns:
            Dados formatados para auditoria.
        """
        results = crawl_results['results']
        summary = results['summary']
        
        # Identifica problemas técnicos
        technical_issues = []
        
        # Verifica códigos de erro
        error_codes = {k: v for k, v in summary['response_codes_count'].items() 
                      if k.startswith(('4', '5'))}
        if error_codes:
            technical_issues.append({
                'type': 'response_errors',
                'description': 'Páginas com códigos de erro HTTP',
                'count': sum(error_codes.values()),
                'details': error_codes
            })
        
        # Verifica problemas de conteúdo
        if summary['pages_without_title'] > 0:
            technical_issues.append({
                'type': 'missing_titles',
                'description': 'Páginas sem título',
                'count': summary['pages_without_title']
            })
        
        if summary['pages_without_meta_description'] > 0:
            technical_issues.append({
                'type': 'missing_meta_descriptions',
                'description': 'Páginas sem meta description',
                'count': summary['pages_without_meta_description']
            })
        
        if summary['pages_without_h1'] > 0:
            technical_issues.append({
                'type': 'missing_h1',
                'description': 'Páginas sem tag H1',
                'count': summary['pages_without_h1']
            })
        
        return {
            'url': crawl_results['url'],
            'crawl_timestamp': crawl_results['timestamp'],
            'summary': summary,
            'technical_issues': technical_issues,
            'raw_data': results,
            'output_files': crawl_results['output_files']
        }
    
    def is_available(self) -> bool:
        """
        Verifica se o Screaming Frog está disponível para uso.
        
        Returns:
            True se disponível, False caso contrário.
        """
        try:
            return self.crawler.validate_executable()
        except ScreamingFrogError:
            return False
    
    def crawl_website(self, url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa crawl de um website usando o Screaming Frog.
        
        Args:
            url: URL do website para fazer crawl
            config: Configurações específicas para o crawl
            
        Returns:
            Dicionário com os resultados do crawl
        """
        try:
            return self.execute_full_audit_crawl(url)
        except Exception as e:
            logger.error(f"Erro no crawl do website: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'timestamp': time.time()
            }