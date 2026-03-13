import pytest
from agno.agent import Agent

# Import the actual get_model to ensure we test the real integration
from agent import get_model


@pytest.mark.vcr(match_on=["method", "scheme", "host", "port", "path", "query"])
def test_agent_basic_response(vcr_config):
    """
    Testa a comunicação real com a API da OpenAI.
    Se a fita (cassette) não existir, o VCR fará a chamada real e gravará a resposta,
    escondendo a key (devido ao vcr_config no conftest).
    Se a fita existir, ele usará o mock perfeito.
    """
    model = get_model("openai", id="gpt-4o-mini")

    agent = Agent(model=model, name="test_vcr_agent", description="Você é um assistente prestativo.")

    response = agent.run("Qual é a capital do Brasil? Responda em uma palavra.")

    # O VCR deve gravar que a resposta foi Brasília (ou algo muito próximo)
    assert response is not None
    assert "Brasília" in response.content or "brasilia" in response.content.lower()
