
```
          ┌────────────────────────────┐
          │      Checklist CSV/Excel   │
          └─────────────┬──────────────┘
                        │
                        ▼
                ┌─────────────────┐
                │ Agente Auditor  │
                │ (validator_agent.py) │
                ├─────────────────┤
                │ - Itera item por item │
                │ - Consulta APIs (GA4, GSC, PSI) │
                │ - Executa Screaming Frog CLI │
                │ - Valida com MCP Chrome │
                │ - Gera JSON estruturado │
                └───────┬─────────┘
                        │
              ┌─────────┴──────────┐
              │ Item é problema?   │
              └───────┬────────────┘
                      │Sim
                      ▼
              ┌─────────────────────┐
              │ Agente Documentador │
              │ (doc_agent.py)      │
              ├─────────────────────┤
              │ - Recebe JSON do Auditor │
              │ - Cria Google Doc formatado │
              │ - Preenche: Problema, Solução, Impacto │
              │ - Inclui Evidências (screenshots, HTML) │
              │ - Referências via Context7 MCP │
              │ - Salva com padrão: CHECKLISTITEMID_URL_SEVERITY │
              └───────┬───────────────┘
                      │
      Notifica Auditor para próximo item
                      │
                      ▼
           ┌─────────────────────────┐
           │ Auditor → próximo item  │
           └─────────────────────────┘
                      │
                      ▼
             (Iteração até fim do checklist)
                      │
                      ▼
            ┌────────────────────────┐
            │ Relatórios Finais       │
            │ - Google Docs individuais│
            │ - JSON estruturado       │
            │ - Excel/PDF consolidado │
            └────────────────────────┘
```

---

Detalhes Técnicos do Diagrama:

1. **Módulos Python:**

   * `validator_agent.py` → Agente Auditor
   * `doc_agent.py` → Agente Documentador
   * `crawler.py` → Integração com Screaming Frog CLI
   * `apis.py` → Integração com GA4, GSC, PSI
   * `consolidate.py` → Consolidação de dados
   * `report.py` → Exportação de relatórios (Excel/PDF/JSON)
   * `utils/` → Logging, helpers, configs

2. **Fluxo de Dados:**

   * Checklist → Auditor → JSON (problemas) → Documentador → Google Docs
   * Auditor só passa para o próximo item após confirmação da documentação

3. **Validações e Evidências:**

   * MCP Chrome captura interações e screenshots
   * JSON contém métricas, evidências, remediation steps
   * Context7 MCP fornece referências oficiais

4. **Outputs finais:**

   * Google Docs individuais para cada problema
   * JSON consolidado
   * Excel/PDF com todos os itens do checklist

---