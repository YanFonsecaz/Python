
# 📑 PRD – Sistema de Análise de Web Core Vitals com IA e Django  

## 📋 Informações do Projeto  
- **Nome:** WCV Auditor AI  
- **Stack:** Django 5+, Python 3.11+, Celery, PostgreSQL (ou SQLite no MVP), TailwindCSS/Bootstrap, Pandas, python-docx, reportlab, MCP Context7, MCP Chrome (chrome-devtools-mcp), APIs (GSC e PageSpeed Insights).  
- **Objetivo:** Analisar e monitorar métricas de Web Core Vitals (LCP, CLS, INP) em tempo real, integrando APIs oficiais do Google e agentes de IA para diagnóstico e documentação técnica.  

---

## 🎯 Visão Geral  
O **WCV Auditor AI** é um sistema web full stack desenvolvido em Django, projetado para auditar e acompanhar a evolução das métricas de Web Core Vitals (WCV) de sites.  

A ferramenta coleta dados em tempo real do **PageSpeed Insights (PSI)** e **Google Search Console (GSC)**, e usa o **MCP (chrome-devtools-mcp)** para capturar métricas idênticas às do DevTools Performance.  

Um **agente de IA especializado em SEO técnico** analisa os resultados e identifica os elementos da página que causam problemas de desempenho. Outro **agente documentador** transforma os achados em relatórios técnicos detalhados, com recomendações e evidências.  

---

## ⚙️ Funcionalidades Principais  

### 🔹 1. Integração com APIs
- Conexão com APIs do **Google Search Console (GSC)** e **PageSpeed Insights (PSI)**.  
- Coleta de métricas de desempenho, cobertura e indexação.  
- Análise comparativa com dados do **DevTools Performance** via **MCP Chrome**.  

### 🔹 2. Análise de Web Core Vitals (WCV)
- Métricas monitoradas: **Largest Contentful Paint (LCP)**, **Cumulative Layout Shift (CLS)** e **Interaction to Next Paint (INP)**.  
- O **MCP Chrome** simula navegação e mede métricas em tempo real.  
- Dados comparados com históricos e recomendações da documentação do Google via **MCP Context7**.  

### 🔹 3. Agente de IA – Auditor Técnico (WCV Auditor)
- Especialista em SEO técnico e performance.  
- Interpreta dados do MCP, PSI e GSC.  
- Identifica elementos causadores de lentidão (imagens, scripts, layout shifts, etc.).  
- Consulta **MCP Context7** para buscar soluções oficiais do Google.  

### 🔹 4. Agente de IA – Documentador SEO
- Consolida achados do auditor técnico.  
- Gera relatórios técnicos estruturados com:  
  - Problema detectado  
  - Causa provável  
  - Impacto em SEO/performance  
  - Evidências (prints, métricas, URLs)  
  - Recomendações práticas (baseadas em docs oficiais)  
- Permite **exportação em Word e PDF**.  

### 🔹 5. Histórico de Análises por Domínio
- Cada domínio recebe uma **pasta individual** no sistema.  
- Armazena métricas históricas de todas as URLs analisadas.  
- Interface para comparar evolução das métricas ao longo do tempo.  

### 🔹 6. Relatórios e Interface Web
- Dashboard com resumo de desempenho (LCP, CLS, INP por data e URL).  
- Relatórios interativos e exportáveis.  
- Filtros por domínio, URL e período.  

---

## 🧠 Fluxo de Operação  

```
[Usuário]
   │
   ├── Insere URL / conecta APIs (GSC, PSI)
   ▼
[Django Backend]
   ├── Coleta dados GSC + PSI
   ├── Executa MCP Chrome (simulação real)
   ▼
[Agente de IA – WCV Auditor]
   ├── Analisa dados e identifica causas
   ├── Consulta documentação via MCP Context7
   ▼
[Agente de IA – Documentador]
   ├── Gera relatório técnico (HTML)
   ├── Exporta Word/PDF
   ▼
[Interface Web]
   ├── Exibe métricas e histórico
   └── Permite download dos relatórios
```

---

## 🏗️ Arquitetura Técnica (resumida)

```
[Django Views/Templates]
   ├── Dashboard (Histórico de domínios)
   ├── Nova Análise (formulário para URL/APIs)
   ├── Resultados WCV
   └── Relatórios (exportação Word/PDF)
   │
[Celery Workers]
   ├── Coleta dados GSC/PSI
   ├── Executa MCP Chrome
   ├── Agente de IA (Auditor)
   └── Agente de IA (Documentador)
   │
[PostgreSQL]
   ├── Domain
   ├── URLMetric
   ├── AuditSession
   ├── Report
   └── User
   │
[File System]
   └── /audits/{dominio}/
        ├── metrics.json
        ├── evidences/
        └── reports/
```

---

## 📊 Roadmap de Entrega

| Semana | Entrega | Descrição |
|--------|----------|-----------|
| 1 | Integração PSI | Coleta de métricas e exibição simples |
| 2 | Integração GSC | Métricas combinadas + histórico básico |
| 3 | MCP Chrome | Coleta real-time igual ao DevTools |
| 4 | Agente Auditor IA | Diagnóstico automatizado dos problemas |
| 5 | Agente Documentador IA | Relatórios Word/PDF com recomendações |
| 6 | Dashboard Histórico | Pastas por domínio + comparativos |
| 7 | Refinamentos | UI final, ajustes e logs automáticos |

---

## ✅ Validações Principais  
- Métricas iguais às do **Chrome DevTools Performance**.  
- Histórico salvo por domínio e data.  
- Exportação Word e PDF funcional.  
- IA gera relatórios técnicos completos e contextualizados.  

---

## 💡 Diferenciais do Sistema
- Auditoria **100% automatizada e explicada com IA**.  
- Uso combinado de **MCP Chrome + Context7**.  
- Integração direta com **APIs oficiais do Google**.  
- Geração de relatórios técnicos e históricos prontos para clientes.  
