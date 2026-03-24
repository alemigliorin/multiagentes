import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from auth import verify_auth


async def unified_middleware(request: Request, call_next):
    """
    Middleware unificado para Logging de Origin e Verificação de Autenticação.
    """
    # 1. Logging de Origin (útil para depurar CORS em produção)
    origin = request.headers.get("origin")
    if origin:
        logging.info(f"📥 Requisição recebida de Origin: {origin}")

    # 2. Verificação de Autenticação (apenas para rotas protegidas)
    # Nota: verify_auth deve lidar com quais caminhos são públicos vs privados
    auth_result = await verify_auth(request)
    if isinstance(auth_result, tuple) and not auth_result[0]:
        return JSONResponse(
            status_code=401,
            content={"detail": auth_result[1]}
        )

    # 3. Continuar para o próximo middleware/handler
    response = await call_next(request)
    return response

def setup_middlewares(app):
    """
    Configura os middlewares na instância do FastAPI.
    """
    # Para DEBUG: Desativando temporariamente o middleware unificado
    # e deixando apenas o log de origin para ver se resolve o problema de digitação
    # app.middleware("http")(unified_middleware)

    @app.middleware("http")
    async def debug_middleware(request: Request, call_next):
        origin = request.headers.get("origin")
        if origin:
            logging.info(f"📥 [DEBUG] Origin: {origin} | Path: {request.url.path}")
        return await call_next(request)
