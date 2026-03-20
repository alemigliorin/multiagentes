import logging

from agno.os import AgentOS
from fastapi import Request
from fastapi.responses import JSONResponse

# Agentes
from agents.orchestrator import orquestrador

# Configuração e Utilitários
from config.cors import parse_allowed_origins
from middleware.auth_logging import setup_middlewares
from middleware.proxy_headers import DisableProxyBufferingMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Roteamento e Middleware
from routers.health import router as health_router
from routers.uploads import router as upload_router
from routers.config import router as config_router

# 🛡️ Configuração de Segurança e CORS
allowed_origins = parse_allowed_origins()
logging.info(f"🛡️ CORS: Origins permitidas configuradas: {allowed_origins}")

# 🚀 Inicialização do AgentOS com o Orquestrador
agent_os = AgentOS(agents=[orquestrador], cors_allowed_origins=allowed_origins)
app = agent_os.get_app()

# 🧩 Registro de Middlewares e Rotas
app.add_middleware(DisableProxyBufferingMiddleware)

# Configuração EXPLICITA de CORS para garantir que Preflight funcione (OPTIONS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_middlewares(app)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(config_router)

# No framework Agno, o app já está pronto para o Uvicorn através do agent_os.get_app()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
