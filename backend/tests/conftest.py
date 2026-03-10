import pytest


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Garante que nenhuma Key real seja usada durante os testes e define placeholders."""
    # Só sobrescreve se não estiver rodando no modo de gravação do VCR (pois gravar precisa da key real)
    import os
    if not os.environ.get("VCR_RECORD"):
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
        monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
        monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
        monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")


@pytest.fixture(scope="module")
def vcr_config():
    """Configuração global do VCR.py para ocultar dados sensíveis das gravações."""
    return {
        "filter_headers": [
            ("authorization", "DUMMY_AUTHORIZATION"),
            ("api-key", "DUMMY_API_KEY"),
            ("x-api-key", "DUMMY_API_KEY"),
        ],
        "filter_query_parameters": ["api_key", "key"],
        "decode_compressed_response": True,
    }


@pytest.fixture
def tmp_dir(tmp_path):
    """Cria um diretório temporário para testes que precisem escrever arquivos reais."""
    return tmp_path


@pytest.fixture
def sample_transcriptions():
    """Retorna um dicionário de exemplo imitando a estrutura do JSON verdadeiro."""
    return {
        "jeffnippard": [
            {
                "arquivo": "video1.mp4",
                "caminho_completo": "videos/jeffnippard/video1.mp4",
                "transcricao": "This is a dummy transcript about hypertrophy.",
            },
            {
                "arquivo": "video2.mp4",
                "caminho_completo": "videos/jeffnippard/video2.mp4",
                "transcricao": "Another dummy transcript of a video.",
            },
        ],
        "kallaway": [
            {"arquivo": "vidA.mp4", "caminho_completo": "videos/kallaway/vidA.mp4", "transcricao": "AI news for today."}
        ],
    }
