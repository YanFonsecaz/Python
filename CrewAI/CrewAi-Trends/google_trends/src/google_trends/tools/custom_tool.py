from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from serpapi import GoogleSearch
import os

class TrendsToolInput(BaseModel):
    categoria: str = Field(..., description="Categoria do Google Trends (ex: autos, carros )")
    top_n: int = Field(default=10, description="Número máximo de termos Top a coletar")
    rising_n: int = Field(default=10, description="Número máximo de Rising Queries a coletar")


class SERPTrendsTool(BaseTool):
    name: str = "SERPAPI_TrendsColletor"
    description: str = (
        "Coleta Top e Rising Queries do Google Trends usando SERPAPI"
    )
    args_schema: Type[BaseModel] = TrendsToolInput

    def _run(self, categoria: str, top_n: int = 10, rising_n: int = 10) -> list:
        """
        Coleta Top e Rising Related Queries do Google Trends via SERPAPI.

        Como funciona:
        - Normaliza a categoria (ex.: "47" ou "Autos"/"Carros") para um termo base (ex.: "carros").
        - Tenta obter Related Queries (top/rising) via engine google_trends.
        - Em caso de falha ou ausência de dados, faz fallback para Trending Now (daily) e retorna itens como 'top'.

        Retorno: lista de dicts com chaves {keyword, type, score}.
        """

        # Lê a chave do ambiente no momento da execução para garantir que .env já foi carregado
        serp_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERP_API_KEY")
        if not serp_key:
            raise ValueError("SERPAPI_API_KEY/SERP_API_KEY não definido no ambiente.")

        # 1) Normalização de categoria para termo base
        def normalizar_categoria(cat: str) -> str:
            c = (cat or "").strip().lower()
            if c in {"47", "autos", "carros", "automotivo", "automóveis", "automoveis"}:
                return "carros"
            return cat

        termo_base = normalizar_categoria(categoria)

        results: list[dict] = []

        # 2) Tentativa: RELATED_QUERIES
        try:
            rq_params = {
                "engine": "google_trends",
                "data_type": "RELATED_QUERIES",
                "q": termo_base,
                "hl": "pt",
                "geo": "BR",
                "date": "today 12-m",
                "api_key": serp_key,
            }
            data = GoogleSearch(rq_params).get_dict()

            # Verifica status e estrutura
            status = data.get("search_metadata", {}).get("status", "")
            related = data.get("related_queries", {}) if status == "Success" else {}

            top_items = related.get("top", [])[:top_n]
            for item in top_items:
                results.append({
                    "keyword": item.get("query"),
                    "type": "top",
                    "score": item.get("extracted_value") or item.get("value")
                })

            rising_items = related.get("rising", [])[:rising_n]
            for item in rising_items:
                results.append({
                    "keyword": item.get("query"),
                    "type": "rising",
                    "score": item.get("extracted_value") or item.get("value")
                })
        except Exception as e:
            # Continua para fallback se houver erro
            pass

        # 3) Fallback: Trending Now Daily (retorna itens como 'top')
        if not results:
            try:
                tn_params = {
                    "engine": "google_trends_trending_now",
                    "frequency": "daily",
                    "geo": "BR",
                    "hl": "pt",
                    "api_key": serp_key,
                }
                tn_data = GoogleSearch(tn_params).get_dict()
                daily = tn_data.get("daily_searches", [])
                if daily:
                    # Pega o primeiro dia e transforma as buscas em 'top'
                    searches = daily[0].get("searches", [])[:top_n]
                    for s in searches:
                        results.append({
                            "keyword": s.get("query"),
                            "type": "top",
                            "score": s.get("traffic")
                        })
            except Exception:
                # Se também falhar, mantém lista vazia
                pass

        return results



class NewsToolInput(BaseModel):
    keywords: list[str] = Field(..., description="Lista de palavras-chave")
    max_articles: int = Field(default=3, description="Número máximo de notícias por palavra-chave")

class SERPNewsTool(BaseTool):
    name: str = "SERPAPI_NewsFetcher"
    description: str = "Busca notícias do Google News via SERPAPI"
    args_schema: Type[BaseModel] = NewsToolInput

    def _run(self, keywords: list[str], max_articles: int = 3) -> list:
        """
        Busca notícias recentes no Google News via SERPAPI para uma lista de palavras-chave.

        - Define localização/idioma (gl=br, hl=pt-BR) para resultados do Brasil.
        - Ordena por data para priorizar notícias do dia.
        - Remove duplicatas por (title, link).

        Retorna: lista de dicts por palavra-chave: {"keyword": kw, "articles": [{title, link, source, date}...]}
        """
        serp_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERP_API_KEY")
        if not serp_key:
            raise ValueError("SERPAPI_API_KEY/SERP_API_KEY não definido no ambiente.")
        results = []
        for kw in keywords:
            params = {
                "engine": "google_news",
                "q": kw,
                "api_key": serp_key,
                "num": max_articles,
                "sort_by": "date",
                "gl": "br",
                "hl": "pt-BR",
            }
            search = GoogleSearch(params)
            data = search.get_dict()
            articles = []
            seen = set()
            for item in data.get("news_results", [])[:max_articles]:
                title = item.get("title")
                link = item.get("link")
                source = item.get("source")
                if isinstance(source, dict):
                    source = source.get("name")
                key = (title, link)
                if key in seen:
                    continue
                seen.add(key)
                articles.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "source": source,
                    "date": item.get("date")
                })
            results.append({"keyword": kw, "articles": articles})
        return results