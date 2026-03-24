import logging
import os

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat

from config.settings import settings

# Registry de fábricas de modelos para evitar elifs
MODEL_REGISTRY = {
    "openai": lambda model_id, api_key: OpenAIChat(id=model_id, api_key=api_key),
    "anthropic": lambda model_id, api_key: Claude(id=model_id, api_key=api_key),
    "google": lambda model_id, api_key: Gemini(id=model_id, api_key=api_key),
    "groq": lambda model_id, api_key: Groq(id=model_id, api_key=api_key),
    "deepseek": lambda model_id, api_key: DeepSeek(id=model_id, api_key=api_key),
}

def get_model(provider: str = "openai", **kwargs):
    """
    Instancia o provedor de LLM adequado usando o registry.
    """
    provider = provider.lower()
    model_id = kwargs.get("id", settings.DEFAULT_MODEL_ID)

    # Busca a fábrica no registry
    factory = MODEL_REGISTRY.get(provider)

    if factory:
        # Pega a chave correta do settings
        api_key = getattr(settings, f"{provider.upper()}_API_KEY", None)
        return factory(model_id, api_key)

    # Fallback para OpenAI com aviso
    logging.warning(f"Provedor LLM desconhecido: {provider}. Usando fallback para OpenAI.")
    return OpenAIChat(id=settings.DEFAULT_MODEL_ID, api_key=settings.OPENAI_API_KEY)

def create_agent(name, description, tools=None, instructions_file=None, db_url=None, **kwargs):
    """
    Função unificada para criar agentes, garantindo consistência em instruções e DB.
    """
    model = kwargs.get("model") or get_model("openai", id=settings.DEFAULT_MODEL_ID)

    db = None
    if db_url:
        try:
            db = PostgresDb(session_table=settings.SESSION_TABLE, db_url=db_url)
        except Exception as e:
            logging.warning(f"Não foi possível inicializar DB para o agente {name}: {e}")

    instructions = ""
    if instructions_file:
        try:
            if os.path.exists(instructions_file):
                with open(instructions_file, encoding="utf-8") as f:
                    instructions = f.read()
            else:
                logging.error(f"Arquivo de instruções não encontrado: {instructions_file}")
                instructions = "Instruções não encontradas."
        except Exception as e:
            logging.error(f"Erro ao ler arquivo de instruções {instructions_file}: {e}")

    # Gera um id estável a partir do nome (Agno usa agent.id para lookup nas rotas /v1/agents/{id}/runs)
    agent_id = name.lower().replace(" ", "_")

    # Remove argumentos que não pertencem ao construtor do Agent
    agent_kwargs = {
        "id": agent_id,
        "model": model,
        "name": name,
        "description": description,
        "tools": tools,
        "instructions": instructions,
        "db": db,
        "add_history_to_context": kwargs.get("add_history_to_context", True),
        "num_history_runs": kwargs.get("num_history_runs", 5),
    }

    # Adiciona outros kwargs que o framework Agno possa suportar
    for k, v in kwargs.items():
        if k not in ["model", "add_history_to_context", "num_history_runs", "instructions_file"]:
            agent_kwargs[k] = v

    return Agent(**agent_kwargs)
