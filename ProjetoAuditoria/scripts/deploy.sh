#!/bin/bash

# Script de Deploy - Sistema de Auditoria SEO
# Uso: ./scripts/deploy.sh [ambiente] [versao]

set -e

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
DOCKER_IMAGE="seo-audit-system"
CONTAINER_NAME="seo-audit-api"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar pré-requisitos
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker não está instalado"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose não está instalado"
        exit 1
    fi
    
    # Verificar se está no diretório correto
    if [[ ! -f "$PROJECT_DIR/app/main.py" ]]; then
        log_error "Execute este script a partir do diretório raiz do projeto"
        exit 1
    fi
    
    log_success "Pré-requisitos verificados"
}

# Validar configurações
validate_config() {
    log_info "Validando configurações..."
    
    # Verificar arquivo de ambiente
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        if [[ -f "$PROJECT_DIR/.env.production" ]]; then
            log_warning "Arquivo .env não encontrado. Copiando .env.production..."
            cp "$PROJECT_DIR/.env.production" "$PROJECT_DIR/.env"
        else
            log_error "Arquivo .env não encontrado. Crie um baseado em .env.production"
            exit 1
        fi
    fi
    
    # Verificar variáveis críticas
    source "$PROJECT_DIR/.env"
    
    if [[ -z "$FLASK_SECRET_KEY" || "$FLASK_SECRET_KEY" == "sua_chave_secreta_super_forte_aqui_min_32_chars" ]]; then
        log_error "FLASK_SECRET_KEY não configurada ou usando valor padrão"
        exit 1
    fi
    
    if [[ ${#FLASK_SECRET_KEY} -lt 32 ]]; then
        log_error "FLASK_SECRET_KEY deve ter pelo menos 32 caracteres"
        exit 1
    fi
    
    log_success "Configurações validadas"
}

# Criar diretórios necessários
create_directories() {
    log_info "Criando diretórios necessários..."
    
    local dirs=("data" "cache" "logs" "uploads" "reports" "temp" "monitoring/prometheus" "monitoring/grafana/dashboards" "monitoring/grafana/datasources" "nginx")
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$PROJECT_DIR/$dir"
        log_info "Diretório criado: $dir"
    done
    
    # Configurar permissões
    chmod 755 "$PROJECT_DIR/data" "$PROJECT_DIR/cache" "$PROJECT_DIR/logs"
    chmod 777 "$PROJECT_DIR/uploads" "$PROJECT_DIR/reports" "$PROJECT_DIR/temp"
    
    log_success "Diretórios criados"
}

# Backup dos dados existentes
backup_data() {
    if [[ -d "$PROJECT_DIR/data" ]] && [[ "$(ls -A $PROJECT_DIR/data)" ]]; then
        log_info "Fazendo backup dos dados existentes..."
        
        local backup_dir="$PROJECT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        cp -r "$PROJECT_DIR/data"/* "$backup_dir/"
        
        log_success "Backup criado em: $backup_dir"
    fi
}

# Build da imagem Docker
build_image() {
    log_info "Construindo imagem Docker..."
    
    cd "$PROJECT_DIR"
    
    # Build da imagem
    docker build -f Dockerfile.prod -t "$DOCKER_IMAGE:$VERSION" .
    docker tag "$DOCKER_IMAGE:$VERSION" "$DOCKER_IMAGE:latest"
    
    log_success "Imagem Docker construída: $DOCKER_IMAGE:$VERSION"
}

# Parar containers existentes
stop_containers() {
    log_info "Parando containers existentes..."
    
    if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
        docker stop "$CONTAINER_NAME" || true
        docker rm "$CONTAINER_NAME" || true
        log_info "Container $CONTAINER_NAME parado e removido"
    fi
    
    # Parar via docker-compose se existir
    if [[ -f "$PROJECT_DIR/docker-compose.prod.yml" ]]; then
        docker-compose -f docker-compose.prod.yml down || true
    fi
    
    log_success "Containers parados"
}

# Iniciar aplicação
start_application() {
    log_info "Iniciando aplicação..."
    
    cd "$PROJECT_DIR"
    
    # Usar docker-compose se disponível
    if [[ -f "docker-compose.prod.yml" ]]; then
        docker-compose -f docker-compose.prod.yml up -d
        log_success "Aplicação iniciada via Docker Compose"
    else
        # Iniciar container individual
        docker run -d \
            --name "$CONTAINER_NAME" \
            --restart unless-stopped \
            -p 5000:5000 \
            -p 9090:9090 \
            --env-file .env \
            -v "$PROJECT_DIR/data:/app/data" \
            -v "$PROJECT_DIR/cache:/app/cache" \
            -v "$PROJECT_DIR/logs:/app/logs" \
            -v "$PROJECT_DIR/uploads:/app/uploads" \
            -v "$PROJECT_DIR/reports:/app/reports" \
            -v "$PROJECT_DIR/temp:/app/temp" \
            "$DOCKER_IMAGE:$VERSION"
        
        log_success "Aplicação iniciada via Docker"
    fi
}

# Verificar saúde da aplicação
health_check() {
    log_info "Verificando saúde da aplicação..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s http://localhost:5000/health > /dev/null; then
            log_success "Aplicação está saudável!"
            return 0
        fi
        
        log_info "Tentativa $attempt/$max_attempts - Aguardando aplicação..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Aplicação não respondeu ao health check"
    return 1
}

# Mostrar status
show_status() {
    log_info "Status da aplicação:"
    echo
    
    # Status dos containers
    echo "=== Containers ==="
    docker ps --filter "name=seo-audit" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    
    # Logs recentes
    echo "=== Logs Recentes ==="
    docker logs --tail 20 "$CONTAINER_NAME" 2>/dev/null || echo "Container não encontrado"
    echo
    
    # URLs de acesso
    echo "=== URLs de Acesso ==="
    echo "API: http://localhost:5000"
    echo "Health Check: http://localhost:5000/health"
    echo "Métricas: http://localhost:9090/metrics"
    echo "Grafana: http://localhost:3000 (se habilitado)"
    echo
}

# Limpeza
cleanup() {
    log_info "Limpando recursos não utilizados..."
    
    # Remover imagens antigas
    docker image prune -f
    
    # Remover volumes não utilizados
    docker volume prune -f
    
    log_success "Limpeza concluída"
}

# Função principal
main() {
    echo "=== Deploy do Sistema de Auditoria SEO ==="
    echo "Ambiente: $ENVIRONMENT"
    echo "Versão: $VERSION"
    echo "=========================================="
    echo
    
    check_prerequisites
    validate_config
    create_directories
    backup_data
    build_image
    stop_containers
    start_application
    
    if health_check; then
        show_status
        cleanup
        
        echo
        log_success "Deploy concluído com sucesso!"
        log_info "A aplicação está rodando em: http://localhost:5000"
    else
        log_error "Deploy falhou - aplicação não está saudável"
        
        echo
        echo "=== Logs de Debug ==="
        docker logs --tail 50 "$CONTAINER_NAME" 2>/dev/null || echo "Não foi possível obter logs"
        
        exit 1
    fi
}

# Executar função principal
main "$@"