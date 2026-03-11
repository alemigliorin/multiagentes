import os
import logging # Added for logging

from agno.agent import Agent
from agno.db.sqlite import SqliteDb # Original SqliteDb import
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.tavily import TavilyTools
from agno.knowledge.knowledge import Knowledge # Added
from agno.knowledge.reader.pdf_reader import PDFReader # Added
from agno.vectordb.chroma import ChromaDb # Added
from dotenv import load_dotenv

from media_tools import consultar_status_video, gerar_imagem, gerar_video
from reels_tools import get_creator_transcripts, list_available_creators

load_dotenv()


def get_model(provider: str = "openai", **kwargs):
    """
    Função dinâmica para ler as chaves e instanciar o provedor de LLM adequado.
    """
    provider = provider.lower()

    if provider == "openai":
        return OpenAIChat(id=kwargs.get("id", "gpt-4o"), api_key=os.getenv("OPENAI_API_KEY"))
    elif provider == "anthropic":
        return Claude(id=kwargs.get("id", "claude-3-5-sonnet-20241022"), api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif provider == "google":
        return Gemini(id=kwargs.get("id", "gemini-2.5-flash"), api_key=os.getenv("GOOGLE_API_KEY"))
    elif provider == "groq":
        return Groq(id=kwargs.get("id", "llama-3.3-70b-versatile"), api_key=os.getenv("GROQ_API_KEY"))
    elif provider == "deepseek":
        return DeepSeek(id=kwargs.get("id", "deepseek-chat"), api_key=os.getenv("DEEPSEEK_API_KEY"))

    # Default fallback
    return OpenAIChat(id="gpt-4o")

# --- SETUP DO BANCO DE DADOS VETORIAL (RAG PARA PDF) ---
pdf_vector_db = ChromaDb(collection="pdf_agent", path="tmp/chromadb", persistent_client=True)
pdf_knowledge = Knowledge(vector_db=pdf_vector_db)

# --- FERRAMENTAS DE PESQUISA CUSTOMIZADAS ---
def busca_rapida(query: str) -> str:
    """Usa a busca rápida e cirúrgica do Tavily para fatos simples, placares, cotações e notícias diárias.
    Extremamente rápida e imune a falhas de timeout.
    
    Args:
        query (str): A consulta de pesquisa.
    """
    try:
        tavily = TavilyTools(search_depth="basic", max_tokens=2000)
        return tavily.web_search_using_tavily(query)
    except Exception as e:
        return f"Erro na busca rápida: {e}"

def busca_profunda(query: str) -> str:
    """Busca profunda na internet usando Tavily. USE APENAS para pesquisa de conteúdo, análise de concorrentes ou quando precisar ler artigos densos.
    Atenção: É lenta e tem risco de timeout se usada muitas vezes.
    
    Args:
        query (str): A consulta de pesquisa detalhada.
    """
    try:
        tavily = TavilyTools(search_depth="advanced")
        return tavily.web_search_using_tavily(query)
    except Exception as e:
        return f"Erro na busca profunda: {e}"

# --- INSTANCIANDO OS AGENTES ESPECIALISTAS ---

pesquisador = Agent(
    model=get_model("openai", id="gpt-5-nano"),  # Modelo mais rápido/barato para pesquisa base
    name="pesquisador",
    description="Agente focado em buscar dados atuais na internet.",
    tools=[busca_rapida, busca_profunda],
    instructions=open("prompts/pesquisador.md", encoding="utf-8").read(),
    add_history_to_context=True,
    num_history_runs=5,
    db=SqliteDb(db_file="tmp/storage.db"),
)

copywriter = Agent(
    model=get_model("openai", id="gpt-5-nano"),  # Bom para seguir estilos
    name="copywriter",
    description="Agente Copywriter que busca no RAG o estilo do expert e escreve.",
    tools=[get_creator_transcripts, list_available_creators],
    instructions=open("prompts/copywriter.md", encoding="utf-8").read(),
    add_history_to_context=True,
    num_history_runs=10,
    db=SqliteDb(db_file="tmp/storage.db"),
)

juridico = Agent(
    model=get_model("openai", id="gpt-5-nano"),
    name="juridico",
    description="Especialista em compliance e leis de defesa do consumidor.", # Modified description
    instructions=open("prompts/juridico.md", encoding="utf-8").read(),
    add_history_to_context=True,
    num_history_runs=3, # Modified num_history_runs
    db=SqliteDb(db_file="tmp/storage.db"),
)

# --- AGENTE DE PDF (RAG) --- # Added
agente_pdf = Agent(
    model=get_model("openai", id="gpt-5-nano"),
    name="agente_pdf",
    description="Agente especializado em ler, analisar e extrair informações precisas de PDFs.",
    knowledge=pdf_knowledge,
    search_knowledge=True,
    instructions=open("prompts/agente_pdf.md", encoding="utf-8").read(),
    add_history_to_context=True,
    num_history_runs=3,
    db=SqliteDb(db_file="tmp/storage.db"),
)

criador_experts = Agent(
    model=get_model("openai", id="gpt-5-nano"),  # Claude costuma ser melhor para brainstoming criativo/personas
    name="criador_experts",
    description="Agente estrategista para criar Personas e Big Ideas.",
    instructions=open("prompts/criador_experts.md", encoding="utf-8").read(),
    add_history_to_context=True,
    num_history_runs=5,
    db=SqliteDb(db_file="tmp/storage.db"),
)

criador_midia = Agent(
    model=get_model("google", id="gemini-2.5-flash"),
    name="criador_midia",
    description="Agente focado na interpretação de ordens visuais e geração de imagens/vídeos. Gerencia filas de vídeos longos (Veo).",
    tools=[gerar_imagem, gerar_video, consultar_status_video],
    instructions=open("prompts/criador_midia.md", encoding="utf-8").read(),
    add_history_to_context=True,
    num_history_runs=10,
    db=SqliteDb(db_file="tmp/storage.db"),
)

# --- DELEGAÇÃO DE TAREFAS (FERRAMENTAS PARA O ORQUESTRADOR) ---


def acionar_pesquisador(query: str) -> str:
    """Delega uma tarefa de busca de dados reais e atualizados na internet ao Pesquisador.
    NÃO USE ESTA FERRAMENTA para buscar informações em PDFs, relatórios corporativos internos (ex: relatórios trimestrais, resultados), ou documentos específicos baixados/armazenados no sistema. Nesses casos, prefira SEMPRE acionar_agente_pdf.

    Args:
        query (str): A pergunta, tópico ou instrução exata para a pesquisa na web.
    """
    import time
    start_time = time.time()
    print(f"--- Iniciando pesquisa: {query} ---")
    response = pesquisador.run(query)
    duration = time.time() - start_time
    print(f"--- Pesquisa concluída em {duration:.2f}s ---")
    return response.content


def acionar_copywriter(instrucao: str) -> str:
    """Delega a tarefa de escrita persuasiva e criação de roteiros usando a voz do Expert ao Copywriter.

    Args:
        instrucao (str): O tópico ou as informações base para escrever o conteúdo.
    """
    response = copywriter.run(instrucao)
    return response.content


def acionar_juridico(conteudo: str) -> str:
    """Delega a tarefa de revisão de compliance e limites legais de uma promessa ou texto ao Jurídico.

    Args:
        conteudo (str): O texto, roteiro ou promessa que precisa ser revisada.
    """
    response = juridico.run(conteudo)
    return response.content


def acionar_criador_experts(tarefa: str) -> str:
    """Delega a criação de identidade, big idea ou estratégia visual de um projeto ao Criador_Experts.

    Args:
        tarefa (str): A instrução do que deve ser planejado ou criado para o expert.
    """
    response = criador_experts.run(tarefa)
    return response.content


def acionar_criador_midia(instrucao: str) -> str:
    """Delega tarefas de criação audiovisual (imagens e vídeos) ao agente Criador de Mídia.

    Args:
        instrucao (str): O detalhamento visual ou cena que precisa ser gerado como mídia (ex: foto, cena, vídeo).
    """
    response = criador_midia.run(instrucao)
    return response.content

# --- DELEGAÇÃO DE TAREFAS (FERRAMENTAS PARA O ORQUESTRADOR) --- # Added
def acionar_agente_pdf(query: str) -> str:
    """Delega a tarefa de consulta e análise de documentos internos corporativos (PDFs) locais ao Agente PDF.
    USE ESTA FERRAMENTA quando o usuário perguntar sobre relatórios financeiros, resultados trimestrais de empresas específicas (ex: Grendene) ou documentos que já foram carregados internamente no sistema, ANTES de tentar buscar na internet.

    Args:
        query (str): A pergunta ou instrução para o Agente PDF sobre o conteúdo dos documentos.
    """
    response = agente_pdf.run(query)
    return response.content

# --- INSTANCIANDO O ORQUESTRADOR ---
orquestrador = Agent(
    model=get_model("openai", id="gpt-5-mini"),  # GPT-5 mini atua como líder da orquestração
    tools=[acionar_pesquisador, acionar_copywriter, acionar_juridico, acionar_criador_experts, acionar_criador_midia, acionar_agente_pdf], # Added acionar_agente_pdf
    name="orquestrador",
    description="Você é o Líder da Equipe e principal contato. Você delega tarefas e consolida o resultado final.",
    instructions=open("prompts/orquestrador.md", encoding="utf-8").read(),
    add_history_to_context=True,
    num_history_runs=20,
    db=SqliteDb(db_file="tmp/storage.db"),
)

# --- CARREGAMENTO INICIAL DE CONHECIMENTO (PDF) --- # Added
logging.info("Aguarde... Carregando dados no AgentOS e preparando times")

# Adicionando o PDF estático do Grendene para prova de conceito
try:
    logging.info("Carregando PDF da Grendene no Banco de Conhecimento...")
    pdf_knowledge.add_content(
        url="https://s3.sa-east-1.amazonaws.com/static.grendene.aatb.com.br/releases/2417_2T25.pdf",
        metadata={"source": "Grendene", "type":"pdf", "description": "Relatório Trimestral 2T25"},
        skip_if_exists=True,
        reader=PDFReader()
    )
    logging.info("PDF carregado/verificado!")
except Exception as e:
    logging.error(f"Erro ao carregar PDF: {e}")


allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3001,http://localhost:3000,http://127.0.0.1:3001").split(
    ","
)
# Expondo apenas o orquestrador no AgentOS
agent_os = AgentOS(agents=[orquestrador], cors_allowed_origins=allowed_origins)
app = agent_os.get_app()

from starlette.middleware.base import BaseHTTPMiddleware
from auth import auth_middleware

app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
