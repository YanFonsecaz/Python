# Guia do Desenvolvedor - Sistema de Auditoria SEO

## 📋 Visão Geral

Este projeto é um sistema completo de auditoria SEO desenvolvido em Python com Flask, que permite analisar websites e gerar relatórios detalhados com documentação automatizada usando IA.

### Status Atual do Projeto ✅
- **Estado**: Totalmente funcional e testado
- **Versão**: 1.0.0
- **Última atualização**: 27/09/2025
- **Todos os endpoints**: Funcionando corretamente
- **Documentação DOCX**: Problema resolvido, download funcionando

## 🏗️ Arquitetura do Sistema

### Componentes Principais

```
ProjetoAuditoria/
├── app/                    # Código principal da aplicação
│   ├── main.py            # API Flask e orquestração
│   ├── apis.py            # Integração com APIs externas
│   ├── crawler.py         # Web crawler
│   ├── validator_agent.py # Validações SEO
│   ├── seo_audit_agent.py # Agente de auditoria SEO
│   ├── seo_documentation_agent.py # Geração de documentação
│   ├── consolidate.py     # Consolidação de dados
│   ├── report.py          # Geração de relatórios
│   └── database.py        # Gerenciamento de banco de dados
├── data/                  # Dados e resultados
│   ├── reports/          # Relatórios JSON das auditorias
│   ├── exports/          # Arquivos DOCX exportados
│   └── screaming_frog/   # Dados do Screaming Frog
├── tests/                # Testes unitários
└── logs/                 # Logs da aplicação
```

### Fluxo de Auditoria

1. **Início**: POST `/audit/start` com URL e opções
2. **Coleta de Dados**: APIs, Crawler, Chrome DevTools
3. **Consolidação**: Unificação dos dados coletados
4. **Validações**: Execução de regras SEO
5. **Documentação**: Geração automática via IA (opcional)
6. **Relatório**: Criação de relatório final
7. **Armazenamento**: Salvamento em JSON e banco de dados

## 🚀 Como Executar

### Pré-requisitos
```bash
# Python 3.9+
# Dependências no requirements.txt
pip install -r requirements.txt
```

### Variáveis de Ambiente
Copie `.env.example` para `.env` e configure:
```bash
# APIs
PAGESPEED_API_KEY=sua_chave_aqui
GOOGLE_SEARCH_CONSOLE_CREDENTIALS=caminho_para_credentials.json

# IA/LLM
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sua_chave_openai (opcional)

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_SECRET_KEY=sua_chave_secreta

# Banco de Dados
DATABASE_PATH=data/audit_history.db
```

### Executar a Aplicação
```bash
# Método 1: Diretamente
python run_app.py

# Método 2: Com porta específica
python run_app.py --port 5001

# Método 3: Modo desenvolvimento
FLASK_DEBUG=True python run_app.py
```

## 📡 API Endpoints

### Principais Endpoints

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|---------|
| GET | `/health` | Status da aplicação | ✅ |
| POST | `/audit/start` | Iniciar auditoria | ✅ |
| GET | `/audit/status/{id}` | Status da auditoria | ✅ |
| GET | `/audit/result/{id}` | Resultado completo | ✅ |
| GET | `/audit/report/{id}` | Relatório detalhado | ✅ |
| GET | `/audit/list` | Listar auditorias | ✅ |
| GET | `/audit/export/{id}` | Exportar relatório | ⚠️ |
| GET | `/audit/documentation/{id}` | Ver documentação | ✅ |
| GET | `/audit/documentation/{id}/download` | Download DOCX | ✅ |

### Exemplo de Uso

```bash
# Iniciar auditoria
curl -X POST "http://localhost:5000/audit/start" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "generate_documentation": true}'

# Verificar status
curl "http://localhost:5000/audit/status/{audit_id}"

# Baixar documentação
curl "http://localhost:5000/audit/documentation/{audit_id}/download" \
  -o documentacao.docx
```

## 🔧 Desenvolvimento

### Estrutura de Classes Principais

#### AuditOrchestrator (`main.py`)
- **Responsabilidade**: Orquestração completa da auditoria
- **Métodos principais**:
  - `execute_full_audit()`: Executa auditoria completa
  - `_collect_api_data()`: Coleta dados de APIs
  - `_execute_crawler()`: Executa web crawler
  - `_execute_validations()`: Executa validações SEO
  - `_generate_documentation()`: Gera documentação IA

#### ValidatorAgent (`validator_agent.py`)
- **Responsabilidade**: Validações SEO
- **Validações implementadas**:
  - Títulos de página
  - Meta descriptions
  - Tags H1
  - Crawlability
  - Integração GA4/GSC

#### SEODocumentationAgent (`seo_documentation_agent.py`)
- **Responsabilidade**: Geração de documentação via IA
- **Funcionalidades**:
  - Análise de dados de auditoria
  - Geração de conteúdo em Markdown
  - Integração com Ollama/OpenAI

### Adicionando Novas Validações

1. **Edite `validator_agent.py`**:
```python
def validate_nova_regra(self, data: Dict) -> ValidationResult:
    """Nova validação SEO."""
    # Implementar lógica
    return ValidationResult(
        validation_type="nova_regra",
        status="passed|failed|warning",
        score=score,
        message="Mensagem descritiva",
        details={"key": "value"},
        recommendations=["Recomendação 1", "Recomendação 2"]
    )
```

2. **Registre no `execute_validations()`**:
```python
validations.append(self.validate_nova_regra(consolidated_data))
```

### Adicionando Novos Endpoints

1. **Adicione no `main.py`**:
```python
@app.route('/novo/endpoint', methods=['GET'])
def novo_endpoint():
    """Documentação do endpoint."""
    try:
        # Lógica do endpoint
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

## 🧪 Testes

### Executar Testes
```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_main.py
pytest tests/test_validator_agent.py

# Com cobertura
pytest --cov=app tests/
```

### Estrutura de Testes
- `tests/test_main.py`: Testes da API Flask
- `tests/test_validator_agent.py`: Testes das validações
- `tests/test_apis.py`: Testes de integração com APIs
- `tests/test_crawler.py`: Testes do web crawler

## 🐛 Problemas Conhecidos e Soluções

### ✅ Problemas Resolvidos

1. **Download de Documentação DOCX**
   - **Problema**: Caminho relativo incorreto
   - **Solução**: Implementado caminho absoluto em `_generate_word_documentation()`

2. **Salvamento de Arquivos JSON**
   - **Problema**: Auditorias não eram salvas automaticamente
   - **Solução**: Adicionado salvamento automático no `execute_full_audit()`

### ⚠️ Limitações Atuais

1. **Endpoint de Exportação**
   - Funciona apenas para auditorias em memória
   - Não carrega auditorias salvas do disco

2. **Screaming Frog Integration**
   - Implementação básica
   - Requer arquivo CSV manual

## 📊 Monitoramento e Logs

### Logs da Aplicação
```bash
# Visualizar logs em tempo real
tail -f logs/app.log

# Filtrar erros
grep "ERROR" logs/app.log
```

### Métricas de Health Check
O endpoint `/health` retorna:
- Status dos componentes
- Número de auditorias ativas/completadas
- Timestamp da verificação

## 🔒 Segurança

### Validação de Entrada
- URLs são validadas antes do processamento
- Parâmetros são sanitizados
- Rate limiting recomendado para produção

### Variáveis Sensíveis
- Nunca commitar chaves de API
- Usar variáveis de ambiente
- Arquivo `.env` no `.gitignore`

## 🚀 Deploy em Produção

### Recomendações
1. **Servidor Web**: Usar Gunicorn + Nginx
2. **Banco de Dados**: Migrar para PostgreSQL
3. **Cache**: Implementar Redis para resultados
4. **Monitoramento**: Adicionar Prometheus/Grafana
5. **Logs**: Centralizar com ELK Stack

### Exemplo de Deploy
```bash
# Instalar Gunicorn
pip install gunicorn

# Executar em produção
gunicorn -w 4 -b 0.0.0.0:5000 run_app:app
```

## 🤝 Contribuindo

### Fluxo de Desenvolvimento
1. Fork do repositório
2. Criar branch feature: `git checkout -b feature/nova-funcionalidade`
3. Implementar mudanças
4. Adicionar testes
5. Executar testes: `pytest`
6. Commit: `git commit -m "feat: nova funcionalidade"`
7. Push: `git push origin feature/nova-funcionalidade`
8. Criar Pull Request

### Padrões de Código
- **PEP 8**: Seguir guia de estilo Python
- **Type Hints**: Usar em todas as funções
- **Docstrings**: Documentar classes e métodos
- **Testes**: Cobertura mínima de 80%

## 📚 Recursos Adicionais

### Documentação Técnica
- `PRD.mk`: Documento de Requisitos do Produto
- `DiagramaTecnico.mk`: Diagrama da arquitetura
- `SCREAMING_FROG_OPTIONS.md`: Opções do Screaming Frog

### Dependências Principais
- **Flask**: Framework web
- **Requests**: Cliente HTTP
- **BeautifulSoup**: Parser HTML
- **Selenium**: Automação de browser
- **python-docx**: Geração de documentos Word
- **pytest**: Framework de testes

## 📞 Suporte

### Contato
- **Issues**: Usar GitHub Issues para bugs
- **Discussões**: GitHub Discussions para dúvidas
- **Email**: [seu-email@exemplo.com]

### FAQ

**Q: Como adicionar uma nova API externa?**
A: Edite `apis.py` e adicione a nova integração na classe `APIManager`.

**Q: Como modificar as validações SEO?**
A: Edite `validator_agent.py` e adicione/modifique as validações na classe `ValidatorAgent`.

**Q: Como personalizar a documentação gerada?**
A: Modifique os prompts em `seo_documentation_agent.py`.

---

**Última atualização**: 27/09/2025  
**Versão do documento**: 1.0  
**Status**: ✅ Projeto totalmente funcional