"""
Testes unitários para agents/factory.py.
Verifica que get_model() retorna a instância correta para cada provider.
"""
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat

from agents.factory import get_model


def test_get_model_openai():
    model = get_model("openai")
    assert isinstance(model, OpenAIChat)


def test_get_model_openai_custom_id():
    model = get_model("openai", id="gpt-4o-mini")
    assert isinstance(model, OpenAIChat)
    assert model.id == "gpt-4o-mini"


def test_get_model_anthropic():
    model = get_model("anthropic")
    assert isinstance(model, Claude)


def test_get_model_google():
    model = get_model("google")
    assert isinstance(model, Gemini)


def test_get_model_groq():
    model = get_model("groq")
    assert isinstance(model, Groq)


def test_get_model_deepseek():
    model = get_model("deepseek")
    assert isinstance(model, DeepSeek)


def test_get_model_unknown_fallback():
    """Provider desconhecido deve fazer fallback para OpenAI."""
    model = get_model("provider_inexistente")
    assert isinstance(model, OpenAIChat)


def test_get_model_case_insensitive():
    """Provider deve ser case insensitive."""
    model = get_model("GooglE")
    assert isinstance(model, Gemini)


def test_get_model_custom_id_preserved():
    """ID customizado deve ser preservado independente do provider."""
    model = get_model("google", id="gemini-2.5-pro")
    assert isinstance(model, Gemini)
    assert model.id == "gemini-2.5-pro"
