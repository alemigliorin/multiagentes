import logging
import mimetypes
import re
import shutil
import uuid
from pathlib import Path

from agno.knowledge.reader.pdf_reader import PDFReader
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from config.settings import settings
from knowledge.pdf_knowledge import get_pdf_knowledge

router = APIRouter()

def is_safe_file(filename: str, allowed_extensions: set) -> bool:
    """Valida extensão básica."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), save_to_rag: str = Form("false")):
    """
    Faz o upload de um PDF, salvando-o no RAG ou extraindo texto temporariamente.
    Implementa segurança básica com UUID e validação de tipo.
    """
    try:
        # Validação básica de tipo
        content_type, _ = mimetypes.guess_type(file.filename)
        if content_type != "application/pdf":
             return JSONResponse(status_code=400, content={"error": "Apenas arquivos PDF são permitidos."})

        upload_dir = Path(settings.UPLOAD_TMP_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Gerar nome único para evitar colisões e ataques de path traversal
        file_extension = Path(file.filename).suffix
        safe_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / safe_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if save_to_rag.lower() == "true":
            knowledge = get_pdf_knowledge()
            if not knowledge:
                return JSONResponse(status_code=500, content={"error": "Base de conhecimento não inicializada."})

            knowledge.add_content(path=str(file_path), reader=PDFReader())
            file_path.unlink() # Limpa temporário
            return {"status": "success", "mode": "rag", "message": "Documento indexado com sucesso."}
        else:
            reader = PDFReader()
            documents = reader.read(pdf=str(file_path))
            extracted_text = "\n\n".join([doc.content for doc in documents if doc.content])
            file_path.unlink() # Limpa temporário
            return {
                "status": "success",
                "mode": "temporary",
                "extracted_text": extracted_text,
                "original_name": file.filename
            }

    except Exception as e:
        logging.exception("Erro no upload de PDF")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/upload-video")
async def upload_video(file: UploadFile = File(...), creator_name: str = Form(...)):
    """
    Upload de vídeos para um diretório específico do criador.
    """
    try:
        if not creator_name.strip():
            return JSONResponse(status_code=400, content={"error": "Nome do criador é obrigatório"})

        # Sanitização do nome do criador
        safe_creator_name = re.sub(r"[^a-zA-Z0-9_\-]", "", creator_name.replace(" ", "_").lower())

        video_dir = Path(settings.VIDEO_BASE_DIR) / safe_creator_name
        video_dir.mkdir(parents=True, exist_ok=True)

        # Gerar nome seguro para o vídeo
        file_extension = Path(file.filename).suffix
        safe_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = video_dir / safe_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "status": "success",
            "message": "Vídeo salvo com sucesso",
            "path": str(file_path),
            "original_name": file.filename
        }

    except Exception as e:
        logging.exception("Erro no upload de vídeo")
        return JSONResponse(status_code=500, content={"error": str(e)})
