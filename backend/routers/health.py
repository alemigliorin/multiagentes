from fastapi import APIRouter, Request

from config.cors import parse_allowed_origins

router = APIRouter()

@router.api_route("/health", methods=["GET", "HEAD", "OPTIONS"])
async def health_check(request: Request):
    """
    Endpoint de saúde robusto para monitoramento e validação de CORS/Proxy.
    """
    return {
        "status": "ok",
        "message": "Backend is running resiliently",
        "method": request.method,
        "allowed_origins": parse_allowed_origins()
    }
