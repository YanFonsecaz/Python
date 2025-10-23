# Referência da API - Sistema de Auditoria SEO

Esta documentação fornece informações detalhadas sobre todos os endpoints da API do sistema de auditoria SEO.

## Base URL

```
http://localhost:5001
```

## Autenticação

Atualmente, a API não requer autenticação. Em produção, considere implementar autenticação via API key ou JWT.

## Headers Padrão

```http
Content-Type: application/json
Accept: application/json
```

---

## 📊 Endpoints da API

### 1. Health Check

Verifica o status de saúde da aplicação e seus componentes.

**Endpoint:** `GET /health`

**Resposta de Sucesso (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-27T21:44:48.123456",
  "components": {
    "api_manager": "healthy",
    "crawler_manager": "healthy", 
    "database": "healthy",
    "documentor_agent": "healthy",
    "validator_agent": "healthy"
  },
  "stats": {
    "total_audits": 1,
    "active_audits": 0
  }
}
```

**Exemplo de uso:**
```bash
curl -X GET http://localhost:5001/health
```

---

### 2. Iniciar Auditoria

Inicia uma nova auditoria SEO para uma URL específica.

**Endpoint:** `POST /audit/start`

**Parâmetros do Body:**
```json
{
  "url": "https://exemplo.com",
  "generate_documentation": true,
  "use_ai": true
}
```

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `url` | string | ✅ | URL a ser auditada |
| `generate_documentation` | boolean | ❌ | Gerar documentação IA (padrão: false) |
| `use_ai` | boolean | ❌ | Usar IA para análises (padrão: false) |

**Resposta de Sucesso (200):**
```json
{
  "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
  "status": "started",
  "url": "https://exemplo.com",
  "timestamp": "2025-09-27T21:44:48.123456"
}
```

**Exemplo de uso:**
```bash
curl -X POST http://localhost:5001/audit/start \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/html",
    "generate_documentation": true,
    "use_ai": true
  }'
```

---

### 3. Status da Auditoria

Verifica o status atual de uma auditoria em andamento.

**Endpoint:** `GET /audit/status/{audit_id}`

**Parâmetros da URL:**
- `audit_id`: ID único da auditoria

**Resposta de Sucesso (200):**
```json
{
  "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
  "status": "completed",
  "progress": 100,
  "current_step": "documentation_generation",
  "overall_score": 21.11,
  "errors": []
}
```

**Status possíveis:**
- `started`: Auditoria iniciada
- `crawling`: Coletando dados da página
- `analyzing`: Analisando dados coletados
- `validating`: Executando validações SEO
- `documenting`: Gerando documentação
- `completed`: Auditoria concluída
- `failed`: Auditoria falhou

**Exemplo de uso:**
```bash
curl -X GET http://localhost:5001/audit/status/781c4ef7-795b-4b6a-8a8f-704f12379294
```

---

### 4. Resultado da Auditoria

Obtém o resultado completo de uma auditoria finalizada.

**Endpoint:** `GET /audit/result/{audit_id}`

**Parâmetros da URL:**
- `audit_id`: ID único da auditoria

**Resposta de Sucesso (200):**
```json
{
  "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
  "url": "https://httpbin.org/html",
  "status": "completed",
  "overall_score": 21.11,
  "timestamp": "2025-09-27T21:44:48.123456",
  "crawl_data": {
    "title": "Herman Melville - Moby-Dick",
    "meta_description": null,
    "h1_tags": ["Herman Melville - Moby-Dick"],
    "page_size": 3741,
    "load_time": 0.85
  },
  "validations": {
    "page_title": {
      "status": "passed",
      "score": 100,
      "message": "Título da página encontrado"
    },
    "meta_description": {
      "status": "failed", 
      "score": 0,
      "message": "Meta description não encontrada"
    }
  },
  "has_seo_documentation": true,
  "documentation": {
    "audit_score": 21.11,
    "audit_url": "https://httpbin.org/html",
    "summary": "Análise SEO detalhada..."
  }
}
```

**Exemplo de uso:**
```bash
curl -X GET http://localhost:5001/audit/result/781c4ef7-795b-4b6a-8a8f-704f12379294
```

---

### 5. Relatório Detalhado

Obtém um relatório detalhado com todas as validações executadas.

**Endpoint:** `GET /audit/report/{audit_id}`

**Parâmetros da URL:**
- `audit_id`: ID único da auditoria

**Resposta de Sucesso (200):**
```json
{
  "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
  "url": "https://httpbin.org/html",
  "overall_score": 21.11,
  "timestamp": "2025-09-27T21:44:48.123456",
  "validations": {
    "page_title_validation": {
      "validator": "PageTitleValidator",
      "status": "passed",
      "score": 100,
      "message": "Título da página encontrado",
      "details": {
        "title": "Herman Melville - Moby-Dick",
        "length": 26
      }
    },
    "meta_description_validation": {
      "validator": "MetaDescriptionValidator", 
      "status": "failed",
      "score": 0,
      "message": "Meta description não encontrada"
    },
    "h1_validation": {
      "validator": "H1Validator",
      "status": "passed", 
      "score": 100,
      "message": "H1 encontrado",
      "details": {
        "h1_tags": ["Herman Melville - Moby-Dick"],
        "count": 1
      }
    }
  }
}
```

**Exemplo de uso:**
```bash
curl -X GET http://localhost:5001/audit/report/781c4ef7-795b-4b6a-8a8f-704f12379294
```

---

### 6. Listar Auditorias

Lista todas as auditorias realizadas.

**Endpoint:** `GET /audit/list`

**Parâmetros de Query (opcionais):**
- `limit`: Número máximo de resultados (padrão: 50)
- `offset`: Número de registros para pular (padrão: 0)

**Resposta de Sucesso (200):**
```json
{
  "audits": [
    {
      "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
      "url": "https://httpbin.org/html", 
      "status": "completed",
      "overall_score": 21.11,
      "timestamp": "2025-09-27T21:44:48.123456"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Exemplo de uso:**
```bash
curl -X GET "http://localhost:5001/audit/list?limit=10&offset=0"
```

---

### 7. Visualizar Documentação

Obtém a documentação gerada por IA para uma auditoria.

**Endpoint:** `GET /audit/documentation/{audit_id}`

**Parâmetros da URL:**
- `audit_id`: ID único da auditoria

**Resposta de Sucesso (200):**
```json
{
  "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
  "has_documentation": true,
  "documentation": {
    "audit_score": 21.11,
    "audit_url": "https://httpbin.org/html",
    "summary": "## Relatório de Auditoria SEO\n\n### Resumo Executivo\nA auditoria técnica do site revelou várias oportunidades de melhoria...",
    "recommendations": [
      "Adicionar meta description",
      "Otimizar velocidade de carregamento",
      "Implementar dados estruturados"
    ]
  }
}
```

**Resposta quando não há documentação (404):**
```json
{
  "error": "Documentação não encontrada para esta auditoria"
}
```

**Exemplo de uso:**
```bash
curl -X GET http://localhost:5001/audit/documentation/781c4ef7-795b-4b6a-8a8f-704f12379294
```

---

### 8. Download da Documentação

Faz o download da documentação em formato DOCX.

**Endpoint:** `GET /audit/documentation/{audit_id}/download`

**Parâmetros da URL:**
- `audit_id`: ID único da auditoria

**Resposta de Sucesso (200):**
- **Content-Type:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Content-Disposition:** `attachment; filename="audit_documentation_{audit_id}.docx"`
- **Body:** Arquivo DOCX binário

**Resposta de Erro (404):**
```json
{
  "error": "Documentação não disponível para download"
}
```

**Exemplo de uso:**
```bash
curl -X GET http://localhost:5001/audit/documentation/781c4ef7-795b-4b6a-8a8f-704f12379294/download \
  -o documentation.docx
```

---

### 9. Exportar Auditoria

Exporta os dados completos de uma auditoria em formato JSON.

**Endpoint:** `GET /audit/export/{audit_id}`

**Parâmetros da URL:**
- `audit_id`: ID único da auditoria

**Resposta de Sucesso (200):**
```json
{
  "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
  "export_data": {
    "metadata": {
      "exported_at": "2025-09-27T21:44:48.123456",
      "version": "1.0.0"
    },
    "audit_result": {
      // Dados completos da auditoria
    }
  }
}
```

**⚠️ Limitação Atual:**
Este endpoint funciona apenas para auditorias em memória. Para auditorias salvas, use `/audit/result/{audit_id}`.

**Exemplo de uso:**
```bash
curl -X GET http://localhost:5001/audit/export/781c4ef7-795b-4b6a-8a8f-704f12379294 \
  -o audit_export.json
```

---

## 🚨 Códigos de Erro

### Códigos HTTP Comuns

| Código | Descrição | Exemplo |
|--------|-----------|---------|
| `200` | Sucesso | Operação realizada com sucesso |
| `400` | Bad Request | Parâmetros inválidos ou ausentes |
| `404` | Not Found | Auditoria ou recurso não encontrado |
| `500` | Internal Server Error | Erro interno do servidor |

### Formato de Erro Padrão

```json
{
  "error": "Descrição do erro",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-27T21:44:48.123456"
}
```

---

## 📝 Exemplos de Fluxo Completo

### Fluxo Básico de Auditoria

```bash
# 1. Iniciar auditoria
AUDIT_ID=$(curl -s -X POST http://localhost:5001/audit/start \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com", "generate_documentation": true}' \
  | jq -r '.audit_id')

# 2. Aguardar conclusão (verificar status)
while true; do
  STATUS=$(curl -s http://localhost:5001/audit/status/$AUDIT_ID | jq -r '.status')
  if [ "$STATUS" = "completed" ]; then
    break
  fi
  echo "Status: $STATUS"
  sleep 10
done

# 3. Obter resultado
curl -s http://localhost:5001/audit/result/$AUDIT_ID | jq '.'

# 4. Download da documentação
curl -X GET http://localhost:5001/audit/documentation/$AUDIT_ID/download \
  -o "documentation_$AUDIT_ID.docx"
```

### Monitoramento de Saúde

```bash
# Verificar saúde da aplicação
curl -s http://localhost:5001/health | jq '.components'

# Listar auditorias recentes
curl -s "http://localhost:5001/audit/list?limit=5" | jq '.audits'
```

---

## 🔧 Configuração para Desenvolvimento

### Variáveis de Ambiente Necessárias

```bash
# API Keys (obrigatórias)
export PAGESPEED_API_KEY="sua_chave_pagespeed"
export GOOGLE_SEARCH_CONSOLE_CREDENTIALS="caminho/para/credentials.json"

# IA (opcional)
export OPENAI_API_KEY="sua_chave_openai"
export OLLAMA_BASE_URL="http://localhost:11434"

# Flask (opcional)
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5001"
```

### Executar em Modo de Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python run_app.py --port 5001

# Ou com debug
python run_app.py --port 5001 --debug
```

---

## 📚 Recursos Adicionais

- **Guia do Desenvolvedor:** [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- **Changelog:** [CHANGELOG.md](./CHANGELOG.md)
- **README Principal:** [README.md](./README.md)

---

**Última atualização:** 27 de setembro de 2025  
**Versão da API:** 1.0.0