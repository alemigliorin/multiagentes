import json
from unittest.mock import mock_open, patch

import pytest

from reels_tools import get_creator_transcripts, list_available_creators


@pytest.fixture
def mock_json_path(sample_transcriptions):
    """Mocks Path.exists and open() to return static sample data."""
    json_data = json.dumps(sample_transcriptions)

    with patch("reels_tools.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=json_data)):
            yield


def test_get_creator_transcripts_sucesso(mock_json_path):
    result = get_creator_transcripts("jeffnippard")
    assert "Transcript 1" in result
    assert "This is a dummy transcript about hypertrophy." in result
    assert "Transcript 2" in result


def test_get_creator_transcripts_case_insensitive(mock_json_path):
    result = get_creator_transcripts("JeffNiPPard")
    assert "Transcript 1" in result


def test_get_creator_transcripts_nao_encontrado(mock_json_path):
    result = get_creator_transcripts("invalid_creator")
    assert "Available creators are: jeffnippard, kallaway" in result


def test_get_creator_transcripts_arquivo_inexistente():
    with patch("reels_tools.Path.exists", return_value=False):
        result = get_creator_transcripts("jeffnippard")
        assert "does not exist" in result


def test_get_creator_transcripts_json_malformado():
    with patch("reels_tools.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="{invalid_json}")):
            result = get_creator_transcripts("jeffnippard")
            assert "malformed" in result


def test_list_available_creators(mock_json_path):
    result = list_available_creators()
    assert "Available creators: jeffnippard, kallaway" in result


def test_list_available_creators_vazio():
    with patch("reels_tools.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="{}")):
            result = list_available_creators()
            assert "No creators found" in result


def test_list_available_creators_not_found():
    with patch("reels_tools.Path.exists", return_value=False):
        result = list_available_creators()
        assert "does not exist" in result


def test_list_available_creators_json_error():
    with patch("reels_tools.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="[erro")):
            result = list_available_creators()
            assert "malformed" in result


def test_list_available_creators_geral_error():
    with patch("reels_tools.Path.exists", return_value=True):
        with patch("builtins.open", side_effect=Exception("Read lock")):
            result = list_available_creators()
            assert "Error reading database: Read lock" in result


def test_get_creator_transcripts_geral_error():
    with patch("reels_tools.Path.exists", return_value=True):
        with patch("builtins.open", side_effect=Exception("Timeout read")):
            result = get_creator_transcripts("jeffnippard")
            assert "Error reading transcripts: Timeout read" in result


def test_get_creator_transcripts_lista_vazia():
    # Cria json onde o criador existe mas a lista tá vazia
    with patch("reels_tools.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data='{"robert": []}')):
            result = get_creator_transcripts("robert")
            assert "No transcripts found for creator 'robert'" in result
