"""
Testes de integração para os endpoints principais da API.
Usa mock do orquestrador para evitar inicialização real do AgentOS.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """
    Cria o TestClient com AgentOS mockado para evitar
    conexões reais com OpenAI e Supabase no boot.
    """
    mock_agent = MagicMock()
    mock_agent.name = "orquestrador"

    with patch("agents.orchestrator.orquestrador", mock_agent):
        from main import app
        yield TestClient(app)


def test_health_check(client):
    """GET /health deve retornar 200 e status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_head(client):
    """HEAD /health deve funcionar para probes de infraestrutura."""
    response = client.head("/health")
    assert response.status_code == 200


def test_options_handler(client):
    """OPTIONS em qualquer rota deve retornar 200 (CORS preflight)."""
    response = client.options(
        "/v1/agents/orquestrador/run",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200


def test_cors_allows_localhost(client):
    """Origin localhost:3000 deve estar nas origins permitidas."""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    # O header CORS pode ser '*' ou a origin específica
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert allow_origin in ("*", "http://localhost:3000")
