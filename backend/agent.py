import logging
import os
import re
import shutil
import time
import traceback
from pathlib import Path

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.tavily import TavilyTools
from agno.vectordb.pgvector import PgVector
from dotenv import load_dotenv
from fastapi import File, Form, UploadFile
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from auth import auth_middleware
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
def get_pdf_knowledge():
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        return None
    try:
        pdf_vector_db = PgVector(table_name="pdf_documents", db_url=db_url)
        return Knowledge(vector_db=pdf_vector_db)
    except Exception as e:
        logging.error(f"Erro ao inicializar base de conhecimento PDF: {e}")
        return None

pdf_knowledge = get_pdf_knowledge()


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
def create_agent(name, description, tools=None, instructions_file=None, db_url=None, **kwargs):
    model = kwargs.get("model") or get_model("openai", id="gpt-4o")
    
    db = None
    if db_url:
        try:
            db = PostgresDb(session_table="sessions", db_url=db_url)
        except Exception:
            logging.warning(f"Could not initialize DB for agent {name}")

    instructions = ""
    if instructions_file:
        try:
            with open(instructions_file, encoding="utf-8") as f:
                instructions = f.read()
        except FileNotFoundError:
            logging.error(f"Instructions file not found: {instructions_file}")

    return Agent(
        model=model,
        name=name,
        description=description,
        tools=tools,
        instructions=instructions,
        db=db,
        add_history_to_context=kwargs.get("add_history_to_context", True),
        num_history_runs=kwargs.get("num_history_runs", 5),
        **{k: v for k, v in kwargs.items() if k not in ["model", "add_history_to_context", "num_history_runs"]}
    )

supabase_db_url = os.getenv("SUPABASE_DB_URL")

pesquisador = create_agent(
    name="pesquisador",
    model=get_model("openai", id="gpt-5-nano"),
    description="Agente focado em buscar dados atuais na internet.",
    tools=[busca_rapida, busca_profunda],
    instructions_file="prompts/pesquisador.md",
    db_url=supabase_db_url
)

copywriter = create_agent(
    name="copywriter",
    model=get_model("openai", id="gpt-5-nano"),
    description="Agente Copywriter que busca no RAG o estilo do expert e escreve.",
    tools=[get_creator_transcripts, list_available_creators],
    instructions_file="prompts/copywriter.md",
    db_url=supabase_db_url,
    num_history_runs=10
)

juridico = create_agent(
    name="juridico",
    model=get_model("openai", id="gpt-5-nano"),
    description="Especialista em compliance e leis de defesa do consumidor.",
    instructions_file="prompts/juridico.md",
    db_url=supabase_db_url,
    num_history_runs=3
)

agente_pdf = create_agent(
    name="agente_pdf",
    model=get_model("openai", id="gpt-5-nano"),
    description="Agente especializado em ler, analisar e extrair informações precisas de PDFs.",
    knowledge=pdf_knowledge,
    search_knowledge=True,
    instructions_file="prompts/agente_pdf.md",
    db_url=supabase_db_url,
    num_history_runs=3
)

criador_experts = create_agent(
    name="criador_experts",
    model=get_model("openai", id="gpt-5-nano"),
    description="Agente estrategista para criar Personas e Big Ideas.",
    instructions_file="prompts/criador_experts.md",
    db_url=supabase_db_url
)

criador_midia = create_agent(
    name="criador_midia",
    model=get_model("google", id="gemini-2.0-flash"),
    description="Agente focado na interpretação de ordens visuais e geração de imagens/vídeos. Gerencia filas de vídeos longos (Veo).",
    tools=[gerar_imagem, gerar_video, consultar_status_video],
    instructions_file="prompts/criador_midia.md",
    db_url=supabase_db_url,
    num_history_runs=10
)

# --- DELEGAÇÃO DE TAREFAS (FERRAMENTAS PARA O ORQUESTRADOR) ---


def acionar_pesquisador(query: str) -> str:
    """Delega uma tarefa de busca de dados reais e atualizados na internet ao Pesquisador.
    NÃO USE ESTA FERRAMENTA para buscar informações em PDFs, relatórios corporativos internos (ex: relatórios trimestrais, resultados), ou documentos específicos baixados/armazenados no sistema. Nesses casos, prefira SEMPRE acionar_agente_pdf.

    Args:
        query (str): A pergunta, tópico ou instrução exata para a pesquisa na web.
    """
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
    model=get_model("openai", id="gpt-5-mini"),
    tools=[
        acionar_pesquisador,
        acionar_copywriter,
        acionar_juridico,
        acionar_criador_experts,
        acionar_criador_midia,
        acionar_agente_pdf,
    ],
    name="orquestrador",
    description="Você é o Líder da Equipe e principal contato. Você delega tarefas e consolida o resultado final.",
    instructions=open("prompts/orquestrador.md", encoding="utf-8").read() if os.path.exists("prompts/orquestrador.md") else "Instruções não encontradas.",
    add_history_to_context=True,
    num_history_runs=20,
    db=PostgresDb(session_table="sessions", db_url=supabase_db_url) if supabase_db_url else None,
)

# --- CARREGAMENTO INICIAL DE CONHECIMENTO (PDF) --- # Added
if pdf_knowledge:
    logging.info("Carregando PDF da Grendene no Banco de Conhecimento...")
    try:
        pdf_knowledge.add_content(
            url="https://s3.sa-east-1.amazonaws.com/static.grendene.aatb.com.br/releases/2417_2T25.pdf",
            metadata={"source": "Grendene", "type": "pdf", "description": "Relatório Trimestral 2T25"},
            skip_if_exists=True,
            reader=PDFReader(),
        )
        logging.info("PDF carregado/verificado!")
    except Exception as e:
        logging.error(f"Erro ao carregar PDF: {e}")

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3001,http://localhost:3000,http://127.0.0.1:3001").split(",")
# Expondo apenas o orquestrador no AgentOS
agent_os = AgentOS(agents=[orquestrador], cors_allowed_origins=allowed_origins)
app = agent_os.get_app()

app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), save_to_rag: str = Form("false")):
    try:
        temp_dir = Path("tmp/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if save_to_rag.lower() == "true":
            # Salvar no banco vetorial
            pdf_knowledge.add_content(path=str(file_path), reader=PDFReader())
            file_path.unlink()
            return {"status": "success", "mode": "rag", "message": "Salvo na Base de Dados"}
        else:
            # Modo temporário: apenas extrair e retornar o texto
            reader = PDFReader()
            documents = reader.read(pdf=str(file_path))
            extracted_text = "\n\n".join([doc.content for doc in documents if doc.content])
            file_path.unlink()
            return {"status": "success", "mode": "temporary", "extracted_text": extracted_text}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...), creator_name: str = Form(...)):
    try:
        if not creator_name.strip():
            return JSONResponse(status_code=400, content={"error": "Nome do criador é obrigatório"})

        safe_creator_name = re.sub(r"[^a-zA-Z0-9_\-]", "", creator_name.replace(" ", "_").lower())

        video_dir = Path(f"videos/{safe_creator_name}")
        video_dir.mkdir(parents=True, exist_ok=True)

        file_path = video_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"status": "success", "message": f"Vídeo salvo em {file_path}", "path": str(file_path)}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
