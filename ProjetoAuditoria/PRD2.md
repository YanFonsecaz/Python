PRD Completo – Auditoria Técnica SEO Automatizada (Vibe Coding)

**Projeto:** Auditoria Técnica SEO Automatizada
**Tecnologia:** Python 3.11+, Screaming Frog CLI, GA4 API, GSC API, PageSpeed Insights API, MCP Chrome (Playwright), Google Docs API, SQLite

**Objetivo:** Automatizar auditorias técnicas de SEO, gerar documentação detalhada para cada problema diretamente em **Google Docs**, e produzir relatórios consolidados em Excel/PDF e JSON estruturado.

---

1. Objetivos Principais

1. Receber checklist em **CSV ou Excel**.
2. Iterar **item por item do checklist** usando o **Agente Auditor**.
3. Validar problemas com:

   * Screaming Frog CLI
   * Google Analytics 4 API
   * Google Search Console API
   * PageSpeed Insights API
   * MCP Chrome via Playwright
4. Se houver problema:

   * Enviar dados para o **Agente Documentador**
   * Criar **Google Docs** bem formatados com Problema, Solução e Impacto
5. Repetir para todos os itens do checklist.
6. Gerar relatórios consolidados em Excel, PDF e JSON.

---

2. Fluxo de Processo

```
[Checklist CSV/Excel]
          │
          ▼
   [Agente Auditor]
   ┌─────────────────────────┐
   │ Itera item por item do  │
   │ checklist sequencialmente│
   └───────────┬────────────┘
               │
     ┌─────────┴─────────┐
     │ Item é problema?  │
     └───────┬───────────┘
             │Sim
             ▼
     [Agente Documentador]
   ┌─────────────────────────┐
   │ Cria Google Doc bem      │
   │ formatado com:           │
   │ - Problema/Oportunidade  │
   │ - Solução Técnica        │
   │ - Impacto Esperado       │
   │ - Evidências (screenshots│
   │   métricas, HTML)        │
   │ - Referências Context7   │
   └───────────┬────────────┘
               │
       Documento salvo em
          Google Docs
               │
               ▼
   [Agente Auditor] → próximo item do checklist
               │
               ▼
       Repetir até checklist
         totalmente auditado
               │
               ▼
        [Relatórios Finais]
   - Google Docs individuais
   - JSON estruturado
   - Excel/PDF consolidado
```

---
3. Agente Auditor / Validador

**Função:** Auditar cada item do checklist sequencialmente e decidir se é problema.

**Tecnologias:** Python + Playwright MCP Chrome + Screaming Frog CLI + APIs externas

**Prompt de referência para IA Auditor:**

```
Atue como Agente Auditor de SEO Técnico Sênior. Para cada item do checklist:
1. Valide usando Screaming Frog, GSC, GA4, PSI e MCP Chrome.
2. Se for problema, gere JSON estruturado com:
   - url, checklist_item_id, problem_category, problem_summary
   - severity, page_importance_score, metrics, evidence, remediation_steps, validation_procedure
3. Próximo item só é auditado após documentação do item atual.
```

**Tarefas detalhadas:**

* Iterar checklist item por item.
* Consultar dados das APIs e Screaming Frog.
* Usar MCP Chrome para validações interativas e screenshots.
* Gerar JSON estruturado para cada problema detectado.
* Registrar erros operacionais ou falhas de acesso às URLs.

---

4. Agente Documentador

**Função:** Criar documentação detalhada e bem formatada para cada problema detectado.

**Tecnologias:** Python + Google Docs API + Context7 MCP

**Prompt de referência para IA Documentador:**

```
Atue como Especialista em Comunicação de SEO Técnico. Para cada problema do Auditor:
1. Gere um Google Doc bem formatado contendo:
   - Título: [SEVERIDADE] Título do problema – URL (incluindo page_importance_score)
   - Descrição técnica detalhada (metrics + problem_category)
   - Evidências (screenshots, HTML, métricas)
   - Passos técnicos para resolução (remediation_steps)
   - Trechos de código/configuração, se aplicável
   - Procedimento de validação (validation_procedure)
   - Referências oficiais do Google Search Central via Context7 MCP
   - Impacto esperado
   - Prazo estimado para resultados
2. Salve o Google Doc com nome padronizado: `CHECKLISTITEMID_URL_SEVERITY`
3. Notifique o Auditor para prosseguir com o próximo item.
```

---

5. Saídas do Projeto

* **Google Docs** individuais, bem formatados, para cada problema.
* **JSON estruturado** consolidando todos os problemas e evidências.
* **Relatórios Excel/PDF** agregados.
* **Histórico** de auditorias armazenado em SQLite.

---

6. Arquitetura Técnica

* **Python 3.11+**
* **Módulos principais:**

  * `crawler.py` → Screaming Frog CLI
  * `apis.py` → GSC, GA4, PSI
  * `consolidate.py` → dataset unificado
  * `validator_agent.py` → Agente Auditor + MCP Chrome
  * `doc_agent.py` → Agente Documentador → Google Docs
  * `report.py` → Excel, PDF, JSON
  * `utils/` → logging, helpers, configs
* **Banco de dados:** SQLite para histórico do checklist e auditorias
* **Agendamento:** cron jobs / Task Scheduler

---

7. Funcionalidades Extras

* Priorização de problemas críticos usando `page_importance_score`.
* Evidências visuais e métricas detalhadas associadas a cada problema.
* Exportação de relatórios para dashboards ou Google Sheets.
* Histórico completo de auditorias e comparação entre execuções.
* Integração automática com Google Docs para documentação individual.

---
