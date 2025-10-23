# Sistema de Auditoria SEO 🔍

![Status](https://img.shields.io/badge/Status-Funcional-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-red)
![Testes](https://img.shields.io/badge/Testes-Passando-green)

**✅ Totalmente funcional e testado**  
**📅 Última atualização**: 27/09/2025

## 📋 Descrição

Sistema completo de auditoria SEO desenvolvido em Python que analisa websites e gera relatórios detalhados com documentação automatizada usando IA.

### 🚀 Funcionalidades Principais

- 🔍 **Auditoria SEO Completa**: Análise abrangente de websites
- 📊 **Múltiplas Fontes de Dados**: PageSpeed, GSC, GA4, Screaming Frog
- 🤖 **Documentação IA**: Geração automática de relatórios usando LLM
- 📄 **Exportação DOCX**: Download de documentação em Word
- 🌐 **API REST**: Interface completa para integração
- 📈 **Validações SEO**: Títulos, meta descriptions, H1, crawlability
- 💾 **Histórico**: Armazenamento de auditorias anteriores

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   Agentes IA    │
│   (Opcional)    │◄──►│   (main.py)     │◄──►│   (Validação)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   APIs Externas │    │   Orquestrador  │    │   Crawler       │
│   (GSC, GA4)    │◄──►│   (Auditoria)   │◄──►│   (Selenium)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Banco SQLite  │
                       │   + Arquivos    │
                       └─────────────────┘
```

### Componentes Principais
- **Orquestrador de Auditoria** (`main.py`): Coordena todo o processo de auditoria
- **Agente Validador** (`validator_agent.py`): Executa validações SEO específicas
- **Agente Documentador** (`seo_documentation_agent.py`): Gera documentação usando IA
- **Gerenciador de APIs** (`apis.py`): Integração com APIs externas
- **Web Crawler** (`crawler.py`): Coleta dados do website
- **Consolidador** (`consolidate.py`): Unifica dados de múltiplas fontes

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd ProjetoAuditoria

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves de API
```

### 2. Configuração Mínima

Edite o arquivo `.env`:
```bash
# APIs obrigatórias
PAGESPEED_API_KEY=sua_chave_pagespeed
GOOGLE_SEARCH_CONSOLE_CREDENTIALS=caminho/para/credentials.json

# IA (opcional - usa Ollama por padrão)
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sua_chave_openai

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 3. Executar

```bash
# Executar a aplicação
python run_app.py

# Ou com porta específica
python run_app.py --port 5001
```

### 4. Testar

```bash
# Verificar se está funcionando
curl http://localhost:5000/health

# Iniciar uma auditoria
curl -X POST "http://localhost:5000/audit/start" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "generate_documentation": true}'
```

## 📡 API Endpoints

| Endpoint | Método | Descrição | Status |
|----------|--------|-----------|---------|
| `/health` | GET | Status da aplicação | ✅ |
| `/audit/start` | POST | Iniciar auditoria | ✅ |
| `/audit/status/{id}` | GET | Status da auditoria | ✅ |
| `/audit/result/{id}` | GET | Resultado completo | ✅ |
| `/audit/report/{id}` | GET | Relatório detalhado | ✅ |
| `/audit/list` | GET | Listar auditorias | ✅ |
| `/audit/documentation/{id}/download` | GET | Download DOCX | ✅ |

### Exemplo de Uso Completo

```bash
# 1. Iniciar auditoria
AUDIT_ID=$(curl -s -X POST "http://localhost:5000/audit/start" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html", "generate_documentation": true}' \
  | jq -r '.audit_id')

# 2. Aguardar conclusão (ou verificar status)
sleep 60

# 3. Verificar resultado
curl "http://localhost:5000/audit/result/$AUDIT_ID" | jq

# 4. Baixar documentação
curl "http://localhost:5000/audit/documentation/$AUDIT_ID/download" \
  -o "auditoria_$AUDIT_ID.docx"
```

## 📊 Exemplo de Resultado

```json
{
  "audit_id": "781c4ef7-795b-4b6a-8a8f-704f12379294",
  "url": "https://httpbin.org/html",
  "status": "completed",
  "overall_score": 21.11,
  "validations": {
    "page_title": {"status": "failed", "score": 0},
    "meta_description": {"status": "failed", "score": 0},
    "h1_tags": {"status": "passed", "score": 100},
    "crawlability": {"status": "warning", "score": 50}
  },
  "documentation": {
    "summary": "Análise detalhada do site...",
    "audit_score": 21.11
  }
}
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Testes específicos
pytest tests/test_main.py -v
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
ProjetoAuditoria/
├── app/                    # Código principal
│   ├── main.py            # API Flask
│   ├── validator_agent.py # Validações SEO
│   ├── seo_documentation_agent.py # IA
│   └── ...
├── data/                  # Dados e resultados
├── tests/                 # Testes unitários
├── logs/                  # Logs da aplicação
└── DEVELOPER_GUIDE.md     # Guia completo para devs
```

### Para Desenvolvedores

📖 **Leia o [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** para:
- Arquitetura detalhada
- Como adicionar novas validações
- Como criar novos endpoints
- Padrões de código
- Deploy em produção

## 🐛 Problemas Conhecidos

### ✅ Resolvidos
- ✅ Download de documentação DOCX
- ✅ Salvamento automático de auditorias
- ✅ Validações SEO funcionando

### ⚠️ Limitações
- Endpoint de exportação funciona apenas para auditorias em memória
- Integração com Screaming Frog requer arquivo CSV manual

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Faça suas mudanças
4. Adicione testes
5. Execute: `pytest`
6. Commit: `git commit -m "feat: nova funcionalidade"`
7. Push: `git push origin feature/nova-funcionalidade`
8. Abra um Pull Request

## 📚 Documentação

- **[Guia do Desenvolvedor](./DEVELOPER_GUIDE.md)** - Documentação técnica completa
- **[Referência da API](./API_REFERENCE.md)** - Endpoints e exemplos de uso  
- **[Changelog](./CHANGELOG.md)** - Histórico de mudanças e correções
- **[Solução de Problemas](./TROUBLESHOOTING.md)** - Guia para resolver issues comuns
- **[Deploy em Produção](./DEPLOYMENT.md)** - Guia completo de deploy
- **[Testes](./tests/)** - Suíte de testes unitários
- **[Logs](./app/logs/)** - Arquivos de log da aplicação
- 📋 [PRD](./PRD.mk) - Requisitos do produto
- 🏗️ [Diagrama Técnico](./DiagramaTecnico.mk) - Arquitetura
- 🕷️ [Screaming Frog](./SCREAMING_FROG_OPTIONS.md) - Configurações

## 📞 Suporte

- 🐛 **Bugs**: Abra uma [Issue](../../issues)
- 💬 **Dúvidas**: Use [Discussions](../../discussions)
- 📧 **Contato**: [seu-email@exemplo.com]

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**🚀 Projeto totalmente funcional e pronto para uso!**

[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red)](https://github.com/seu-usuario/ProjetoAuditoria)

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação da API em `/api/info`
- Verifique os logs em `./logs/audit.log`

## 🔄 Versões

- **v1.0.0** - Versão inicial com todas as funcionalidades principais
  - Integração com APIs do Google
  - Agentes Auditor e Documentador
  - Sistema de relatórios
  - Interface Flask API
  - Testes unitários completos