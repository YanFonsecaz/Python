# %%
import requests
import os
from langchain.agents import create_agent
from langchain_community.utilities.serpapi import SerpAPIWrapper
from IPython.display import Markdown

# Configurar chave da API
os.environ["SERPAPI_API_KEY"] = "78e8409a6968eddb86f3555587566424d0a7a92e2e8ae27db5b2c213093b5cd7"

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
        "api_key": os.environ["SERPAPI_API_KEY"]
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na requisição: {e}"}

# SerpAPI para Google News (mantém como estava)
news_tools = SerpAPIWrapper(
    serpapi_api_key=os.environ["SERPAPI_API_KEY"],
    params={
        "engine": "google_news",
        "hl": "pt-BR",
        "gl": "br",
        "num": 10,
    },
)

# Tema de pesquisa
tema = "Auto"

# Buscar tendências com parâmetros completos
print("=== BUSCANDO GOOGLE TRENDS ===")
tendencias = buscar_google_trends_completo(
    query=tema,
    hl="pt-BR",      # Português brasileiro
    geo="BR",        # Brasil
    date="today 12-m",  # Últimos 12 meses
    data_type="TIMESERIES"  # Interesse ao longo do tempo
)
print("Tendências:", tendencias)

# Buscar notícias
print("\n=== BUSCANDO GOOGLE NEWS ===")
noticias = news_tools.run(tema)
print("Notícias:", noticias)

# Criar agente para processar os dados
agent_buscador = create_agent(
    model="ollama:gemma3:4b",
    system_prompt=f"""
        Você é um assistente de análise de tendências em português do Brasil.
        Seu trabalho é:
        1. Analisar as tendências do Google Trends: {tendencias}
        2. Analisar as notícias do Google News: {noticias}
        3. Gerar as 10 palavras-chave mais importantes do tema em uma tabela formatada em markdown
        4. Criar um resumo didático do que está acontecendo no momento
        5. Devolver o output completo em Markdown, incluindo tabela + resumo
        
        IMPORTANTE: Seja conciso e objetivo. Evite repetições.
    """
)

# Processar com o agente
print("\n=== PROCESSANDO COM AGENTE ===")
resultado = agent_buscador.invoke({
    "messages": [{"role": "user", "content": f"Analise o tema '{tema}' e me dê o top 10 palavras-chave com resumo em tabela Markdown"}]
})


print("\n=== RESULTADO FINAL ===")
print(resultado['messages'][-1].content)
Markdown(resultado['messages'][-1].content)
# %%
