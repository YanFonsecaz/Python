# Opções de Uso do Screaming Frog SEO Spider

O sistema de auditoria SEO oferece **duas opções** para utilizar o Screaming Frog SEO Spider:

## 🔧 Opção 1: Execução Automática via CLI

### Como Funciona
- O sistema executa automaticamente o Screaming Frog SEO Spider via linha de comando
- Realiza o crawling da URL fornecida em tempo real
- Processa os dados diretamente do output do crawler

### Como Usar
**Endpoint:** `POST /audit/start`

**Requisição JSON:**
```json
{
    "url": "https://exemplo.com",
    "options": {
        "include_crawler": true,
        "include_chrome_validations": true,
        "generate_documentation": true
    }
}
```

**Fluxo de Execução:**
1. Sistema valida a URL fornecida
2. Executa o Screaming Frog CLI automaticamente
3. Processa dados do crawling em tempo real
4. Consolida com dados de APIs (Google Analytics, Search Console)
5. Gera relatório completo

**Vantagens:**
- ✅ Dados sempre atualizados
- ✅ Processo totalmente automatizado
- ✅ Integração com outras fontes de dados
- ✅ Não requer conhecimento técnico do usuário

**Requisitos:**
- Screaming Frog SEO Spider instalado no servidor
- Licença válida (para sites grandes)

---

## 📁 Opção 2: Upload de CSV Exportado

### Como Funciona
- Usuário executa o Screaming Frog manualmente
- Exporta os dados como CSV
- Faz upload do arquivo via API
- Sistema processa os dados do CSV

### Como Usar
**Endpoint:** `POST /audit/start`

**Requisição Form-Data:**
```
Content-Type: multipart/form-data

screaming_frog_file: [arquivo.csv]
url: "https://exemplo.com" (opcional)
options: '{"generate_documentation": true}' (opcional)
```

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:5000/audit/start \
  -F "screaming_frog_file=@crawl_data.csv" \
  -F "url=https://exemplo.com" \
  -F "options={\"generate_documentation\": true}"
```

**Fluxo de Execução:**
1. Sistema valida o arquivo CSV enviado
2. Carrega dados do Screaming Frog do arquivo
3. Analisa problemas baseados no CSV
4. Gera relatório focado nos dados do Screaming Frog
5. Opcionalmente gera documentação

**Vantagens:**
- ✅ Controle total sobre o crawling
- ✅ Pode usar configurações personalizadas do Screaming Frog
- ✅ Funciona offline
- ✅ Permite análise de crawls históricos
- ✅ Não requer Screaming Frog no servidor

**Requisitos:**
- Screaming Frog SEO Spider no computador do usuário
- Arquivo CSV exportado do Screaming Frog

---

## 🔄 Como o Sistema Decide Entre as Opções

O sistema detecta automaticamente qual opção usar baseado na requisição:

```python
# No endpoint /audit/start
if 'screaming_frog_file' in request.files:
    # Opção 2: Processa upload de CSV
    return _handle_csv_upload_audit()
else:
    # Opção 1: Execução automática via CLI
    # Processa requisição JSON normal
```

## 📊 Diferenças nos Resultados

### Opção 1 (CLI Automático)
- **Dados Consolidados:** Screaming Frog + Google APIs + Chrome DevTools
- **Relatório Completo:** Performance, SEO técnico, Analytics
- **Tempo:** 5-10 minutos
- **Score:** Baseado em múltiplas fontes

### Opção 2 (Upload CSV)
- **Dados Focados:** Apenas Screaming Frog
- **Relatório Técnico:** SEO técnico detalhado
- **Tempo:** 3-8 minutos
- **Score:** Baseado nos problemas do Screaming Frog

## 🛠️ Configurações Avançadas

### Variáveis de Ambiente
```bash
# Para Opção 1 (CLI)
SCREAMING_FROG_PATH=/path/to/screaming-frog
SCREAMING_FROG_TIMEOUT=300

# Para ambas as opções
SCREAMING_FROG_MAX_PAGES=10000
SCREAMING_FROG_DEPTH=5
```

### Opções Personalizadas
```json
{
    "screaming_frog_options": {
        "max_pages": 5000,
        "crawl_depth": 3,
        "include_external_links": false,
        "respect_robots_txt": true
    }
}
```

## 📋 Formatos de CSV Suportados

O sistema aceita os seguintes exports do Screaming Frog:
- **Internal HTML:** Páginas internas do site
- **Response Codes:** Status HTTP das páginas
- **Page Titles:** Títulos das páginas
- **Meta Description:** Meta descrições
- **H1:** Cabeçalhos H1
- **Images:** Análise de imagens
- **External Links:** Links externos

## 🚀 Exemplos Práticos

### Exemplo 1: Auditoria Automática Completa
```bash
curl -X POST http://localhost:5000/audit/start \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://meusite.com",
    "options": {
      "include_crawler": true,
      "include_chrome_validations": true,
      "generate_documentation": true
    }
  }'
```

### Exemplo 2: Upload de CSV do Screaming Frog
```bash
curl -X POST http://localhost:5000/audit/start \
  -F "screaming_frog_file=@internal_html.csv" \
  -F "url=https://meusite.com"
```

## 📈 Monitoramento

Ambas as opções podem ser monitoradas através dos endpoints:
- `GET /audit/status/{audit_id}` - Status da auditoria
- `GET /audit/result/{audit_id}` - Resultado completo
- `GET /audit/report/{audit_id}` - Relatório formatado

## 🔍 Troubleshooting

### Problemas Comuns - Opção 1 (CLI)
- **Screaming Frog não encontrado:** Verificar `SCREAMING_FROG_PATH`
- **Timeout:** Aumentar `SCREAMING_FROG_TIMEOUT`
- **Licença:** Verificar licença para sites grandes

### Problemas Comuns - Opção 2 (CSV)
- **Arquivo inválido:** Verificar se é CSV válido do Screaming Frog
- **Formato incorreto:** Usar export padrão do Screaming Frog
- **Arquivo muito grande:** Limitar crawl ou dividir em partes

---

**💡 Dica:** Para sites pequenos (< 500 páginas), use a Opção 1 para análise completa. Para sites grandes ou análises específicas, use a Opção 2 com configurações personalizadas do Screaming Frog.