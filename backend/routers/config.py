import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from agents.orchestrator import orquestrador
from agents.factory import get_model

router = APIRouter()

# Mapa explícito de model_id → provider
MODEL_PROVIDER_MAP: dict[str, str] = {
    'gpt-5-mini':               'openai',
    'gpt-5-nano':               'openai',
    'gpt-4o':                   'openai',
    'gpt-4o-mini':              'openai',
    'claude-sonnet-4-6':        'anthropic',
    'claude-haiku-4-5-20251001': 'anthropic',
    'gemini-2.5-flash':         'google',
    'llama-3.3-70b-versatile':  'groq',
    'deepseek-chat':            'deepseek',
}


@router.post("/api/config/model")
async def set_orchestrator_model(model_id: str):
    """
    Atualiza o modelo LLM do agente orquestrador em tempo de execução.
    Chamado pelo frontend quando o usuário seleciona um modelo no ModelSelector.
    """
    provider = MODEL_PROVIDER_MAP.get(model_id)
    if not provider:
        return JSONResponse(
            status_code=400,
            content={"error": f"Modelo desconhecido: {model_id}. Modelos válidos: {list(MODEL_PROVIDER_MAP.keys())}"}
        )

    try:
        orquestrador.model = get_model(provider, id=model_id)
        logging.info(f"Modelo do orquestrador atualizado: {provider}/{model_id}")
        return {"status": "ok", "model": model_id, "provider": provider}
    except Exception as e:
        logging.exception("Erro ao atualizar modelo do orquestrador")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/api/config/model")
async def get_orchestrator_model():
    """
    Retorna o modelo LLM atualmente configurado no orquestrador.
    Usado pelo frontend para sincronizar o estado inicial do ModelSelector.
    """
    try:
        model_id = orquestrador.model.id if orquestrador.model else None
        provider = MODEL_PROVIDER_MAP.get(model_id, "unknown") if model_id else "unknown"
        return {"model": model_id, "provider": provider}
    except Exception:
        return {"model": None, "provider": "unknown"}
