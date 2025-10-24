# -*- coding: utf-8 -*-
"""
Monitoramento diário de tópicos e notícias: Setor “Autos / Carros”.

Este script:
- Busca no Google Trends (categoria 47 – Automóveis/Autos) os Top 10 termos e Rising Queries.
- Para cada termo, consulta 2–3 notícias no Google News (priorizando as mais recentes do dia).
- Remove duplicatas, valida links e gera uma saída em Markdown com tabela + resumo.
- LLM para resumo: Ollama (gemma3:4b) via REST API (configure OLLAMA_HOST e OLLAMA_MODEL).
- Usa variáveis de ambiente (SERPAPI_API_KEY, OLLAMA_HOST, OLLAMA_MODEL) — não inclua segredos no código.
- Frequência sugerida: 08:00 e 12:00 (America/Sao_Paulo). Pode ser agendado via cron ou com a lib "schedule" se disponível.
"""

import os
import sys
import time
import requests
from typing import List, Dict, Tuple
from datetime import datetime, timezone

# Fuso horário — apenas anotação; ajuste o agendamento externamente
TZ = os.getenv("APP_TZ", "America/Sao_Paulo")

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

# Ollama config (LLM)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

HL = "pt-BR"  # idioma
GEO = "BR"    # país
CATEGORY_AUTOS = 47
DATE_RANGE = "today 12-m"

# ----------------------
# Utilitários
# ----------------------

def _require_serpapi() -> None:
    if not SERPAPI_API_KEY:
        print("[WARN] SERPAPI_API_KEY não definida. Exporte no ambiente (.env).")


def _safe_get(url: str, params: Dict) -> Dict:
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": f"GET failed: {e}", "url": url, "params": params}


def _is_today_or_yesterday(label: str) -> Tuple[bool, str]:
    """Heurística para datas do Google News (ex.: 'há 2 horas', '1 day ago', ISO)."""
    try:
        label_l = label.lower()
        now = datetime.now(timezone.utc)
        if any(x in label_l for x in ["hour", "minute", "min", "hora", "horas", "minuto"]):
            return True, "D"
        if "day" in label_l or "dia" in label_l:
            # "1 day ago" ~ ontem
            return True, "D-1"
        # Tenta ISO / RFC
        dt = datetime.fromisoformat(label.replace("Z", "+00:00"))
        delta = now.date() - dt.date()
        if delta.days == 0:
            return True, "D"
        if delta.days == 1:
            return True, "D-1"
        return False, "D-?"
    except Exception:
        return False, "D-?"


def _head_status_200(url: str) -> bool:
    try:
        h = requests.head(url, timeout=10, allow_redirects=True)
        return 200 <= h.status_code < 300
    except Exception:
        return False


def _dedup_news(items: List[Dict]) -> List[Dict]:
    seen = set()
    result = []
    for it in items:
        key = (it.get("title", "").strip(), it.get("link", "").strip())
        if key in seen:
            continue
        seen.add(key)
        result.append(it)
    return result


# ----------------------
# Google Trends via SerpAPI
# ----------------------

SERPAPI_ENDPOINT = "https://serpapi.com/search"


def fetch_trends(data_type: str) -> Dict:
    """data_type: 'TOP_QUERIES' ou 'RISING_QUERIES' ou 'TIMESERIES'"""
    _require_serpapi()
    params = {
        "engine": "google_trends",
        "hl": HL,
        "geo": GEO,
        "date": DATE_RANGE,
        "category": CATEGORY_AUTOS,
        "data_type": data_type,
        "api_key": SERPAPI_API_KEY,
    }
    return _safe_get(SERPAPI_ENDPOINT, params)


def parse_terms_from_trends(payload: Dict, kind: str) -> List[str]:
    """Extrai lista de termos do payload. kind: 'Top' ou 'Rising'."""
    terms = []
    if not isinstance(payload, dict):
        return terms
    # Estruturas possíveis (variam com SerpAPI)
    # Tenta chaves comuns
    candidates = [
        "top_queries", "rising_queries", "queries", "related_queries", "results"
    ]
    for key in candidates:
        data = payload.get(key)
        if isinstance(data, list):
            for item in data:
                q = item.get("query") or item.get("topic") or item.get("title")
                if q and isinstance(q, str):
                    terms.append(q)
    # Fallback: se não veio nada, tenta dentro de "data"/"news_results" etc.
    if not terms:
        for v in payload.values():
            if isinstance(v, list):
                for item in v:
                    q = item.get("query") or item.get("title")
                    if q and isinstance(q, str):
                        terms.append(q)
    # Normaliza, limita
    uniq = []
    seen = set()
    for t in terms:
        t2 = t.strip()
        if t2 and t2.lower() not in seen:
            seen.add(t2.lower())
            uniq.append(t2)
    # Top 10 por padrão
    return uniq[:10] if kind == "Top" else uniq[:10]


# ----------------------
# Google News via SerpAPI
# ----------------------

def fetch_news_for_term(term: str, num: int = 6) -> List[Dict]:
    _require_serpapi()
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
        title = r.get("title")
        link = r.get("link") or r.get("url")
        source = (r.get("source") or {}).get("name") if isinstance(r.get("source"), dict) else r.get("source")
        date_str = r.get("date") or r.get("published_date") or r.get("dateTime") or ""
        ok, day_tag = _is_today_or_yesterday(str(date_str))
        if not ok:
            continue  # aplica regra: prioriza D/D-1
        if link and not _head_status_200(link):
            continue
        items.append({
            "title": title or "(sem título)",
            "link": link or "",
            "source": source or "",
            "date": str(date_str),
            "day_tag": day_tag,
        })
    # Dedupe e limita 2–3
    items = _dedup_news(items)
    return items[:3]


# ----------------------
# Resumo com LLM (Ollama gemma3:4b)
# ----------------------

def summarize_text(text: str) -> str:
    """Usa Ollama (gemma3:4b) via REST API; fallback simples se indisponível."""
    try:
        prompt = (
            "Resuma em 2 a 4 frases, em português do Brasil, destacando fato principal, impacto no setor de Autos/Carros,"
            " e quem/onde/quando se relevante. Seja conciso e objetivo. Texto:\n\n" + text
        )
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("response", "").strip()
        if content:
            return content
    except Exception as e:
        # log simplificado
        sys.stderr.write(f"[WARN] Ollama resumo falhou: {e}\n")
    # Fallback simples se Ollama indisponível
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    return ". ".join(sentences[:3]) + ("." if sentences else "")


# ----------------------
# Execução principal
# ----------------------

def collect_and_render_markdown() -> str:
    """Coleta termos Top + Rising e busca notícias por termo; retorna Markdown com tabela + resumo."""
    top_payload = fetch_trends("TOP_QUERIES")
    rising_payload = fetch_trends("RISING_QUERIES")

    top_terms = parse_terms_from_trends(top_payload, kind="Top")
    rising_terms = parse_terms_from_trends(rising_payload, kind="Rising")

    # Critério de qualidade: tentar cobrir pelo menos 80% (se vazio, avisa)
    coverage_note = ""
    if not top_terms and not rising_terms:
        coverage_note = "[ALERTA] Não foi possível obter termos do Trends."

    rows = []
    for typ, terms in [("Top", top_terms), ("Rising", rising_terms)]:
        for term in terms:
            news = fetch_news_for_term(term, num=6)
            for item in news:
                # Monta texto para resumo (título + fonte)
                brief = f"{item['title']} — {item['source']} ({item['date']})"
                summary = summarize_text(brief)
                rows.append({
                    "keyword": term,
                    "type": typ,
                    "title": item["title"],
                    "source": item["source"],
                    "link": item["link"],
                    "datetime": item["date"],
                    "day_tag": item["day_tag"],
                    "summary": summary,
                })

    # Ordena por dia_tag (D antes de D-1) e depois por keyword
    rows.sort(key=lambda r: (0 if r["day_tag"] == "D" else 1, r["keyword"].lower()))

    # Render Markdown
    header = (
        "# Monitoramento diário de tópicos e notícias: Setor “Autos / Carros”\n\n"
        "- Frequência: 2 coletas/dia (08:00 e 12:00) — TZ: " + TZ + "\n"
        "- Fonte Trends: categoria 47 (Autos). Período: " + DATE_RANGE + "\n"
        "- Fonte notícias: Google News (prioriza mais recentes do dia).\n\n"
    )

    table_header = (
        "| Palavra-chave | Tipo | Título | Fonte | Link | Data/Hora | Dia | Resumo |\n"
        "|---|---|---|---|---|---|---|---|\n"
    )

    table_rows = []
    for r in rows:
        link_md = f"[{r['link']}]({r['link']})" if r['link'] else ""
        table_rows.append(
            f"| {r['keyword']} | {r['type']} | {r['title']} | {r['source']} | {link_md} | {r['datetime']} | {r['day_tag']} | {r['summary']} |"
        )

    quality = (
        "\n\nObservações e critérios:\n"
        "- Priorizar notícias do dia (D); se não houver, permitir D-1 com marcação.\n"
        "- Remover duplicatas. Garantir 2–3 notícias por termo quando disponíveis.\n"
        "- Resumos objetivos; incluir fonte e link verificado (status 200).\n"
    )

    coverage = ("\n" + coverage_note + "\n") if coverage_note else "\n"

    return header + table_header + "\n".join(table_rows) + quality + coverage


if __name__ == "__main__":
    # Execução única (pode agendar via cron: 08:00 e 12:00)
    md = collect_and_render_markdown()
    print(md)
    # Se quiser salvar a saída:
    out_path = os.getenv("OUTPUT_MD_PATH", "GoogleTrends_Autos_Report.md")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"\n[OK] Relatório salvo em: {out_path}")
    except Exception as e:
        print(f"[WARN] Não foi possível salvar relatório: {e}")
