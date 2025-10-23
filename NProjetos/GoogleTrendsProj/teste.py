
from crewai import Agent, Task, Crew, LLM
from crewai import LMM
from IPython.display import Markdown
from crwcrewai_tools import tool

@tool("GoogleTrendsTools")
def google_trends(topic:str) -> str:
    f"""
    Consulta tendências no Google Trends para um {topic} e retorna um resumo em Markdown.
    """
    return f"Consulta tendências no Google Trends para um {topic} e retorna um resumo em Markdown."

# Use o wrapper LLM do CrewAI com provider 'ollama' (compatível com o executor interno)
llm = LLM(model="ollama/gemma3:4b", base_url="http://localhost:11434")
import os


os.environ["SERPAPI_API_KEY"] = "78e8409a6968eddb86f3555587566424d0a7a92e2e8ae27db5b2c213093b5cd7"

toolGoogleTrends = GoogleTrendsQueryRun(api_wrapper=GoogleTrendsAPIWrapper())

agent_buscador = Agent(
    role="Busca de Tendências",
    goal="Buscar tendências no Google Trends sobre o {topic}",
    backstory="""
        Você está buscando tendências no Google Trends sobre o tópico: {topic}.
        Você coleta informações que ajudam a entender a tendência do público.
    """,
    allow_delegation=False,
    verbose=True,
    llm=llm,
    tools=[toolGoogleTrends],
)
task_busca = Task(
    description="Buscar tendências no Google Trends sobre o {topic}",
    agent=agent_buscador,
    expected_output="Lista de tendências no Google Trends sobre o {topic}"
)

crew = Crew(
    agents=[agent_buscador],
    tasks=[task_busca],
    verbose=True,
)

result = crew.kickoff(inputs={"topic": "IA"})

Markdown(result.raw)
