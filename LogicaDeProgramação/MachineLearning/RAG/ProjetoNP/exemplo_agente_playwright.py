"""
Exemplo de uso do Agente Extrator com ferramentas Playwright
Este arquivo demonstra como usar o agente CrewAI com as ferramentas personalizadas do Playwright.
"""

from crewai import Agent, Task, Crew
from crewai.llm import LLM
from playwright_tools import PLAYWRIGHT_TOOLS

# Configuração do LLM (Ollama)
llm = LLM(model="ollama/gemma3:4b", base_url="http://localhost:11434")

# Definição do Agente Extrator com ferramentas Playwright
Agent_Extrair_Conteudo = Agent(
    role="Especialista em Extração de Conteúdo Web",
    goal="Extrair e analisar conteúdo de páginas web usando ferramentas avançadas do Playwright",
    backstory="""Você é um agente especializado em extrair conteúdo de páginas web usando automação 
    de navegador com Playwright. Você possui as seguintes habilidades:
    
    1. Navegar para qualquer página web e aguardar o carregamento completo
    2. Extrair texto de páginas inteiras ou elementos específicos usando seletores CSS
    3. Capturar screenshots de páginas para documentação visual
    4. Preencher e submeter formulários automaticamente
    
    Você sempre verifica se a página carregou corretamente antes de extrair informações e 
    fornece feedback detalhado sobre suas ações.""",
    tools=PLAYWRIGHT_TOOLS,
    allow_delegation=False,
    llm=llm,
    verbose=True
)

# Exemplo de Task para extrair conteúdo
task_extrair_conteudo = Task(
    description="""
    Acesse o site https://example.com e execute as seguintes ações:
    
    1. Navegue até a página e confirme que carregou corretamente
    2. Extraia todo o texto da página
    3. Capture um screenshot da página
    4. Forneça um resumo do conteúdo encontrado
    
    Seja detalhado em suas ações e explique o que encontrou.
    """,
    agent=Agent_Extrair_Conteudo,
    expected_output="Relatório detalhado com o conteúdo extraído, confirmação do screenshot capturado e resumo das informações encontradas na página."
)

# Exemplo de Task para interagir com formulário
task_preencher_formulario = Task(
    description="""
    Acesse uma página com formulário de busca e execute as seguintes ações:
    
    1. Navegue até https://httpbin.org/forms/post
    2. Preencha o formulário com dados de teste
    3. Capture um screenshot antes e depois do preenchimento
    4. Relate o resultado da operação
    
    Use dados fictícios apropriados para o teste.
    """,
    agent=Agent_Extrair_Conteudo,
    expected_output="Relatório da interação com o formulário, incluindo screenshots e confirmação do preenchimento."
)

# Criação da Crew
crew = Crew(
    agents=[Agent_Extrair_Conteudo],
    tasks=[task_extrair_conteudo],  # Você pode adicionar task_preencher_formulario também
    verbose=True
)

# Função para executar o exemplo
def executar_exemplo():
    """
    Executa o exemplo de extração de conteúdo.
    Certifique-se de que o Ollama está rodando antes de executar.
    """
    print("🚀 Iniciando exemplo de extração de conteúdo com Playwright...")
    print("📋 Verificando se o Ollama está rodando em http://localhost:11434")
    
    try:
        # Executar a crew
        resultado = crew.kickoff()
        
        print("✅ Exemplo executado com sucesso!")
        print("📄 Resultado:")
        print(resultado)
        
    except Exception as e:
        print(f"❌ Erro ao executar o exemplo: {str(e)}")
        print("💡 Dicas para resolver:")
        print("   1. Verifique se o Ollama está rodando: ollama serve")
        print("   2. Verifique se o modelo está disponível: ollama pull gemma3:4b")
        print("   3. Certifique-se de que o ambiente virtual está ativo")

if __name__ == "__main__":
    executar_exemplo()