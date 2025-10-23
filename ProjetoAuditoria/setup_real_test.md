# 🧪 Guia para Teste Real do Sistema de Auditoria SEO

## 📋 Checklist de Configuração

### ✅ **Passo 1: Google Cloud Console**

1. **Acesse:** https://console.cloud.google.com/
2. **Crie um projeto** ou selecione um existente
3. **Ative as APIs necessárias:**
   - Google Analytics Reporting API
   - Google Search Console API
   - PageSpeed Insights API
   - Google Docs API

4. **Crie credenciais de Service Account:**
   ```bash
   # Navegue para: APIs & Services > Credentials
   # Clique em: Create Credentials > Service Account
   # Baixe o arquivo JSON
   ```

5. **Organize as credenciais:**
   ```bash
   mkdir -p credentials/
   # Coloque os arquivos JSON na pasta credentials/
   ```

### ✅ **Passo 2: Screaming Frog CLI**

1. **Download e Instalação:**
   ```bash
   # Baixe de: https://www.screamingfrog.co.uk/seo-spider/
   # Para macOS: arquivo .dmg
   # Instale arrastando para Applications
   ```

2. **Encontre o caminho do executável:**
   ```bash
   # Caminho típico no macOS:
   /Applications/Screaming\ Frog\ SEO\ Spider.app/Contents/MacOS/ScreamingFrogSEOSpider
   
   # Verifique se existe:
   ls -la "/Applications/Screaming Frog SEO Spider.app/Contents/MacOS/"
   ```

### ✅ **Passo 3: Configurar .env**

Copie `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

**Edite o arquivo .env com dados reais:**

```env
# Google Analytics 4 API
GA4_PROPERTY_ID=123456789  # Seu Property ID real
GA4_CREDENTIALS_PATH=./credentials/ga4-service-account.json

# Google Search Console API  
GSC_SITE_URL=https://seusite.com  # URL do seu site
GSC_CREDENTIALS_PATH=./credentials/gsc-service-account.json

# PageSpeed Insights API
PSI_API_KEY=AIzaSyC...  # Sua API Key real

# Google Docs API
GOOGLE_DOCS_CREDENTIALS_PATH=./credentials/docs-service-account.json
GOOGLE_DOCS_FOLDER_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms  # ID da pasta no Drive

# Screaming Frog CLI
SCREAMING_FROG_PATH=/Applications/Screaming\ Frog\ SEO\ Spider.app/Contents/MacOS/ScreamingFrogSEOSpider
SCREAMING_FROG_LICENSE_KEY=sua_licenca_aqui  # Opcional para versão paga

# Database
DATABASE_PATH=./data/audit_history.db
```

### ✅ **Passo 4: Teste Individual das Integrações**

**Teste Google Analytics:**
```bash
python -c "
from app.apis import GA4APIClient
import os
from dotenv import load_dotenv
load_dotenv()

client = GA4APIClient()
print('GA4 configurado:', client.property_id)
"
```

**Teste Google Search Console:**
```bash
python -c "
from app.apis import GSCAPIClient
import os
from dotenv import load_dotenv
load_dotenv()

client = GSCAPIClient()
print('GSC configurado:', client.site_url)
"
```

**Teste PageSpeed Insights:**
```bash
python -c "
from app.apis import PSIAPIClient
import os
from dotenv import load_dotenv
load_dotenv()

client = PSIAPIClient()
data = client.get_page_insights('https://google.com')
print('PSI funcionando:', 'performance' in data)
"
```

**Teste Screaming Frog:**
```bash
python -c "
from app.crawler import ScreamingFrogCrawler
import os
from dotenv import load_dotenv
load_dotenv()

crawler = ScreamingFrogCrawler()
print('Screaming Frog path:', crawler.screaming_frog_path)
print('Executável existe:', os.path.exists(crawler.screaming_frog_path))
"
```

### ✅ **Passo 5: Teste Completo**

**Inicie a aplicação:**
```bash
# Ative o ambiente virtual
source venv/bin/activate

# Inicie a aplicação completa
python -m flask --app app.main run --debug --port 5000
```

**Teste via API:**
```bash
# Inicie uma auditoria real
curl -X POST http://localhost:5000/api/audit/start \
  -H "Content-Type: application/json" \
  -d '{"url": "https://seusite.com", "audit_type": "complete"}'

# Verifique o status
curl http://localhost:5000/api/audit/{audit_id}/status

# Obtenha os resultados
curl http://localhost:5000/api/audit/{audit_id}/results
```

## 🚨 **Possíveis Problemas e Soluções**

### **Erro: "Credenciais não encontradas"**
- Verifique se os arquivos JSON estão na pasta `credentials/`
- Confirme os caminhos no arquivo `.env`
- Verifique permissões dos arquivos

### **Erro: "Screaming Frog não encontrado"**
- Confirme a instalação: `ls -la "/Applications/Screaming Frog SEO Spider.app/"`
- Verifique o caminho no `.env`
- Para versão gratuita, limite de 500 URLs

### **Erro: "API Key inválida"**
- Verifique se as APIs estão ativadas no Google Cloud
- Confirme se a API Key do PSI está correta
- Verifique cotas e limites das APIs

### **Erro: "Permissões insuficientes"**
- Configure permissões adequadas para as Service Accounts
- Para GA4: Analytics Viewer
- Para GSC: Search Console Viewer  
- Para Docs: Editor ou Owner da pasta

## 📊 **Dados de Teste Recomendados**

**Sites para testar:**
- Seu próprio site (com GA4 e GSC configurados)
- Sites públicos simples (para PSI e Screaming Frog)
- Exemplo: `https://example.com` (para testes básicos)

**Métricas esperadas:**
- GA4: Sessões, visualizações, taxa de rejeição
- GSC: Impressões, cliques, CTR, posição
- PSI: Scores de performance, acessibilidade, SEO
- Screaming Frog: URLs, status codes, meta tags

## 🎯 **Resultado Esperado**

Após a configuração completa, você deve conseguir:
1. ✅ Iniciar auditorias via API
2. ✅ Coletar dados reais das integrações
3. ✅ Gerar relatórios consolidados
4. ✅ Salvar histórico no banco SQLite
5. ✅ Exportar documentação para Google Docs