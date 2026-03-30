import os
import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(tags=["media"])

MEDIA_DIR = Path("tmp")
VIDEO_DIR = Path("videos")

# Garantir que os diretórios existam ao inicializar
MEDIA_DIR.mkdir(exist_ok=True)
VIDEO_DIR.mkdir(exist_ok=True)


@router.get("/media/list")
async def list_media():
    """Lista todos os arquivos de mídia disponíveis (imagens e vídeos)."""
    files = []
    # Imagens
    for f in MEDIA_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif'):
            files.append({
                "filename": f.name,
                "type": "image",
                "size": f.stat().st_size,
                "created": f.stat().st_mtime,
                "url": f"/media/download/{f.name}"
            })
    # Vídeos
    for f in VIDEO_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in ('.mp4', '.webm', '.mov'):
            files.append({
                "filename": f.name,
                "type": "video",
                "size": f.stat().st_size,
                "created": f.stat().st_mtime,
                "url": f"/videos/download/{f.name}"
            })
    # Ordenar por data de criação (mais recente primeiro)
    files.sort(key=lambda x: x["created"], reverse=True)
    return {"files": files}
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
