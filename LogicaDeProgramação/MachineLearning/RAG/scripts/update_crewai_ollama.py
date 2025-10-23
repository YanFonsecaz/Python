#!/usr/bin/env python3
"""
Atualiza o notebook "CrewAI copy.ipynb" para:
- Usar Ollama via ChatOllama com o modelo gemma3:4b
- Traduzir o conteúdo (roles, goals, backstories, descriptions, outputs) para português
- Injetar o LLM nos agentes
- Configurar variáveis de ambiente para o litellm com provider Ollama
- Definir OPENAI_* para o uso via litellm com provider 'ollama'
"""
import nbformat as nbf
from typing import Optional, List

NOTEBOOK_PATH = "CrewAI copy.ipynb"

# --- Helpers ---

def _cell_source_to_str(cell) -> str:
    """Retorna o conteúdo de uma célula como string única, independente do formato."""
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return src or ""


def _set_cell_source(cell, lines: List[str]) -> None:
    """Define o 'source' da célula usando uma lista de linhas (cada uma terminando com \n)."""
    cell["source"] = lines


def _find_code_cell_index(nb, marker: str) -> Optional[int]:
    """Encontra o índice da primeira célula de código que contenha o marcador fornecido."""
    for i, c in enumerate(nb["cells"]):
        if c.get("cell_type") == "code":
            if marker in _cell_source_to_str(c):
                return i
    return None


# --- Novos conteúdos das células ---

IMPORTS_CELL_LINES = [
    "from crewai import Agent, Task, Crew\n",
    "from IPython.display import Markdown\n",
    "from crewai.llm import LLM\n",
]

ENV_LLМ_CELL_LINES = [
    "# Instância do LLM via CrewAI LLM (Ollama)\n",
    "llm = LLM(model=\"ollama/gemma3:4b\", base_url=\"http://localhost:11434\")\n",
]

LLM_CELL_LINES = [
    "# Configura o LLM local via Ollama (model: gemma3:4b)\n",
    "llm = LLM(model=\"ollama/gemma3:4b\", base_url=\"http://localhost:11434\")\n",
]

PLANNER_CELL_LINES = [
    "planner = Agent(\n",
    "    role=\"Planejador de Conteúdo\",\n",
    "    goal=\"Planejar conteúdo envolvente e factual sobre o {topic}\",\n",
    "    backstory=\"\"\"\n",
    "        Você está trabalhando no planejamento de um artigo de blog sobre o tópico: {topic}.\n",
    "        Você coleta informações que ajudam o público a aprender algo e tomar decisões informadas.\n",
    "        Seu trabalho é a base para o Escritor de Conteúdo escrever o artigo sobre esse tópico.\n",
    "    \"\"\",\n",
    "    allow_delegation=False,\n",
    "    verbose=True,\n",
    "    llm=llm,\n",
    ")\n",
]

WRITER_CELL_LINES = [
    "writer = Agent(\n",
    "    role=\"Escritor de Conteúdo\",\n",
    "    goal=\"Escrever um artigo opinativo informativo e baseado em fatos sobre o {topic}\",\n",
    "    backstory=\"\"\"\n",
    "        Você está escrevendo uma opinião sobre o tópico: {topic}.\n",
    "        Você baseia sua opinião no trabalho do Planejador de Conteúdo, que fornece um roteiro e contexto relevante.\n",
    "        Você segue os principais objetivos e a direção do roteiro, conforme fornecido pelo Planejador.\n",
    "        Você também oferece insights objetivos e imparciais, apoiados por informações fornecidas pelo Planejador.\n",
    "    \"\"\",\n",
    "    allow_delegation=False,\n",
    "    verbose=True,\n",
    "    llm=llm,\n",
    ")\n",
]

EDITOR_CELL_LINES = [
    "editor = Agent(\n",
    "    role=\"Editor\",\n",
    "    goal=\"Editar o artigo para alinhar com o estilo de escrita da organização.\",\n",
    "    backstory=\"\"\"\n",
    "        Você é um editor que recebe um artigo do Escritor de Conteúdo.\n",
    "        Seu objetivo é revisar o artigo para garantir que segue as melhores práticas jornalísticas.\n",
    "    \"\"\",\n",
    "    allow_delegation=False,\n",
    "    verbose=True,\n",
    "    llm=llm,\n",
    ")\n",
]

PLAN_TASK_CELL_LINES = [
    "plan = Task(\n",
    "    description=(\n",
    "        \"1. Priorize as últimas tendências, principais players e notícias relevantes sobre {topic}.\"\n",
    "        \"2. Identifique o público-alvo, considerando seus interesses e dores.\"\n",
    "        \"3. Desenvolva um roteiro detalhado incluindo introdução, pontos-chave e chamada para ação.\"\n",
    "        \"4. Inclua palavras-chave de SEO e dados ou fontes relevantes.\"\n",
    "    ),\n",
    "    expected_output=\"Um plano de conteúdo abrangente com roteiro, análise de público, palavras-chave de SEO e recursos.\",\n",
    "    agent=planner,\n",
    ")\n",
]

WRITE_TASK_CELL_LINES = [
    "write = Task(\n",
    "    description=(\n",
    "        \"1. Use o plano de conteúdo para elaborar um artigo de blog atraente sobre {topic}.\"\n",
    "        \"2. Incorpore as palavras-chave de SEO de forma natural.\"\n",
    "        \"3. Nomeie seções/subtítulos de maneira envolvente e clara.\"\n",
    "        \"4. Garanta uma estrutura com introdução envolvente, corpo com insights e conclusão resumida.\"\n",
    "    ),\n",
    "    expected_output=\"Um artigo bem estruturado em Markdown, pronto para publicação; cada seção deve ter 2–3 parágrafos.\",\n",
    "    agent=writer,\n",
    ")\n",
]

EDIT_TASK_CELL_LINES = [
    "edit = Task(\n",
    "    description=(\n",
    "        \"Revisar o artigo de blog para correções gramaticais e alinhamento com a voz da marca.\"\n",
    "    ),\n",
    "    expected_output=\"Um artigo bem escrito em Markdown, pronto para publicação.\",\n",
    "    agent=editor,\n",
    ")\n",
]

KICKOFF_CELL_LINES = [
    "result = crew.kickoff(inputs={\"topic\": \"O Futuro da IA na Saúde\"})\n",
]


# --- Atualização principal ---

def update_notebook(path: str) -> None:
    """Carrega o notebook, aplica as alterações e salva o resultado."""
    nb = nbf.read(path, as_version=4)

    # 1) Imports: substituir a célula que contém 'from crewai import Agent, Task, Crew'
    idx_imports = _find_code_cell_index(nb, "from crewai import Agent, Task, Crew")
    if idx_imports is not None:
        _set_cell_source(nb["cells"][idx_imports], IMPORTS_CELL_LINES)

    # 2) Substituir célula de env OpenAI por configuração do llm (Ollama via litellm)
    idx_env = _find_code_cell_index(nb, "OPENAI_API_KEY")
    if idx_env is None:
        # fallback: procurar OPENAI_MODEL_NAME
        idx_env = _find_code_cell_index(nb, "OPENAI_MODEL_NAME")
    if idx_env is not None:
        _set_cell_source(nb["cells"][idx_env], ENV_LLМ_CELL_LINES)
    # 2b) Garantir célula de configuração do LLM (ChatOllama com base_url)
    idx_llm = _find_code_cell_index(nb, "llm = ChatOllama(")
    if idx_llm is None:
        idx_llm = _find_code_cell_index(nb, "llm = LLM(")
    if idx_llm is not None:
        _set_cell_source(nb["cells"][idx_llm], LLM_CELL_LINES)

    # 3) Agentes em português com llm injetado
    idx_planner = _find_code_cell_index(nb, "planner = Agent(")
    if idx_planner is not None:
        _set_cell_source(nb["cells"][idx_planner], PLANNER_CELL_LINES)

    idx_writer = _find_code_cell_index(nb, "writer = Agent(")
    if idx_writer is not None:
        _set_cell_source(nb["cells"][idx_writer], WRITER_CELL_LINES)

    idx_editor = _find_code_cell_index(nb, "editor = Agent(")
    if idx_editor is not None:
        _set_cell_source(nb["cells"][idx_editor], EDITOR_CELL_LINES)

    # 4) Tarefas traduzidas
    idx_plan_task = _find_code_cell_index(nb, "plan = Task(")
    if idx_plan_task is not None:
        _set_cell_source(nb["cells"][idx_plan_task], PLAN_TASK_CELL_LINES)

    idx_write_task = _find_code_cell_index(nb, "write = Task(")
    if idx_write_task is not None:
        _set_cell_source(nb["cells"][idx_write_task], WRITE_TASK_CELL_LINES)

    idx_edit_task = _find_code_cell_index(nb, "edit = Task(")
    if idx_edit_task is not None:
        _set_cell_source(nb["cells"][idx_edit_task], EDIT_TASK_CELL_LINES)

    # 5) Kickoff com tópico em português
    idx_kickoff = _find_code_cell_index(nb, "crew.kickoff(")
    if idx_kickoff is not None:
        _set_cell_source(nb["cells"][idx_kickoff], KICKOFF_CELL_LINES)

    # Salvar
    nbf.write(nb, path)
    print("Notebook atualizado: Ollama (gemma3:4b) e conteúdo em português; usando crewai.llm.LLM com base_url e sem variáveis litellm/OPENAI_*.")


if __name__ == "__main__":
    update_notebook(NOTEBOOK_PATH)