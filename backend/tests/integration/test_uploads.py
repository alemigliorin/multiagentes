"""
Testes de integração para routers/uploads.py.
Usa um app FastAPI mínimo para evitar a inicialização do AgentOS.
"""
import io
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.uploads import router

# App mínimo — só o router de uploads, sem AgentOS
_app = FastAPI()
_app.include_router(router)
client = TestClient(_app)


# ── PDF ──────────────────────────────────────────────────────────────────────

def test_upload_pdf_valid(tmp_path, monkeypatch):
    """PDF com nome correto deve ser aceito e retornar texto extraído."""
    monkeypatch.setattr("routers.uploads.settings.UPLOAD_TMP_DIR", str(tmp_path))

    mock_doc = MagicMock()
    mock_doc.content = "Texto extraído do PDF de teste."

    with patch("routers.uploads.PDFReader") as mock_reader:
        mock_reader.return_value.read.return_value = [mock_doc]
        response = client.post(
            "/upload-pdf",
            files={"file": ("documento.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
            data={"save_to_rag": "false"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["mode"] == "temporary"
    assert "Texto extraído" in body["extracted_text"]


def test_upload_pdf_invalid_extension():
    """Arquivo com extensão não-PDF deve retornar 400."""
    response = client.post(
        "/upload-pdf",
        files={"file": ("documento.txt", io.BytesIO(b"conteudo texto"), "text/plain")},
        data={"save_to_rag": "false"},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["error"]


def test_upload_pdf_to_rag(tmp_path, monkeypatch):
    """Com save_to_rag=true deve chamar knowledge.add_content e retornar mode=rag."""
    monkeypatch.setattr("routers.uploads.settings.UPLOAD_TMP_DIR", str(tmp_path))

    mock_knowledge = MagicMock()
    with patch("routers.uploads.get_pdf_knowledge", return_value=mock_knowledge):
        with patch("routers.uploads.PDFReader"):
            response = client.post(
                "/upload-pdf",
                files={"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
                data={"save_to_rag": "true"},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["mode"] == "rag"
    mock_knowledge.add_content.assert_called_once()


def test_upload_pdf_rag_not_initialized(tmp_path, monkeypatch):
    """Se knowledge não estiver disponível, deve retornar 500."""
    monkeypatch.setattr("routers.uploads.settings.UPLOAD_TMP_DIR", str(tmp_path))

    with patch("routers.uploads.get_pdf_knowledge", return_value=None):
        response = client.post(
            "/upload-pdf",
            files={"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
            data={"save_to_rag": "true"},
        )

    assert response.status_code == 500


def test_upload_pdf_uses_uuid_filename(tmp_path, monkeypatch):
    """O arquivo salvo deve ter nome UUID, não o nome original."""
    monkeypatch.setattr("routers.uploads.settings.UPLOAD_TMP_DIR", str(tmp_path))

    mock_doc = MagicMock()
    mock_doc.content = "texto"

    with patch("routers.uploads.PDFReader") as mock_reader:
        mock_reader.return_value.read.return_value = [mock_doc]
        client.post(
            "/upload-pdf",
            files={"file": ("../../etc/passwd.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
            data={"save_to_rag": "false"},
        )

    # Nenhum arquivo com o nome original deve ter sido criado
    saved_files = list(tmp_path.iterdir())
    for f in saved_files:
        assert "passwd" not in f.name
        assert ".." not in f.name


# ── VÍDEO ─────────────────────────────────────────────────────────────────────

def test_upload_video_valid(tmp_path, monkeypatch):
    """Vídeo com creator válido deve ser salvo com sucesso."""
    monkeypatch.setattr("routers.uploads.settings.VIDEO_BASE_DIR", str(tmp_path))

    response = client.post(
        "/upload-video",
        files={"file": ("video.mp4", io.BytesIO(b"fake video content"), "video/mp4")},
        data={"creator_name": "João Silva"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    # Nome sanitizado: espaço vira _, acentos removidos, tudo lowercase
    assert "jo" in body["path"].lower()


def test_upload_video_empty_creator():
    """Creator name em branco deve retornar 400."""
    response = client.post(
        "/upload-video",
        files={"file": ("video.mp4", io.BytesIO(b"fake"), "video/mp4")},
        data={"creator_name": "   "},
    )
    assert response.status_code == 400


def test_upload_video_creator_sanitization(tmp_path, monkeypatch):
    """Caracteres especiais no creator_name devem ser removidos na sanitização."""
    monkeypatch.setattr("routers.uploads.settings.VIDEO_BASE_DIR", str(tmp_path))

    response = client.post(
        "/upload-video",
        files={"file": ("video.mp4", io.BytesIO(b"fake"), "video/mp4")},
        data={"creator_name": "../../../etc/passwd"},
    )

    assert response.status_code == 200
    # O path retornado não deve conter traversal
    assert ".." not in response.json()["path"]
