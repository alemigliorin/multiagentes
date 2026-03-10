from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Como o `conftest.py` aplica os mocks de env var no `autouse=True`,
# a instância global `client = Groq()` no `transcripter.py`
# será iniciada com o test-groq-key e não irá quebrar.
from transcripter import extract_audio, get_ffmpeg_path, process_directory, transcribe_audio


def test_get_ffmpeg_path_found_in_path():
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
        assert get_ffmpeg_path() == "/usr/bin/ffmpeg"


def test_get_ffmpeg_path_not_found():
    with patch("shutil.which", return_value=None):
        with pytest.raises(FileNotFoundError, match="ffmpeg não encontrado no PATH"):
            get_ffmpeg_path()


def test_extract_audio():
    with patch("subprocess.run") as mock_run, patch("transcripter.get_ffmpeg_path", return_value="fake-ffmpeg"):
        extract_audio(Path("input.mp4"), Path("output.mp3"))

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]  # O primeiro argumento posicional

        assert args[0] == "fake-ffmpeg"
        assert args[1] == "-i"
        assert "input.mp4" in args[2]


def test_transcribe_audio():
    with (
        patch("transcripter.client.audio.transcriptions.create") as mock_create,
        patch("builtins.open", mock_open(read_data=b"dummy audio data")),
    ):
        mock_response = MagicMock()
        mock_response.text = "Texto transcrito com sucesso."
        mock_create.return_value = mock_response

        resultado = transcribe_audio(Path("teste.mp3"))

        assert resultado == "Texto transcrito com sucesso."
        mock_create.assert_called_once()


def test_process_directory_no_dir():
    with patch("pathlib.Path.exists", return_value=False) as mock_exists:
        # Testa o early return se a pasta não existe. Não vai estourar erro.
        process_directory("fake_dir")
        mock_exists.assert_called_once()


def test_process_directory_completo(tmp_dir):
    # Setup mock file structure in a real tmp dir
    base = tmp_dir / "videos"
    base.mkdir()

    # Criador 1 com 1 video válido e 1 inválido (.txt)
    c1 = base / "creator_a"
    c1.mkdir()
    (c1 / "vid1.mp4").write_text("dummy")
    (c1 / "ignored.txt").write_text("text")

    # Arquivo solto sem subpasta (entra no creator: desconhecido)
    (base / "loose.mkv").write_text("dummy")

    with (
        patch("transcripter.extract_audio") as mock_extract,
        patch("transcripter.transcribe_audio", return_value="Transcrito OK") as mock_trans,
        patch("pathlib.Path.unlink"),
    ):  # Previne tentar apagar algo que o mock extrail_audio sequer criou
        # Altera transcrever no tempdir sem sobrescrever onde tem videos reais
        process_directory(str(base), str(tmp_dir / "out.json"))

        # Duas tentativas válidas: vid1.mp4 e loose.mkv
        assert mock_extract.call_count == 2
        assert mock_trans.call_count == 2

        # Verifica se o JSON foi escrito corretamente
        import json

        with open(tmp_dir / "out.json", encoding="utf-8") as f:
            data = json.load(f)

            assert "creator_a" in data
            assert len(data["creator_a"]) == 1
            assert data["creator_a"][0]["arquivo"] == "vid1.mp4"
            assert data["creator_a"][0]["transcricao"] == "Transcrito OK"

            assert "desconhecido" in data
            assert len(data["desconhecido"]) == 1
            assert data["desconhecido"][0]["arquivo"] == "loose.mkv"


def test_process_directory_error_continue(tmp_dir):
    # Garante que um arquivo com erro não derruba o fluxo do outro
    base = tmp_dir / "videos2"
    base.mkdir()
    c1 = base / "c1"
    c1.mkdir()
    (c1 / "vid_bad.mp4").write_text("dummy")
    (c1 / "vid_good.mp4").write_text("dummy")

    def extrair_bug_condicional(v_path, a_path):
        if "vid_bad" in str(v_path):
            raise Exception("Erro forçado")
        # good passa

    with (
        patch("transcripter.extract_audio", side_effect=extrair_bug_condicional),
        patch("transcripter.transcribe_audio", return_value="OK"),
        patch("pathlib.Path.unlink"),
    ):
        process_directory(str(base), str(tmp_dir / "out2.json"))

        # O process_directory logou o erro mas continuou escrevendo pro json o arquivo OK
        import json

        with open(tmp_dir / "out2.json", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data["c1"]) == 1
            assert data["c1"][0]["arquivo"] == "vid_good.mp4"
