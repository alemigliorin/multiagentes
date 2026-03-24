from agents.factory import create_agent, get_model
from config.settings import settings
from knowledge.pdf_knowledge import get_pdf_knowledge
from knowledge.tavily import busca_profunda, busca_rapida
from media_tools import consultar_status_video, gerar_imagem, gerar_video
from reels_tools import get_creator_transcripts, list_available_creators


# --- PESQUISADOR ---
def get_pesquisador():
    return create_agent(
        name="pesquisador",
        model=get_model("openai", id=settings.DEFAULT_MODEL_ID),
        description="Agente focado em buscar dados atuais na internet.",
        tools=[busca_rapida, busca_profunda],
        instructions_file="prompts/pesquisador.md",
        db_url=settings.SUPABASE_DB_URL
    )

# --- COPYWRITER ---
def get_copywriter():
    return create_agent(
        name="copywriter",
        model=get_model("openai", id=settings.DEFAULT_MODEL_ID),
        description="Agente Copywriter que busca no RAG o estilo do expert e escreve.",
        tools=[get_creator_transcripts, list_available_creators],
        instructions_file="prompts/copywriter.md",
        db_url=settings.SUPABASE_DB_URL,
        num_history_runs=10
    )

# --- JURÍDICO ---
def get_juridico():
    return create_agent(
        name="juridico",
        model=get_model("openai", id=settings.DEFAULT_MODEL_ID),
        description="Especialista em compliance e leis de defesa do consumidor.",
        instructions_file="prompts/juridico.md",
        db_url=settings.SUPABASE_DB_URL,
        num_history_runs=3
    )

# --- CRIADOR EXPERTS ---
def get_criador_experts():
    return create_agent(
        name="criador_experts",
        model=get_model("openai", id=settings.DEFAULT_MODEL_ID),
        description="Agente estrategista para criar Personas e Big Ideas.",
        instructions_file="prompts/criador_experts.md",
        db_url=settings.SUPABASE_DB_URL
    )

# --- CRIADOR MÍDIA ---
def get_criador_midia():
    return create_agent(
        name="criador_midia",
        model=get_model("google", id=settings.CRIADOR_MIDIA_MODEL_ID),
        description="Agente focado na interpretação de ordens visuais e geração de imagens/vídeos. Gerencia filas de vídeos longos (Veo).",
        tools=[gerar_imagem, gerar_video, consultar_status_video],
        instructions_file="prompts/criador_midia.md",
        db_url=settings.SUPABASE_DB_URL,
        num_history_runs=10,
    )

# --- AGENTE PDF ---
def get_agente_pdf():
    return create_agent(
        name="agente_pdf",
        model=get_model("openai", id=settings.DEFAULT_MODEL_ID),
        description="Agente especializado em ler, analisar e extrair informações precisas de PDFs.",
        knowledge=get_pdf_knowledge(),
        search_knowledge=True,
        instructions_file="prompts/agente_pdf.md",
        db_url=settings.SUPABASE_DB_URL,
        num_history_runs=3
    )
