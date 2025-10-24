# %%
import requests
import os
from langchain.agents import create_agent
from langchain_community.utilities.serpapi import SerpAPIWrapper
from IPython.display import Markdown

# Configurar chave da API
# SERPAPI_API_KEY deve ser configurada via variável de ambiente (ex.: em .env)

# Constantes de configuração SerpAPI/Trends
HL = "pt-BR"
GEO = "BR"
CATEGORY_AUTOS = 47  # Categoria 'Autos' no Google Trends
SERPAPI_ENDPOINT = "https://serpapi.com/search"

def buscar_google_trends_completo(query, hl="pt-BR", geo="BR", date="today 12-m", data_type="TIMESERIES"):
    """
    Busca Google Trends usando SerpAPI diretamente com todos os parâmetros suportados
    """
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_trends",
        "q": query,
        "hl": hl,           # Idioma (pt-BR para português brasileiro)
        "geo": geo,         # Localização (BR para Brasil)
        "date": date,       # Período (today 12-m = últimos 12 meses)
        "data_type": data_type,  # Tipo de dados
        "api_key": os.getenv("SERPAPI_API_KEY", "")
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na requisição: {e}"}

# SerpAPI para Google News (mantém como estava, mas opcional)
if os.getenv("SERPAPI_API_KEY"):
    news_tools = SerpAPIWrapper(
        serpapi_api_key=SERPAPI_API_KEY,
        params={
            "engine": "google_news",
            "hl": "pt-BR",
            "gl": "br",
            "num": 10,
        },
    )
else:
    news_tools = None

# Tema de pesquisa
tema = "Autos"

# Buscar tendências com parâmetros completos (opcional)
print("=== BUSCANDO GOOGLE TRENDS (TIMESERIES, opcional) ===")
tendencias_timeseries = buscar_google_trends_completo(
    query=tema,
    hl=HL,
    geo=GEO,
    date="today 12-m",
    data_type="TIMESERIES"
)
print("TIMESERIES:", tendencias_timeseries)

# Buscar notícias simples (opcional)
if news_tools:
    print("\n=== BUSCANDO GOOGLE NEWS (geral) ===")
    noticias_geral = news_tools.run(tema)
    print("Notícias (geral):", noticias_geral)
else:
    print("\n[INFO] news_tools não inicializado (SERPAPI_API_KEY ausente). Usaremos fetch_news_for_term por palavra-chave.")

# Criar agente para processar os dados
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
if not SERPAPI_API_KEY:
    print("[WARN] SERPAPI_API_KEY não definida. Exporte no ambiente (.env)")

# Utilitários

def _safe_get(url: str, params: dict) -> dict:
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": f"GET failed: {e}", "params": params}


def _is_today_or_yesterday(label: str):
    try:
        l = str(label).lower()
        if any(x in l for x in ["hour", "minute", "min", "hora", "horas", "minuto"]):
            return True, "D"
        if "day" in l or "dia" in l:
            return True, "D-1"
    except:
        pass
    return False, ""


def _head_status_200(url: str) -> bool:
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        return r.status_code == 200
    except:
        return False


def _dedup(items: list, key_fn):
    seen = set()
    out = []
    for it in items:
        k = key_fn(it)
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out

# Google Trends — RELATED_QUERIES por seeds do segmento Autos

def fetch_related_queries(seed: str) -> dict:
    params = {
        "engine": "google_trends",
        "hl": HL,
        "geo": GEO,
        "date": "today 12-m",
        "cat": CATEGORY_AUTOS,
        "data_type": "RELATED_QUERIES",
        "q": seed,
        "api_key": SERPAPI_API_KEY,
    }
    return _safe_get(SERPAPI_ENDPOINT, params)


def parse_terms_from_related(payload: dict):
    top, rising = [], []
    rq = payload.get("related_queries")
    if isinstance(rq, dict):
        top_arr = rq.get("top") or []
        rising_arr = rq.get("rising") or []
        for item in top_arr:
            q = item.get("query") or item.get("title")
            if isinstance(q, str):
                top.append(q.strip())
        for item in rising_arr:
            q = item.get("query") or item.get("title")
            if isinstance(q, str):
                rising.append(q.strip())
    return top, rising

# Google News via SerpAPI (2–3 notícias, prioriza D/D-1, links válidos)

def fetch_news_for_term(term: str, num: int = 6) -> list:
    params = {
        "engine": "google_news",
        "q": term,
        "hl": HL,
        "gl": "br",
        "num": num,
        "sort_by": "date",
        "api_key": SERPAPI_API_KEY,
    }
    payload = _safe_get(SERPAPI_ENDPOINT, params)
    results = payload.get("news_results") or payload.get("results") or []
    items = []
    for r in results:
        title = r.get("title") or "(sem título)"
        link = r.get("link") or r.get("url") or ""
        source = (r.get("source") or {}).get("name") if isinstance(r.get("source"), dict) else r.get("source") or ""
        date_str = r.get("date") or r.get("published_date") or r.get("dateTime") or ""
        ok, day_tag = _is_today_or_yesterday(str(date_str))
        if not ok:
            continue
        if link and not _head_status_200(link):
            continue
        items.append({
            "title": title,
            "link": link,
            "source": source,
            "date": str(date_str),
            "day_tag": day_tag,
        })
    items = _dedup(items, key_fn=lambda x: (x["title"].strip(), x["link"].strip()))
    return items[:3]

# Buscar tendências com parâmetros completos
# [LEGADO] Bloco de busca adicional de Trends/News desativado para evitar duplicidade.
# Mantemos a coleta principal baseada em RELATED_QUERIES e fetch_news_for_term.

# Coletar Top 10 + Rising Queries do segmento Autos (seeds)
seeds = ["carros", "automóveis", "SUV", "sedan", "picape", "veículo elétrico", "veículo híbrido"]
all_top = []
all_rising = []
for s in seeds:
    p = fetch_related_queries(s)
    t, r = parse_terms_from_related(p)
    all_top += t
    all_rising += r
# Dedupe e limitar a 10
uniq_top = []
seen_t = set()
for t in all_top:
    tl = t.lower()
    if tl not in seen_t:
        seen_t.add(tl)
        uniq_top.append(t)
uniq_top = uniq_top[:10]
uniq_rising = []
seen_r = set()
for t in all_rising:
    tl = t.lower()
    if tl not in seen_r:
        seen_r.add(tl)
        uniq_rising.append(t)
uniq_rising = uniq_rising[:10]

print("=== TÓPICOS TRENDS (Top) ===", uniq_top)
print("=== TÓPICOS TRENDS (Rising) ===", uniq_rising)

# Buscar notícias 2–3 por termo, priorizando mais recentes do dia
noticias_por_termo = {}
for term in uniq_top + uniq_rising:
    noticias_por_termo[term] = fetch_news_for_term(term, num=6)

# Ajustar dados que vão para o agente
tendencias = {"top_terms": uniq_top, "rising_terms": uniq_rising}
noticias = noticias_por_termo

# Criar agente para processar os dados
agent_buscador = create_agent(
    model="ollama:gemma3:4b",
    system_prompt=f"""
        Você é um assistente de análise de tendências em português do Brasil.
        Segmento: Automóveis / Autos.
        Objetivo:
        - Dados do Trends: Top 10 termos + Rising Queries (ascensão) obtidos via seeds do segmento.
        - Fontes de notícia: Google News.
        - Ordem da notícia: Sempre priorizar mais recente do dia (D). Permitir D-1 se não houver D.
        - Frequência: 2 coletas por dia (08:00 e 12:00) — agendado externamente.
        - Entrega: Tabela + resumo das notícias.

        Dados disponíveis:
        - Top terms: {tendencias['top_terms']}
        - Rising terms: {tendencias['rising_terms']}
        - Notícias por termo (2–3 por termo, filtradas por D/D-1): {noticias}

        Tarefa:
        1) Monte uma tabela Markdown com colunas: Palavra-chave | Tipo (Top/Rising) | Título | Fonte | Link | Data/Hora | Dia | Resumo.
        2) Gere resumos objetivos (2–4 frases) de cada notícia.
        3) Garanta ordem pela marcação de Dia (D antes de D-1) e organize por palavra-chave.
        4) Seja conciso e evite repetições.
    """
)

# Processar com o agente
print("\n=== PROCESSANDO COM AGENTE ===")
resultado = agent_buscador.invoke({
    "messages": [{"role": "user", "content": f"Analise o segmento '{tema}' e gere a tabela + resumos conforme as regras."}]
})


print("\n=== RESULTADO FINAL ===")
print(resultado['messages'][-1].content)
Markdown(resultado['messages'][-1].content)
# Persistir em arquivo Markdown
report_path = os.path.join(os.path.dirname(__file__), "GoogleTrends_Autos_Report.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(resultado['messages'][-1].content)
print(f"\n[OK] Relatório salvo em: {report_path}")
# %%
