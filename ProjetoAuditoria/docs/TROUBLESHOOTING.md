# Guia de Solução de Problemas

Este documento contém soluções para problemas comuns encontrados no sistema de auditoria SEO.

## 🚨 Problemas Críticos Resolvidos

### 1. Download de Documentação DOCX Falhando

**❌ Problema:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/exports/audit_documentation_xxx.docx'
```

**✅ Solução Implementada:**
O problema foi causado pelo uso de caminhos relativos. Foi corrigido implementando caminhos absolutos:

```python
# ANTES (problemático)
export_dir = "data/exports"

# DEPOIS (corrigido)
export_dir = os.path.join(os.path.dirname(__file__), "data", "exports")
```

**📍 Localização da correção:** `app/main.py` - função `_generate_word_documentation()`

---

### 2. Auditorias Não Sendo Salvas

**❌ Problema:**
Auditorias completadas não eram persistidas no sistema de arquivos.

**✅ Solução Implementada:**
Adicionado salvamento automático após conclusão da auditoria:

```python
# Salvamento automático implementado
def execute_full_audit(self, url: str, generate_documentation: bool = False, use_ai: bool = False):
    # ... código da auditoria ...
    
    # Salvar resultado automaticamente
    self._save_audit_result(audit_id, result)
    return result
```

**📍 Localização da correção:** `app/main.py` - função `execute_full_audit()`

---

## 🔧 Problemas Comuns e Soluções

### 3. Erro de Importação de Módulos

**❌ Sintomas:**
```
ModuleNotFoundError: No module named 'app.crawler'
```

**✅ Soluções:**

1. **Verificar estrutura de diretórios:**
```bash
ls -la app/
# Deve conter: __init__.py, main.py, crawler/, validator/, etc.
```

2. **Verificar PYTHONPATH:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python run_app.py
```

3. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

---

### 4. Selenium WebDriver Não Encontrado

**❌ Sintomas:**
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**✅ Soluções:**

1. **Instalar ChromeDriver (macOS):**
```bash
brew install chromedriver
```

2. **Verificar instalação:**
```bash
chromedriver --version
```

3. **Alternativa - Download manual:**
```bash
# Baixar de https://chromedriver.chromium.org/
# Colocar no PATH ou especificar caminho no código
```

---

### 5. Erro de Conexão com APIs Externas

**❌ Sintomas:**
```
requests.exceptions.ConnectionError: Failed to establish a new connection
```

**✅ Soluções:**

1. **Verificar conectividade:**
```bash
curl -I https://www.googleapis.com/pagespeedonline/v5/runPagespeed
```

2. **Verificar API Keys:**
```bash
echo $PAGESPEED_API_KEY
# Deve retornar sua chave válida
```

3. **Testar API manualmente:**
```bash
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&key=$PAGESPEED_API_KEY"
```

---

### 6. Erro de Permissões de Arquivo

**❌ Sintomas:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/data/exports'
```

**✅ Soluções:**

1. **Criar diretórios necessários:**
```bash
mkdir -p app/data/exports
mkdir -p app/data/reports
chmod 755 app/data/exports
chmod 755 app/data/reports
```

2. **Verificar permissões:**
```bash
ls -la app/data/
```

---

### 7. Porta em Uso

**❌ Sintomas:**
```
OSError: [Errno 48] Address already in use
```

**✅ Soluções:**

1. **Verificar processos na porta:**
```bash
lsof -i :5001
```

2. **Matar processo existente:**
```bash
kill -9 <PID>
```

3. **Usar porta diferente:**
```bash
python run_app.py --port 5002
```

---

### 8. Erro de Timeout em Auditorias

**❌ Sintomas:**
```
TimeoutException: Message: Timeout waiting for page load
```

**✅ Soluções:**

1. **Aumentar timeout no crawler:**
```python
# Em app/crawler/web_crawler.py
driver.set_page_load_timeout(60)  # Aumentar de 30 para 60 segundos
```

2. **Verificar URL de destino:**
```bash
curl -I <URL_DA_AUDITORIA>
```

---

## 🔍 Debugging e Logs

### Ativar Logs Detalhados

1. **Configurar nível de log:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Verificar logs da aplicação:**
```bash
tail -f app/logs/app.log
```

### Verificar Status dos Componentes

```bash
# Health check completo
curl -s http://localhost:5001/health | jq '.'

# Verificar componentes específicos
curl -s http://localhost:5001/health | jq '.components'
```

### Testar Componentes Individualmente

```python
# Testar crawler
from app.crawler.web_crawler import WebCrawler
crawler = WebCrawler()
result = crawler.crawl_page("https://example.com")
print(result)

# Testar validador
from app.validator.seo_validator import SEOValidator
validator = SEOValidator()
validations = validator.validate_page_data(result)
print(validations)
```

---

## 📊 Monitoramento de Performance

### Verificar Uso de Memória

```bash
# Durante auditoria
ps aux | grep python
top -p <PID_DO_PROCESSO>
```

### Monitorar Tempo de Resposta

```bash
# Testar tempo de resposta da API
time curl -s http://localhost:5001/health > /dev/null
```

### Verificar Espaço em Disco

```bash
# Verificar espaço usado pelos dados
du -sh app/data/
```

---

## 🔐 Problemas de Segurança

### Credenciais Não Carregadas

**❌ Sintomas:**
```
ValueError: Google Search Console credentials not found
```

**✅ Soluções:**

1. **Verificar arquivo de credenciais:**
```bash
ls -la /path/to/credentials.json
cat /path/to/credentials.json | jq '.'
```

2. **Verificar variável de ambiente:**
```bash
echo $GOOGLE_SEARCH_CONSOLE_CREDENTIALS
```

3. **Testar credenciais:**
```python
import json
with open(os.getenv('GOOGLE_SEARCH_CONSOLE_CREDENTIALS')) as f:
    creds = json.load(f)
    print("Credenciais carregadas com sucesso")
```

---

## 🧪 Problemas com Testes

### Testes Falhando

**❌ Sintomas:**
```
pytest: command not found
```

**✅ Soluções:**

1. **Instalar pytest:**
```bash
pip install pytest pytest-cov
```

2. **Executar testes:**
```bash
python -m pytest tests/ -v
```

3. **Executar teste específico:**
```bash
python -m pytest tests/test_crawler.py::test_crawl_page -v
```

---

## 📱 Problemas de Integração

### Ollama Não Respondendo

**❌ Sintomas:**
```
ConnectionError: Failed to connect to Ollama
```

**✅ Soluções:**

1. **Verificar se Ollama está rodando:**
```bash
curl http://localhost:11434/api/version
```

2. **Iniciar Ollama:**
```bash
ollama serve
```

3. **Verificar modelo instalado:**
```bash
ollama list
```

### OpenAI API Falhando

**❌ Sintomas:**
```
openai.error.AuthenticationError: Invalid API key
```

**✅ Soluções:**

1. **Verificar API key:**
```bash
echo $OPENAI_API_KEY
```

2. **Testar API key:**
```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

---

## 🚀 Problemas de Deploy

### Erro em Produção

**❌ Sintomas:**
Aplicação funciona localmente mas falha em produção.

**✅ Checklist de Deploy:**

1. **Variáveis de ambiente configuradas:**
```bash
env | grep -E "(PAGESPEED|GOOGLE|OPENAI|OLLAMA|FLASK)"
```

2. **Dependências instaladas:**
```bash
pip freeze > requirements_atual.txt
diff requirements.txt requirements_atual.txt
```

3. **Permissões de diretório:**
```bash
mkdir -p app/data/{exports,reports}
chmod -R 755 app/data/
```

4. **Firewall e portas:**
```bash
# Verificar se porta está acessível
telnet <HOST> <PORT>
```

---

## 📞 Quando Buscar Ajuda

### Informações para Incluir no Report

1. **Versão do sistema:**
```bash
python --version
pip freeze | grep -E "(flask|selenium|requests)"
```

2. **Logs de erro completos:**
```bash
tail -50 app/logs/app.log
```

3. **Configuração do ambiente:**
```bash
env | grep -E "(PAGESPEED|GOOGLE|OPENAI|OLLAMA|FLASK)" | sed 's/=.*/=***/'
```

4. **Comando que causou o erro:**
```bash
# Incluir comando exato executado
```

### Contatos de Suporte

- **Issues no GitHub:** [Criar nova issue](https://github.com/seu-usuario/ProjetoAuditoria/issues)
- **Documentação:** [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- **API Reference:** [API_REFERENCE.md](./API_REFERENCE.md)

---

**Última atualização:** 27 de setembro de 2025  
**Versão:** 1.0.0