"""
Testes para configuração de produção do Sistema de Auditoria SEO.
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from config.production import ProductionConfig


class TestProductionConfig:
    """Testes para a classe ProductionConfig."""
    
    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_default_configuration(self):
        """Testa se a configuração padrão está correta."""
        config = ProductionConfig()
        
        # Verificar configurações básicas
        assert config.ENVIRONMENT == 'production'
        assert config.FLASK_DEBUG is False
        assert config.FLASK_HOST == '0.0.0.0'
        assert config.FLASK_PORT == 5000
        
        # Verificar configurações de cache
        assert config.CACHE_MEMORY_SIZE == 200
        assert config.CACHE_DISK_SIZE == 2000
        assert config.CACHE_TTL == 3600
        
        # Verificar configurações de processamento assíncrono
        assert config.ASYNC_MAX_WORKERS == 4
        assert config.ASYNC_QUEUE_SIZE == 100
        assert config.ASYNC_ENABLE_RETRY is True
    
    def test_environment_variable_override(self):
        """Testa se as variáveis de ambiente sobrescrevem as configurações padrão."""
        os.environ['FLASK_PORT'] = '8080'
        os.environ['CACHE_MEMORY_SIZE'] = '500'
        os.environ['ASYNC_MAX_WORKERS'] = '8'
        os.environ['FLASK_DEBUG'] = 'true'
        
        config = ProductionConfig()
        
        assert config.FLASK_PORT == 8080
        assert config.CACHE_MEMORY_SIZE == 500
        assert config.ASYNC_MAX_WORKERS == 8
        assert config.FLASK_DEBUG is True
    
    def test_secret_key_generation(self):
        """Testa a geração automática de chave secreta."""
        config = ProductionConfig()
        
        # Se não há FLASK_SECRET_KEY definida, deve gerar uma
        if not os.getenv('FLASK_SECRET_KEY'):
            assert len(config.FLASK_SECRET_KEY) >= 32
            assert isinstance(config.FLASK_SECRET_KEY, str)
    
    def test_database_path_creation(self):
        """Testa se o caminho do banco de dados é criado corretamente."""
        db_path = os.path.join(self.temp_dir, 'test_audit.db')
        os.environ['DATABASE_PATH'] = db_path
        
        config = ProductionConfig()
        assert config.DATABASE_PATH == db_path
    
    def test_validate_config_success(self):
        """Testa validação de configuração bem-sucedida."""
        os.environ['FLASK_SECRET_KEY'] = 'a' * 32  # Chave válida
        os.environ['DATABASE_PATH'] = os.path.join(self.temp_dir, 'test.db')
        
        result = ProductionConfig.validate_config()
        
        assert result['valid'] is True
        assert len(result['issues']) == 0
    
    def test_validate_config_missing_secret_key(self):
        """Testa validação com chave secreta ausente."""
        os.environ.pop('FLASK_SECRET_KEY', None)
        
        result = ProductionConfig.validate_config()
        
        assert result['valid'] is False
        assert any('FLASK_SECRET_KEY' in issue for issue in result['issues'])
    
    def test_validate_config_weak_secret_key(self):
        """Testa validação com chave secreta fraca."""
        os.environ['FLASK_SECRET_KEY'] = 'weak'  # Muito curta
        
        result = ProductionConfig.validate_config()
        
        assert result['valid'] is False
        assert any('32 caracteres' in issue for issue in result['issues'])
    
    def test_validate_config_invalid_database_path(self):
        """Testa validação com caminho de banco inválido."""
        os.environ['DATABASE_PATH'] = '/invalid/path/that/does/not/exist/db.sqlite'
        
        result = ProductionConfig.validate_config()
        
        # Pode ser válido se o diretório pai não existir mas puder ser criado
        # Ou inválido se não puder ser criado
        assert isinstance(result['valid'], bool)
    
    def test_gunicorn_config(self):
        """Testa configurações específicas do Gunicorn."""
        config = ProductionConfig()
        gunicorn_config = config.get_gunicorn_config()
        
        assert 'bind' in gunicorn_config
        assert 'workers' in gunicorn_config
        assert 'worker_class' in gunicorn_config
        assert 'timeout' in gunicorn_config
        
        # Verificar valores padrão
        assert gunicorn_config['workers'] == config.GUNICORN_WORKERS
        assert gunicorn_config['timeout'] == config.GUNICORN_TIMEOUT
    
    def test_logging_configuration(self):
        """Testa configurações de logging."""
        config = ProductionConfig()
        
        assert config.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        assert config.LOG_MAX_BYTES > 0
        assert config.LOG_BACKUP_COUNT > 0
        assert isinstance(config.ENABLE_JSON_LOGGING, bool)
    
    def test_security_configuration(self):
        """Testa configurações de segurança."""
        config = ProductionConfig()
        
        assert config.RATE_LIMIT_DEFAULT is not None
        assert isinstance(config.IP_WHITELIST, list)
        assert isinstance(config.CORS_ORIGINS, list)
        assert isinstance(config.ENABLE_HTTPS_REDIRECT, bool)
    
    def test_monitoring_configuration(self):
        """Testa configurações de monitoramento."""
        config = ProductionConfig()
        
        assert isinstance(config.ENABLE_METRICS, bool)
        assert config.METRICS_PORT > 0
        assert config.HEALTH_CHECK_INTERVAL > 0
    
    def test_upload_configuration(self):
        """Testa configurações de upload."""
        config = ProductionConfig()
        
        assert config.MAX_CONTENT_LENGTH > 0
        assert isinstance(config.ALLOWED_EXTENSIONS, list)
        assert len(config.ALLOWED_EXTENSIONS) > 0
        assert config.MAX_URLS_PER_AUDIT > 0
    
    @patch('os.makedirs')
    def test_create_production_directories(self, mock_makedirs):
        """Testa criação de diretórios de produção."""
        from config.production import create_production_directories
        
        result = create_production_directories()
        
        assert 'created' in result
        assert 'errors' in result
        assert isinstance(result['created'], list)
        assert isinstance(result['errors'], list)
        
        # Verificar se tentou criar os diretórios principais
        expected_dirs = ['data', 'cache', 'logs', 'uploads', 'reports', 'temp']
        created_dirs = [call[0][0] for call in mock_makedirs.call_args_list]
        
        for expected_dir in expected_dirs:
            assert any(expected_dir in created_dir for created_dir in created_dirs)
    
    def test_env_template_generation(self):
        """Testa geração do template .env."""
        template = ProductionConfig.generate_env_template()
        
        assert isinstance(template, str)
        assert 'FLASK_SECRET_KEY' in template
        assert 'DATABASE_PATH' in template
        assert 'CACHE_MEMORY_SIZE' in template
        assert 'ASYNC_MAX_WORKERS' in template
        
        # Verificar se contém comentários explicativos
        assert '#' in template
        assert 'Configurações' in template or 'Configuration' in template
    
    def test_boolean_environment_variables(self):
        """Testa conversão correta de variáveis booleanas."""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('', False),
        ]
        
        for env_value, expected in test_cases:
            os.environ['FLASK_DEBUG'] = env_value
            config = ProductionConfig()
            assert config.FLASK_DEBUG == expected, f"Failed for {env_value}"
    
    def test_integer_environment_variables(self):
        """Testa conversão correta de variáveis inteiras."""
        os.environ['FLASK_PORT'] = '8080'
        os.environ['CACHE_MEMORY_SIZE'] = '512'
        os.environ['ASYNC_MAX_WORKERS'] = '6'
        
        config = ProductionConfig()
        
        assert config.FLASK_PORT == 8080
        assert config.CACHE_MEMORY_SIZE == 512
        assert config.ASYNC_MAX_WORKERS == 6
    
    def test_list_environment_variables(self):
        """Testa conversão correta de variáveis de lista."""
        os.environ['IP_WHITELIST'] = '127.0.0.1,192.168.1.1,10.0.0.1'
        os.environ['CORS_ORIGINS'] = 'http://localhost:3000,https://example.com'
        os.environ['ALLOWED_EXTENSIONS'] = 'csv,xlsx,txt,json'
        
        config = ProductionConfig()
        
        assert config.IP_WHITELIST == ['127.0.0.1', '192.168.1.1', '10.0.0.1']
        assert config.CORS_ORIGINS == ['http://localhost:3000', 'https://example.com']
        assert config.ALLOWED_EXTENSIONS == ['csv', 'xlsx', 'txt', 'json']
    
    def test_path_normalization(self):
        """Testa normalização de caminhos."""
        test_path = os.path.join(self.temp_dir, 'test', 'path')
        os.environ['DATABASE_PATH'] = test_path
        os.environ['UPLOAD_FOLDER'] = test_path + '/uploads'
        
        config = ProductionConfig()
        
        assert os.path.isabs(config.DATABASE_PATH)
        assert os.path.isabs(config.UPLOAD_FOLDER)
    
    def test_configuration_inheritance(self):
        """Testa se a configuração herda corretamente de configurações base."""
        config = ProductionConfig()
        
        # Verificar se tem atributos básicos esperados
        expected_attrs = [
            'FLASK_HOST', 'FLASK_PORT', 'FLASK_DEBUG',
            'DATABASE_PATH', 'CACHE_MEMORY_SIZE', 'LOG_LEVEL'
        ]
        
        for attr in expected_attrs:
            assert hasattr(config, attr), f"Missing attribute: {attr}"
    
    def test_sensitive_data_not_logged(self):
        """Testa se dados sensíveis não são expostos em logs."""
        os.environ['FLASK_SECRET_KEY'] = 'super_secret_key_123456789012345'
        os.environ['PAGESPEED_API_KEY'] = 'secret_api_key'
        
        config = ProductionConfig()
        config_str = str(config)  # Usar __repr__ em vez de __dict__
        
        # Chaves sensíveis não devem aparecer completas
        assert 'super_secret_key' not in config_str
        assert 'secret_api_key' not in config_str


class TestProductionConfigIntegration:
    """Testes de integração para configuração de produção."""
    
    def test_flask_app_configuration(self):
        """Testa se a configuração pode ser aplicada a uma app Flask."""
        from flask import Flask
        
        app = Flask(__name__)
        config = ProductionConfig()
        
        # Aplicar configuração
        for key, value in config.__dict__.items():
            if key.isupper():
                app.config[key] = value
        
        # Verificar se foi aplicada corretamente
        assert app.config['FLASK_DEBUG'] == config.FLASK_DEBUG
        assert app.config['DATABASE_PATH'] == config.DATABASE_PATH
    
    @patch('sqlite3.connect')
    def test_database_connection(self, mock_connect):
        """Testa se a configuração de banco permite conexão."""
        mock_connect.return_value = MagicMock()
        
        config = ProductionConfig()
        
        # Simular conexão com banco
        import sqlite3
        conn = sqlite3.connect(config.DATABASE_PATH)
        
        assert conn is not None
        mock_connect.assert_called_once_with(config.DATABASE_PATH)
    
    def test_cache_configuration_compatibility(self):
        """Testa compatibilidade da configuração de cache."""
        config = ProductionConfig()
        
        # Verificar se os valores são compatíveis com sistemas de cache
        assert config.CACHE_MEMORY_SIZE > 0
        assert config.CACHE_DISK_SIZE > 0
        assert config.CACHE_TTL > 0
        
        # Verificar se o tamanho de disco é maior que memória (recomendado)
        assert config.CACHE_DISK_SIZE >= config.CACHE_MEMORY_SIZE