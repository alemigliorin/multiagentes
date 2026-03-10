from unittest.mock import MagicMock, mock_open, patch

# O client do genai é iniciado no escopo global do módulo.
# Graças ao conftest.py, a chave fictícia "test-google-key" já foi setada.
import media_tools


def test_gerar_imagem_sucesso():
    with patch("media_tools.client.models.generate_images") as mock_generate:
        # Configura o mock da resposta da API do Google
        mock_result = MagicMock()
        mock_image = MagicMock()
        mock_image.image.image_bytes = b"fake-png-bytes"
        mock_result.generated_images = [mock_image]
        mock_generate.return_value = mock_result

        # Evita a criação real de pastas e arquivos no sistema
        with patch("media_tools.os.makedirs"), patch("builtins.open", mock_open()) as m_open:
            res = media_tools.gerar_imagem("dummy prompt")

            assert "Sucesso: Imagem gerada e salva" in res
            m_open.assert_called_once()
            m_open().write.assert_called_once_with(b"fake-png-bytes")


def test_gerar_imagem_erro_api():
    with patch("media_tools.client.models.generate_images", side_effect=Exception("API limit reached")):
        # Como o código tem um bloco except abrangente, ele deve retornar uma string de erro
        res = media_tools.gerar_imagem("dummy prompt")
        assert "Erro ao gerar imagem" in res
        assert "API limit reached" in res


def test_gerar_video_sucesso_lro():
    with patch("media_tools.client.models.generate_videos") as mock_generate:
        mock_result = MagicMock()
        mock_result.name = "veo-job-123"
        mock_generate.return_value = mock_result

        with (
            patch("media_tools._load_jobs", return_value={}),
            patch("media_tools._save_jobs") as mock_save,
            patch("media_tools.os.makedirs"),
        ):
            res = media_tools.gerar_video("dummy video prompt")

            assert "VÍDEO ENVIADO PARA A FILA COM SUCESSO" in res
            assert "veo-job-123" in res

            # Garante que salvou o job na lista local
            mock_save.assert_called_once()
            jobs_salvos = mock_save.call_args[0][0]
            assert "veo-job-123" in jobs_salvos
            assert jobs_salvos["veo-job-123"]["status"] == "pending"


def test_consultar_status_video_concluido_previamente():
    job_mock = {"veo-job-123": {"status": "completed", "output_path": "fake/path/video.mp4"}}
    with patch("media_tools._load_jobs", return_value=job_mock), patch("os.path.exists", return_value=True):
        res = media_tools.consultar_status_video("veo-job-123")
        assert "O vídeo já havia sido concluído" in res
        assert "fake/path/video.mp4" in res


def test_consultar_status_video_nao_encontrado():
    with patch("media_tools._load_jobs", return_value={}):
        res = media_tools.consultar_status_video("job_fantasma")
        assert "não foi encontrado nos registros" in res


@patch("requests.get")
def test_consultar_status_video_processando(mock_get):
    job_mock = {"veo-job-123": {"status": "pending"}}

    with patch("media_tools._load_jobs", return_value=job_mock):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"done": False}
        mock_get.return_value = mock_response

        res = media_tools.consultar_status_video("veo-job-123")
        assert "ainda está sendo PROCESSADO na fila" in res


def test_gerar_imagem_sem_resultado():
    with patch("media_tools.client.models.generate_images") as mock_generate:
        mock_result = MagicMock()
        mock_result.generated_images = []
        mock_generate.return_value = mock_result

        with patch("media_tools.os.makedirs"):
            res = media_tools.gerar_imagem("dummy prompt")
            assert "Falha ao gerar a imagem" in res


def test_gerar_video_sem_job_id():
    with patch("media_tools.client.models.generate_videos") as mock_generate:
        mock_result = MagicMock()
        mock_result.name = None
        mock_generate.return_value = mock_result

        with patch("media_tools.os.makedirs"):
            res = media_tools.gerar_video("dummy prompt")
            assert "não recebi um Job ID rastreável" in res


def test_gerar_video_falha_attribute_error():
    with patch("media_tools.client.models.generate_videos", side_effect=AttributeError):
        with patch("media_tools.os.makedirs"):
            res = media_tools.gerar_video("prompt")
            assert "não suporta esta ação" in res


def test_gerar_video_falha_geral():
    with patch("media_tools.client.models.generate_videos", side_effect=Exception("Timeout")):
        with patch("media_tools.os.makedirs"):
            res = media_tools.gerar_video("prompt")
            assert "Erro fatal ao despachar o vídeo com Veo. Erro: Timeout" in res


@patch("requests.get")
def test_consultar_status_video_http_error(mock_get):
    job_mock = {"veo-job-123": {"status": "pending"}}
    with patch("media_tools._load_jobs", return_value=job_mock):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        res = media_tools.consultar_status_video("veo-job-123")
        assert "Erro na API do Google ao consultar o Job: HTTP 500" in res


@patch("requests.get")
def test_consultar_status_video_done_with_error(mock_get):
    job_mock = {"veo-job-123": {"status": "pending"}}
    with patch("media_tools._load_jobs", return_value=job_mock), patch("media_tools._save_jobs") as mock_save:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"done": True, "error": "Quota exceeded"}
        mock_get.return_value = mock_response

        res = media_tools.consultar_status_video("veo-job-123")
        assert "A geração do vídeo falhou no servidor do Google" in res

        # O _save_jobs deve ter sido chamado marcando failed
        jobs_salvos = mock_save.call_args[0][0]
        assert jobs_salvos["veo-job-123"]["status"] == "failed"
        assert jobs_salvos["veo-job-123"]["error_details"] == "Quota exceeded"


@patch("requests.get")
def test_consultar_status_video_done_key_error(mock_get):
    job_mock = {"veo-job-123": {"status": "pending"}}
    with patch("media_tools._load_jobs", return_value=job_mock), patch("media_tools._save_jobs") as mock_save:
        mock_response = MagicMock()
        mock_response.status_code = 200
        # done é true mas o body não tem a estrutura json esperada para video URI
        mock_response.json.return_value = {"done": True, "response": {"wrongFormat": {}}}
        mock_get.return_value = mock_response

        res = media_tools.consultar_status_video("veo-job-123")
        assert "resposta inesperado" in res
        jobs_salvos = mock_save.call_args[0][0]
        assert jobs_salvos["veo-job-123"]["status"] == "failed"


@patch("requests.get")
def test_consultar_status_video_download_success(mock_get):
    job_mock = {"veo-job-123": {"status": "pending", "output_path": "test.mp4"}}
    with (
        patch("media_tools._load_jobs", return_value=job_mock),
        patch("media_tools._save_jobs") as mock_save,
        patch("builtins.open", mock_open()) as m_open,
    ):
        # 1a chamada é get status, 2a chamada é baixar o arquivo
        mock_status = MagicMock()
        mock_status.status_code = 200
        mock_status.json.return_value = {
            "done": True,
            "response": {"generateVideoResponse": {"generatedSamples": [{"video": {"uri": "http://fake-url"}}]}},
        }

        mock_download = MagicMock()
        mock_download.status_code = 200
        mock_download.iter_content.return_value = [b"chunk1", b"chunk2"]

        mock_get.side_effect = [mock_status, mock_download]

        res = media_tools.consultar_status_video("veo-job-123")
        assert "VÍDEO CONCLUÍDO E BAIXADO COM SUCESSO" in res
        m_open.assert_called_with("test.mp4", "wb")

        # Verifica salvamento de jobs
        jobs_salvos = mock_save.call_args[0][0]
        assert jobs_salvos["veo-job-123"]["status"] == "completed"


@patch("requests.get")
def test_consultar_status_video_download_fail(mock_get):
    job_mock = {"veo-job-123": {"status": "pending", "output_path": "test.mp4"}}
    with patch("media_tools._load_jobs", return_value=job_mock):
        mock_status = MagicMock()
        mock_status.status_code = 200
        mock_status.json.return_value = {
            "done": True,
            "response": {"generateVideoResponse": {"generatedSamples": [{"video": {"uri": "http://fake-url"}}]}},
        }

        mock_download = MagicMock()
        mock_download.status_code = 404

        mock_get.side_effect = [mock_status, mock_download]

        res = media_tools.consultar_status_video("veo-job-123")
        assert "falhou ao baixar: HTTP 404" in res


def test_load_save_jobs_funcs():
    # Testa os fallback functions usando json.dump json.load
    with patch("os.path.exists", return_value=False):
        assert media_tools._load_jobs() == {}

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", side_effect=Exception):
            assert media_tools._load_jobs() == {}

    with patch("os.makedirs"), patch("builtins.open", mock_open()), patch("json.dump") as m_dump:
        media_tools._save_jobs({"a": 1})
        m_dump.assert_called()
