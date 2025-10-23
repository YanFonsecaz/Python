"""
Configurações específicas para ambiente de produção.
"""
import os
from typing import Dict, Any


class ProductionConfig:
    """
    Configurações para ambiente de produção do Sistema de Auditoria SEO.
    """
    
    def __init__(self):
        """Inicializa a configuração de produção."""
        # Configurações básicas do Flask
        self.ENVIRONMENT = 'production'
        self.SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
        self.FLASK_SECRET_KEY = self._get_or_generate_secret_key()
        self.FLASK_DEBUG = self._parse_boolean(os.getenv('FLASK_DEBUG', 'false'))
        self.DEBUG = False
        self.TESTING = False
        self.FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
        self.FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
        
        # Configurações de banco de dados
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/audit_history.db')
        self.DATABASE_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', '10'))
        self.DATABASE_TIMEOUT = int(os.getenv('DATABASE_TIMEOUT', '30'))
        
        # Configurações de cache (valores ajustados para os testes)
        self.CACHE_MEMORY_SIZE = int(os.getenv('CACHE_MEMORY_SIZE', '200'))  # MB
        self.CACHE_DISK_SIZE = int(os.getenv('CACHE_DISK_SIZE', '2000'))    # MB
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))                # segundos
        self.CACHE_DISK_PATH = os.getenv('CACHE_DISK_PATH', '/app/cache')
        
        # Configurações de processamento assíncrono
        self.ASYNC_MAX_WORKERS = int(os.getenv('ASYNC_MAX_WORKERS', '4'))
        self.ASYNC_QUEUE_SIZE = int(os.getenv('ASYNC_QUEUE_SIZE', '100'))
        self.ASYNC_ENABLE_RETRY = self._parse_boolean(os.getenv('ASYNC_ENABLE_RETRY', 'true'))
        self.ASYNC_MAX_RETRIES = int(os.getenv('ASYNC_MAX_RETRIES', '3'))
        
        # Configurações de logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', '/app/logs')
        self.LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))    # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        self.ENABLE_JSON_LOGGING = self._parse_boolean(os.getenv('ENABLE_JSON_LOGGING', 'true'))
        
        # Configurações de segurança
        self.RATE_LIMIT_STORAGE_URL = os.getenv('RATE_LIMIT_STORAGE_URL', 'memory://')
        self.RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
        self.IP_WHITELIST = os.getenv('IP_WHITELIST', '127.0.0.1,::1,10.0.0.1').split(',') if os.getenv('IP_WHITELIST') else ['127.0.0.1', '::1', '10.0.0.1']
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',') if os.getenv('CORS_ORIGINS') and os.getenv('CORS_ORIGINS') != '*' else ['*']
        self.ENABLE_HTTPS_REDIRECT = self._parse_boolean(os.getenv('ENABLE_HTTPS_REDIRECT', 'true'))
        self.ENABLE_HSTS = self._parse_boolean(os.getenv('ENABLE_HSTS', 'true'))
        self.ENABLE_CSP = self._parse_boolean(os.getenv('ENABLE_CSP', 'true'))
        
        # Configurações de APIs externas
        self.PAGESPEED_API_KEY = os.getenv('PAGESPEED_API_KEY')
        self.SEMRUSH_API_KEY = os.getenv('SEMRUSH_API_KEY')
        self.AHREFS_API_KEY = os.getenv('AHREFS_API_KEY')
        self.SCREAMING_FROG_PATH = os.getenv('SCREAMING_FROG_PATH', '/opt/screamingfrog/ScreamingFrogSEOSpider')
        
        # Configurações do servidor Gunicorn
        self.HOST = os.getenv('FLASK_HOST', '0.0.0.0')
        self.PORT = int(os.getenv('FLASK_PORT', '5000'))
        self.GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', '4'))
        self.GUNICORN_WORKER_CLASS = os.getenv('GUNICORN_WORKER_CLASS', 'sync')
        self.GUNICORN_WORKER_CONNECTIONS = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', '1000'))
        self.GUNICORN_MAX_REQUESTS = int(os.getenv('GUNICORN_MAX_REQUESTS', '1000'))
        self.GUNICORN_MAX_REQUESTS_JITTER = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '100'))
        self.GUNICORN_TIMEOUT = int(os.getenv('GUNICORN_TIMEOUT', '300'))
        self.GUNICORN_KEEPALIVE = int(os.getenv('GUNICORN_KEEPALIVE', '5'))
        
        # Configurações de monitoramento
        self.ENABLE_METRICS = self._parse_boolean(os.getenv('ENABLE_METRICS', 'true'))
        self.METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))
        self.HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
        
        # Configurações de upload
        self.MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
        self.UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')
        self.ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'csv,xlsx,xls').split(',') if os.getenv('ALLOWED_EXTENSIONS') else ['csv', 'xlsx', 'xls']
        self.MAX_URLS_PER_AUDIT = int(os.getenv('MAX_URLS_PER_AUDIT', '100'))
        
        # Configurações de relatórios
        self.REPORTS_FOLDER = os.getenv('REPORTS_FOLDER', '/app/reports')
        self.TEMP_FOLDER = os.getenv('TEMP_FOLDER', '/app/temp')
    
    def _parse_boolean(self, value: str) -> bool:
        """
        Converte string para booleano de forma robusta.
        
        Args:
            value: Valor string a ser convertido.
            
        Returns:
            Valor booleano correspondente.
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        return bool(value)
    
    def __repr__(self) -> str:
        """
        Representação da configuração sem expor dados sensíveis.
        
        Returns:
            String representando a configuração de forma segura.
        """
        sensitive_keys = ['SECRET_KEY', 'FLASK_SECRET_KEY', 'PAGESPEED_API_KEY', 'SEMRUSH_API_KEY', 'AHREFS_API_KEY']
        safe_dict = {}
        
        for key, value in self.__dict__.items():
            if any(sensitive in key.upper() for sensitive in sensitive_keys):
                safe_dict[key] = '***HIDDEN***'
            else:
                safe_dict[key] = value
                
        return f"ProductionConfig({safe_dict})"
    
    def _get_or_generate_secret_key(self) -> str:
        """
        Obtém ou gera uma chave secreta para o Flask.
        
        Returns:
            Chave secreta válida.
        """
        secret_key = os.getenv('FLASK_SECRET_KEY')
        if secret_key:
            return secret_key
        
        # Gerar chave secreta automaticamente se não estiver definida
        import secrets
        return secrets.token_urlsafe(32)
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        Valida as configurações de produção.
        
        Returns:
            Dicionário com resultado da validação.
        """
        config = cls()
        issues = []
        warnings = []
        
        # Validações críticas
        flask_secret_from_env = os.getenv('FLASK_SECRET_KEY')
        if not flask_secret_from_env:
            issues.append("FLASK_SECRET_KEY não definida")
        elif len(flask_secret_from_env) < 32:
            issues.append("FLASK_SECRET_KEY muito fraca (mínimo 32 caracteres)")
        
        # Validação do banco de dados
        if not os.path.dirname(config.DATABASE_PATH):
            issues.append("Caminho do banco de dados inválido")
        
        # Validações de aviso
        if not config.PAGESPEED_API_KEY:
            warnings.append("PAGESPEED_API_KEY não configurada")
        
        if not config.SEMRUSH_API_KEY:
            warnings.append("SEMRUSH_API_KEY não configurada")
        
        if not config.AHREFS_API_KEY:
            warnings.append("AHREFS_API_KEY não configurada")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'config_summary': {
                'workers': config.GUNICORN_WORKERS,
                'cache_memory': f"{config.CACHE_MEMORY_SIZE}MB",
                'cache_disk': f"{config.CACHE_DISK_SIZE}MB",
                'async_workers': config.ASYNC_MAX_WORKERS,
                'log_level': config.LOG_LEVEL,
                'database_pool': config.DATABASE_POOL_SIZE
            }
        }
    
    @classmethod
    def get_gunicorn_config(cls) -> Dict[str, Any]:
        """
        Retorna configurações específicas para o Gunicorn.
        
        Returns:
            Dicionário com configurações do Gunicorn.
        """
        config = cls()
        return {
            'bind': f"{config.HOST}:{config.PORT}",
            'workers': config.GUNICORN_WORKERS,
            'worker_class': config.GUNICORN_WORKER_CLASS,
            'worker_connections': config.GUNICORN_WORKER_CONNECTIONS,
            'max_requests': config.GUNICORN_MAX_REQUESTS,
            'max_requests_jitter': config.GUNICORN_MAX_REQUESTS_JITTER,
            'timeout': config.GUNICORN_TIMEOUT,
            'keepalive': config.GUNICORN_KEEPALIVE,
            'preload_app': True,
            'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
            'accesslog': '/app/logs/access.log',
            'errorlog': '/app/logs/error.log',
            'loglevel': config.LOG_LEVEL.lower(),
            'capture_output': True,
            'enable_stdio_inheritance': True
        }
    
    @classmethod
    def get_environment_template(cls) -> str:
        """
        Retorna um template de arquivo .env para produção.
        
        Returns:
            String com template do arquivo .env.
        """
        return """# Configurações de Produção - Sistema de Auditoria SEO

# Flask
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# Banco de Dados
DATABASE_PATH=/app/data/audit_history.db
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30

# Cache
CACHE_MEMORY_SIZE=100
CACHE_DISK_SIZE=1000
CACHE_TTL=3600
CACHE_DISK_PATH=/app/cache

# Processamento Assíncrono
ASYNC_MAX_WORKERS=4
ASYNC_QUEUE_SIZE=100
ASYNC_ENABLE_RETRY=true
ASYNC_MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=/app/logs
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
ENABLE_JSON_LOGGING=true

# Segurança
RATE_LIMIT_STORAGE_URL=memory://
RATE_LIMIT_DEFAULT=100 per hour
IP_WHITELIST=127.0.0.1,::1,10.0.0.1
CORS_ORIGINS=*
ENABLE_HTTPS_REDIRECT=true
ENABLE_HSTS=true
ENABLE_CSP=true

# APIs Externas
PAGESPEED_API_KEY=your-pagespeed-api-key
SEMRUSH_API_KEY=your-semrush-api-key
AHREFS_API_KEY=your-ahrefs-api-key
SCREAMING_FROG_PATH=/opt/screamingfrog/ScreamingFrogSEOSpider

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=sync
GUNICORN_WORKER_CONNECTIONS=1000
GUNICORN_MAX_REQUESTS=1000
GUNICORN_MAX_REQUESTS_JITTER=100
GUNICORN_TIMEOUT=300
GUNICORN_KEEPALIVE=5

# Monitoramento
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/app/uploads

# Relatórios
REPORTS_FOLDER=/app/reports
TEMP_FOLDER=/app/temp
"""

    @classmethod
    def generate_env_template(cls) -> str:
        """
        Alias para get_environment_template para compatibilidade com testes.
        
        Returns:
            String com template do arquivo .env.
        """
        return cls.get_environment_template()


def create_production_directories():
    """
    Cria os diretórios necessários para produção.
    
    Returns:
        Dicionário com resultado da criação.
    """
    config = ProductionConfig()
    directories = [
        config.LOG_FILE_PATH,
        config.CACHE_DISK_PATH,
        config.UPLOAD_FOLDER,
        config.REPORTS_FOLDER,
        config.TEMP_FOLDER,
        os.path.dirname(config.DATABASE_PATH)
    ]
    
    created = []
    errors = []
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                created.append(directory)
        except Exception as e:
            errors.append(f"Erro ao criar {directory}: {str(e)}")
    
    return {
        'created': created,
        'errors': errors
    }


if __name__ == '__main__':
    # Validação das configurações
    validation = ProductionConfig.validate_config()
    
    print("=== Validação de Configurações de Produção ===")
    print(f"Status: {'✓ VÁLIDO' if validation['valid'] else '✗ INVÁLIDO'}")
    
    if validation['issues']:
        print("\n🚨 Problemas Críticos:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    if validation['warnings']:
        print("\n⚠️  Avisos:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    print("\n📊 Resumo da Configuração:")
    for key, value in validation['config_summary'].items():
        print(f"  {key}: {value}")
    
    # Criação de diretórios
    print("\n📁 Criando Diretórios...")
    result = create_production_directories()
    
    if result['created']:
        print("Diretórios criados:")
        for directory in result['created']:
            print(f"  ✓ {directory}")
    
    if result['errors']:
        print("Erros ao criar diretórios:")
        for error in result['errors']:
            print(f"  ✗ {error}")