import logging

from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector

from config.settings import settings

_pdf_knowledge = None

def get_pdf_knowledge():
    """
    Inicializa a base de conhecimento (RAG) de forma lazy.
    """
    global _pdf_knowledge
    if _pdf_knowledge is not None:
        return _pdf_knowledge

    db_url = settings.SUPABASE_DB_URL
    if not db_url:
        logging.warning("SUPABASE_DB_URL não configurada. RAG para PDF desativado.")
        return None

    try:
        pdf_vector_db = PgVector(
            table_name=settings.PDF_TABLE,
            db_url=db_url
        )
        _pdf_knowledge = Knowledge(vector_db=pdf_vector_db)
        return _pdf_knowledge
    except Exception as e:
        logging.error(f"Erro ao inicializar base de conhecimento PDF (PgVector): {e}")
        return None

# Instância exportada para retrocompatibilidade (mas inicializada na primeira chamada)
# Para forçar lazy, agora os agentes devem usar get_pdf_knowledge()
