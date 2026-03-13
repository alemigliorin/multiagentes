import os

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_supabase_client = None


def get_supabase() -> Client:
    global _supabase_client
    if not _supabase_client:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


async def auth_middleware(request: Request, call_next):
    # Allow CORS preflight requests
    if request.method == "OPTIONS":
        return await call_next(request)

    # Only protect API routes (like AgentOS /v1/ routes)
    if not request.url.path.startswith("/v1/"):
        return await call_next(request)

    # Check for authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid authorization header"})

    token = auth_header.split(" ")[1]

    try:
        supabase = get_supabase()
        # Verify user token with Supabase
        user_response = supabase.auth.get_user(token)

        # User auth failed or token expired
        if not user_response or not user_response.user:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

    except Exception as e:
        return JSONResponse(status_code=401, content={"detail": f"Authentication failed: {str(e)}"})

    response = await call_next(request)
    return response
