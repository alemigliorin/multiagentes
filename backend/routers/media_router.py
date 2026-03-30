import os
import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(tags=["media"])

MEDIA_DIR = Path("tmp")
VIDEO_DIR = Path("videos")

@router.get("/media/download/{filename}")
async def download_media(filename: str):
    """Retorna um arquivo de mídia (imagem) gerado pelo agente."""
    filepath = MEDIA_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        return JSONResponse(status_code=404, content={"detail": f"Arquivo '{filename}' não encontrado."})
    return FileResponse(str(filepath), media_type="image/png", filename=filename)


@router.get("/videos/download/{filename}")
async def download_video(filename: str):
    """Retorna um arquivo de vídeo gerado pelo agente."""
    filepath = VIDEO_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        return JSONResponse(status_code=404, content={"detail": f"Vídeo '{filename}' não encontrado."})
    return FileResponse(str(filepath), media_type="video/mp4", filename=filename)
