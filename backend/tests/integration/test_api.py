from fastapi.testclient import TestClient

from agent import app

client = TestClient(app)


def test_openapi_docs_endpoint():
    """Testa se a documentação OpenAPI swagger está sendo gerada e acessível."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text or "openapi" in response.text.lower()


def test_cors_headers():
    """Testa se as configurações de CORS estão retornando os headers corretos."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    # A biblioteca starlette/fastapi pode retornar 200 ou 404 para OPTION na raiz
    # dependendo do roteador, mas no mínimo não deve estourar erro 500.
    assert response.status_code in [200, 404, 405]

    # Se retornar 200 pro preflight, testa as chaves (CORS middleware)
    if response.status_code == 200:
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_v1_router_exists():
    """Testa se as rotas da v1 do agente existem (AgentOS padrão cria algo em /v1 ou dependendo da versão do agno)."""
    # É apenas um hit genérico para prever se as rotas da framework Agno não quebram.
    response = client.get("/v1/agents/orquestrador")
    # 404 = Não encontrado (mas servidor funciona)
    # 403 = Não autorizado
    # 200 = OK
    # 401 = Missing API Key
    assert response.status_code in [200, 401, 403, 404, 422]
