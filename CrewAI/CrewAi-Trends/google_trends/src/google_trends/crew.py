from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv
from pathlib import Path
import agentops
import os
from google_trends.tools.custom_tool import SERPTrendsTool, SERPNewsTool
# Carrega variáveis do .env local ao pacote e também do ambiente atual
_dotenv_pkg_path = Path(__file__).parent / ".env"
load_dotenv(_dotenv_pkg_path)
load_dotenv()

AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
# Inicializa AgentOps apenas se houver chave configurada
if AGENTOPS_API_KEY:
    agentops.init(api_key=AGENTOPS_API_KEY)

llm = LLM(
    model=os.getenv("OPENAI_MODEL_NAME"),
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY"),
)


@CrewBase
class GoogleTrends():
    """GoogleTrends crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    
    @agent
    def Agent_ColetorTrends(self) -> Agent:
        return Agent(
            config=self.agents_config['Agent_ColetorTrends'], # type: ignore[index]
            verbose=True,
            # Usa ferramenta personalizada para coletar Top/Rising via SERPAPI
            tools=[SERPTrendsTool()],
            llm=llm,
        )

    @agent
    def Agent_BuscadorNoticias(self) -> Agent:
        return Agent(
            config=self.agents_config['Agent_BuscadorNoticias'], # type: ignore[index]
            # Usa ferramenta personalizada para buscar notícias no Google News
            tools=[SERPNewsTool()],
            verbose=True,
            llm=llm,
        )

    @agent
    def Agent_De_Resumo(self) -> Agent:
        return Agent(
            config=self.agents_config['Agent_De_Resumo'], # type: ignore[index]
            verbose=True,
            llm=llm,
        )

    @agent
    def Agent_Reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['Agent_Reporter'], # type: ignore[index]
            verbose=True,
            llm=llm,
        )

    @task
    def Task_ColetorTrends(self) -> Task:
        return Task(
            config=self.tasks_config['Task_ColetorTrends'], # type: ignore[index]
        )

    @task
    def Task_BuscadorNoticias(self) -> Task:
        return Task(
            config=self.tasks_config['Task_BuscadorNoticias'], # type: ignore[index]
            
        )

    @task
    def Task_Resumo(self) -> Task:
        return Task(
            config=self.tasks_config['Task_Resumo'], # type: ignore[index]
            
        )

    @task
    def Task_Reporting(self) -> Task:
        return Task(
            config=self.tasks_config['Task_Reporting'], # type: ignore[index]
            # Mantém alinhado ao tasks.yaml
            output_file='resultado/Noticias.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the GoogleTrends crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
