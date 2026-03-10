from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat

from agent import get_model


def test_get_model_openai():
    model = get_model("openai")
    assert isinstance(model, OpenAIChat)
    assert model.id == "gpt-4o"


def test_get_model_openai_custom_id():
    model = get_model("openai", id="gpt-4o-mini")
    assert isinstance(model, OpenAIChat)
    assert model.id == "gpt-4o-mini"


def test_get_model_anthropic():
    model = get_model("anthropic")
    assert isinstance(model, Claude)
    assert model.id == "claude-3-5-sonnet-20241022"


def test_get_model_google():
    model = get_model("google")
    assert isinstance(model, Gemini)
    assert model.id == "gemini-2.5-flash"


def test_get_model_groq():
    model = get_model("groq")
    assert isinstance(model, Groq)
    assert model.id == "llama-3.3-70b-versatile"


def test_get_model_deepseek():
    model = get_model("deepseek")
    assert isinstance(model, DeepSeek)
    assert model.id == "deepseek-chat"


def test_get_model_default_fallback():
    # Deve fazer fallback pro OpenAI caso o nome não seja nenhum mapeado
    model = get_model("provider_inexistente")
    assert isinstance(model, OpenAIChat)
    assert model.id == "gpt-4o"


def test_get_model_case_insensitive():
    # Passando no uppercase mas deveria processar normal
    model_google = get_model("GooglE")
    assert isinstance(model_google, Gemini)
