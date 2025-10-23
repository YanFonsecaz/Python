"""
Configuração do Gunicorn para o Sistema de Auditoria SEO em produção.
"""
import os
import multiprocessing
from config.production import ProductionConfig

# Configurações básicas
bind = f"{ProductionConfig.HOST}:{ProductionConfig.PORT}"
workers = ProductionConfig.WORKERS
worker_class = ProductionConfig.WORKER_CLASS
worker_connections = ProductionConfig.WORKER_CONNECTIONS

# Configurações de performance
max_requests = ProductionConfig.MAX_REQUESTS
max_requests_jitter = ProductionConfig.MAX_REQUESTS_JITTER
timeout = ProductionConfig.TIMEOUT
keepalive = ProductionConfig.KEEPALIVE
preload_app = True

# Configurações de logging
accesslog = os.path.join(ProductionConfig.LOG_FILE_PATH, 'access.log')
errorlog = os.path.join(ProductionConfig.LOG_FILE_PATH, 'error.log')
loglevel = ProductionConfig.LOG_LEVEL.lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de processo
capture_output = True
enable_stdio_inheritance = True
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = ProductionConfig.TEMP_FOLDER

# Configurações de SSL (se necessário)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Hooks do Gunicorn
def on_starting(server):
    """
    Hook executado quando o servidor está iniciando.
    """
    server.log.info("=== Sistema de Auditoria SEO ===")
    server.log.info("Iniciando servidor Gunicorn...")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Worker class: {worker_class}")
    server.log.info(f"Bind: {bind}")


def on_reload(server):
    """
    Hook executado quando o servidor é recarregado.
    """
    server.log.info("Recarregando servidor...")


def worker_int(worker):
    """
    Hook executado quando um worker recebe SIGINT ou SIGQUIT.
    """
    worker.log.info(f"Worker {worker.pid} interrompido")


def pre_fork(server, worker):
    """
    Hook executado antes de fazer fork de um worker.
    """
    server.log.info(f"Iniciando worker {worker.pid}")


def post_fork(server, worker):
    """
    Hook executado após fazer fork de um worker.
    """
    server.log.info(f"Worker {worker.pid} iniciado")


def post_worker_init(worker):
    """
    Hook executado após a inicialização de um worker.
    """
    worker.log.info(f"Worker {worker.pid} inicializado")


def worker_abort(worker):
    """
    Hook executado quando um worker é abortado.
    """
    worker.log.error(f"Worker {worker.pid} abortado")


def pre_exec(server):
    """
    Hook executado antes de executar um novo processo.
    """
    server.log.info("Executando novo processo...")


def when_ready(server):
    """
    Hook executado quando o servidor está pronto para aceitar conexões.
    """
    server.log.info("Servidor pronto para aceitar conexões")
    server.log.info(f"Listening on: {bind}")


def pre_request(worker, req):
    """
    Hook executado antes de processar uma requisição.
    """
    # Log apenas para requisições importantes (não health checks)
    if not req.path.startswith('/health'):
        worker.log.debug(f"{req.method} {req.path}")


def post_request(worker, req, environ, resp):
    """
    Hook executado após processar uma requisição.
    """
    # Log apenas para erros ou requisições importantes
    if resp.status_code >= 400 or not req.path.startswith('/health'):
        worker.log.info(f"{req.method} {req.path} - {resp.status_code}")


def child_exit(server, worker):
    """
    Hook executado quando um worker child sai.
    """
    server.log.info(f"Worker {worker.pid} saiu")


def worker_exit(server, worker):
    """
    Hook executado quando um worker sai.
    """
    server.log.info(f"Worker {worker.pid} finalizou")


def nworkers_changed(server, new_value, old_value):
    """
    Hook executado quando o número de workers muda.
    """
    server.log.info(f"Número de workers alterado de {old_value} para {new_value}")


def on_exit(server):
    """
    Hook executado quando o servidor está saindo.
    """
    server.log.info("Finalizando servidor Gunicorn...")
    server.log.info("Sistema de Auditoria SEO finalizado")


# Configurações específicas para diferentes ambientes
if os.getenv('ENVIRONMENT') == 'development':
    # Configurações para desenvolvimento
    workers = 1
    reload = True
    timeout = 0
    loglevel = 'debug'
elif os.getenv('ENVIRONMENT') == 'staging':
    # Configurações para staging
    workers = max(2, multiprocessing.cpu_count() // 2)
    timeout = 120
elif os.getenv('ENVIRONMENT') == 'production':
    # Configurações para produção (já definidas acima)
    pass

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de SSL/TLS (descomente se necessário)
# ssl_version = 2  # TLS
# ciphers = 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'
# do_handshake_on_connect = False
# suppress_ragged_eofs = True