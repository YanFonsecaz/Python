# Guia de Deploy - Sistema de Auditoria SEO

Este documento fornece instruções detalhadas para fazer o deploy do sistema de auditoria SEO em diferentes ambientes.

## 🎯 Ambientes Suportados

- **Desenvolvimento Local** - Para desenvolvimento e testes
- **Servidor Linux** - Deploy em VPS/servidor dedicado
- **Docker** - Containerização para deploy consistente
- **Cloud Platforms** - AWS, GCP, Azure, Heroku

---

## 🚀 Deploy Local (Desenvolvimento)

### Pré-requisitos

```bash
# Python 3.9+
python3 --version

# Git
git --version

# Chrome/Chromium (para Selenium)
google-chrome --version
```

### Instalação Rápida

```bash
# 1. Clonar repositório
git clone <URL_DO_REPOSITORIO>
cd ProjetoAuditoria

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 5. Executar aplicação
python run_app.py --port 5001
```

---

## 🐧 Deploy em Servidor Linux

### 1. Preparação do Servidor

```bash
# Atualizar sistema (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y python3 python3-pip python3-venv git nginx

# Instalar Chrome para Selenium
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Instalar ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f3 | cut -d '.' -f1)
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### 2. Deploy da Aplicação

```bash
# Criar usuário para aplicação
sudo useradd -m -s /bin/bash seoaudit
sudo su - seoaudit

# Clonar e configurar aplicação
git clone <URL_DO_REPOSITORIO> /home/seoaudit/app
cd /home/seoaudit/app

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn  # Para produção

# Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Configurar credenciais
```

### 3. Configurar Systemd Service

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/seoaudit.service
```

**Conteúdo do arquivo:**
```ini
[Unit]
Description=SEO Audit System
After=network.target

[Service]
Type=notify
User=seoaudit
Group=seoaudit
WorkingDirectory=/home/seoaudit/app
Environment=PATH=/home/seoaudit/app/venv/bin
EnvironmentFile=/home/seoaudit/app/.env
ExecStart=/home/seoaudit/app/venv/bin/gunicorn --bind 127.0.0.1:5001 --workers 4 --timeout 300 run_app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable seoaudit
sudo systemctl start seoaudit
sudo systemctl status seoaudit
```

### 4. Configurar Nginx (Proxy Reverso)

```bash
# Criar configuração do Nginx
sudo nano /etc/nginx/sites-available/seoaudit
```

**Conteúdo do arquivo:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Aumentar limite de upload para documentos
    client_max_body_size 50M;
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/seoaudit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL com Let's Encrypt (Opcional)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo crontab -e
# Adicionar linha:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🐳 Deploy com Docker

### 1. Dockerfile

```dockerfile
FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f3 | cut -d '.' -f1) \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Configurar diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p app/data/exports app/data/reports app/logs

# Expor porta
EXPOSE 5001

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "300", "run_app:app"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  seoaudit:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5001
    env_file:
      - .env
    volumes:
      - ./app/data:/app/app/data
      - ./app/logs:/app/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - seoaudit
    restart: unless-stopped
```

### 3. Executar com Docker

```bash
# Build e execução
docker-compose up -d

# Verificar logs
docker-compose logs -f seoaudit

# Parar serviços
docker-compose down
```

---

## ☁️ Deploy em Cloud Platforms

### AWS EC2

```bash
# 1. Criar instância EC2 (Ubuntu 20.04 LTS)
# 2. Configurar Security Group (portas 22, 80, 443)
# 3. Conectar via SSH
ssh -i sua-chave.pem ubuntu@ip-da-instancia

# 4. Seguir passos do "Deploy em Servidor Linux"
```

### Google Cloud Platform

```bash
# 1. Criar VM no Compute Engine
gcloud compute instances create seoaudit-vm \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --tags=http-server,https-server

# 2. Conectar e configurar
gcloud compute ssh seoaudit-vm

# 3. Seguir passos do "Deploy em Servidor Linux"
```

### Heroku

```bash
# 1. Instalar Heroku CLI
# 2. Login
heroku login

# 3. Criar aplicação
heroku create seu-app-seoaudit

# 4. Configurar buildpacks
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add --index 3 https://github.com/heroku/heroku-buildpack-chromedriver

# 5. Configurar variáveis de ambiente
heroku config:set PAGESPEED_API_KEY=sua_chave
heroku config:set GOOGLE_SEARCH_CONSOLE_CREDENTIALS=base64_encoded_json

# 6. Deploy
git push heroku main
```

---

## 🔧 Configurações de Produção

### Variáveis de Ambiente Obrigatórias

```bash
# APIs (obrigatórias)
PAGESPEED_API_KEY=sua_chave_pagespeed
GOOGLE_SEARCH_CONSOLE_CREDENTIALS=/path/to/credentials.json

# IA (opcional)
OPENAI_API_KEY=sua_chave_openai
OLLAMA_BASE_URL=http://localhost:11434

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_ENV=production

# Selenium (produção)
CHROME_OPTIONS=--headless,--no-sandbox,--disable-dev-shm-usage
```

### Otimizações de Performance

```python
# gunicorn.conf.py
bind = "0.0.0.0:5001"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### Configuração de Logs

```python
# logging.conf
[loggers]
keys=root,gunicorn.error,gunicorn.access

[handlers]
keys=console,error_file,access_file

[formatters]
keys=generic,access

[logger_root]
level=INFO
handlers=console

[logger_gunicorn.error]
level=INFO
handlers=error_file
propagate=1
qualname=gunicorn.error

[logger_gunicorn.access]
level=INFO
handlers=access_file
propagate=0
qualname=gunicorn.access

[handler_console]
class=StreamHandler
formatter=generic
args=(sys.stdout, )

[handler_error_file]
class=logging.FileHandler
formatter=generic
args=('/var/log/seoaudit/error.log',)

[handler_access_file]
class=logging.FileHandler
formatter=access
args=('/var/log/seoaudit/access.log',)

[formatter_generic]
format=%(asctime)s [%(process)d] [%(levelname)s] %(message)s
datefmt=%Y-%m-%d %H:%M:%S
class=logging.Formatter

[formatter_access]
format=%(message)s
class=logging.Formatter
```

---

## 🔒 Segurança em Produção

### Firewall (UFW)

```bash
# Configurar firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Backup Automático

```bash
# Script de backup
#!/bin/bash
# /home/seoaudit/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/seoaudit/backups"
APP_DIR="/home/seoaudit/app"

mkdir -p $BACKUP_DIR

# Backup dos dados
tar -czf $BACKUP_DIR/seoaudit_data_$DATE.tar.gz $APP_DIR/app/data

# Manter apenas últimos 7 backups
find $BACKUP_DIR -name "seoaudit_data_*.tar.gz" -mtime +7 -delete

# Crontab para execução diária
# 0 2 * * * /home/seoaudit/backup.sh
```

### Monitoramento

```bash
# Instalar ferramentas de monitoramento
sudo apt install -y htop iotop nethogs

# Script de monitoramento
#!/bin/bash
# /home/seoaudit/monitor.sh

# Verificar se aplicação está rodando
if ! systemctl is-active --quiet seoaudit; then
    echo "SEO Audit service is down!" | mail -s "Alert: Service Down" admin@exemplo.com
    systemctl restart seoaudit
fi

# Verificar uso de disco
DISK_USAGE=$(df /home/seoaudit | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is at ${DISK_USAGE}%" | mail -s "Alert: High Disk Usage" admin@exemplo.com
fi
```

---

## 📊 Verificação de Deploy

### Checklist Pós-Deploy

```bash
# 1. Verificar saúde da aplicação
curl -f http://seu-dominio.com/health

# 2. Testar endpoint principal
curl -X POST http://seu-dominio.com/audit/start \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# 3. Verificar logs
sudo journalctl -u seoaudit -f

# 4. Verificar recursos do sistema
htop
df -h
free -h

# 5. Testar SSL (se configurado)
curl -I https://seu-dominio.com/health
```

### Testes de Carga (Opcional)

```bash
# Instalar Apache Bench
sudo apt install apache2-utils

# Teste básico
ab -n 100 -c 10 http://seu-dominio.com/health

# Teste com POST
ab -n 50 -c 5 -p post_data.json -T application/json http://seu-dominio.com/audit/start
```

---

## 🚨 Rollback e Recuperação

### Rollback Rápido

```bash
# 1. Parar serviço atual
sudo systemctl stop seoaudit

# 2. Restaurar versão anterior
cd /home/seoaudit/app
git checkout HEAD~1  # ou tag específica

# 3. Reinstalar dependências se necessário
source venv/bin/activate
pip install -r requirements.txt

# 4. Reiniciar serviço
sudo systemctl start seoaudit
```

### Recuperação de Dados

```bash
# Restaurar backup
cd /home/seoaudit
tar -xzf backups/seoaudit_data_YYYYMMDD_HHMMSS.tar.gz
```

---

## 📞 Suporte e Manutenção

### Logs Importantes

```bash
# Logs da aplicação
tail -f /var/log/seoaudit/error.log
tail -f /var/log/seoaudit/access.log

# Logs do sistema
sudo journalctl -u seoaudit -f
sudo journalctl -u nginx -f
```

### Comandos Úteis

```bash
# Reiniciar serviços
sudo systemctl restart seoaudit
sudo systemctl restart nginx

# Verificar status
sudo systemctl status seoaudit
sudo systemctl status nginx

# Atualizar aplicação
cd /home/seoaudit/app
git pull origin main
sudo systemctl restart seoaudit
```

---

**Última atualização:** 27 de setembro de 2025  
**Versão:** 1.0.0