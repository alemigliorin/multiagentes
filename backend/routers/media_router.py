import logging
from fastapi import APIRouter
from storage import list_media as storage_list_media

router = APIRouter(tags=["media"])

@router.get("/media/list")
async def list_media():
    """Lista todos os arquivos de mídia disponíveis (imagens e vídeos) no Supabase Storage."""
    files = storage_list_media()
    return {"files": files}

