from fastapi import Request
from supabase import Client, create_client

from config.settings import settings

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY

_supabase_client = None


def get_supabase() -> Client:
    global _supabase_client
    if not _supabase_client:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


async def verify_auth(request: Request):
    """
    Função auxiliar de autenticação para ser usada dentro do middleware global.
    Isso evita problemas de compatibilidade do BaseHTTPMiddleware com Streaming.
    """
    # Allow CORS preflight requests
    if request.method == "OPTIONS":
        return True

    # Only protect API routes (like AgentOS /v1/ routes)
    if not request.url.path.startswith("/v1/"):
        return True

    # Check for authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False, "Missing or invalid authorization header"

    token = auth_header.split(" ")[1]

    try:
        supabase = get_supabase()
        # Verify user token with Supabase
        user_response = supabase.auth.get_user(token)

        # User auth failed or token expired
        if not user_response or not user_response.user:
            return False, "Invalid or expired token"

        return True, None

    except Exception as e:
        return False, f"Authentication failed: {str(e)}"

