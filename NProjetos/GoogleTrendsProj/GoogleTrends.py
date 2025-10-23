# %%
from langchain.agents import create_agent
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper
from langchain_community.utilities.serpapi import SerpAPIWrapper
import os

os.environ["SERPAPI_API_KEY"] = "78e8409a6968eddb86f3555587566424d0a7a92e2e8ae27db5b2c213093b5cd7"

toolGoogleTrends = GoogleTrendsQueryRun(
    api_wrapper=GoogleTrendsAPIWrapper(
        serp_api_key=os.environ["SERPAPI_API_KEY"],
    )
)

# SerpAPI (Google News via engine)
news_tools = SerpAPIWrapper(
    serpapi_api_key=os.environ["SERPAPI_API_KEY"],
    params={
        "engine": "google_news",
        "hl": "pt-BR",
        "gl": "br",
        "num": 10,
    },
)

tema = "Auto"
tendencias = toolGoogleTrends.invoke(tema)
print(tendencias)

# Para utilitário SerpAPIWrapper, use .run em vez de .invoke
noticias = news_tools.run(tema)
print(noticias)



agent_buscador = create_agent(
    model="ollama:gemma3:4b",
    system_prompt=f"""
        Você é um assistente de busca de tendências e notificas em português do Brasil.
        Seu trabalho é:
        1. Receber as tendências do Google Trends: {tendencias}.
        2. Receber as notícias do Google News: {noticias}.
        3. Gerar as 10 palavras-chave mais importantes do tema em uma tabela formatada em markdown.
        4.Criar um resumo didatico do que esta no momento.
        5. Devolver o output completo em Markdown, incluindo tabela + resumo
    """
)

resultado = agent_buscador.invoke({"messages": [{"role": "user", "content": f"Me de o top 10 do tema '{tema}' com resumo e tabela Markdown"}]})
print(resultado['messages'][-1].content)

# %%
