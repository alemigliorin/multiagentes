from unittest.mock import MagicMock, patch

import pytest

from agent import (
    acionar_agente_pdf,
    acionar_copywriter,
    acionar_criador_experts,
    acionar_criador_midia,
    acionar_juridico,
    acionar_pesquisador,
)


@pytest.fixture
def mock_agent_response():
    mock_resp = MagicMock()
    mock_resp.content = "Resposta Mockada"
    return mock_resp


@patch("agent.pesquisador.run")
def test_acionar_pesquisador(mock_run, mock_agent_response):
    mock_run.return_value = mock_agent_response
    assert acionar_pesquisador("teste") == "Resposta Mockada"
    mock_run.assert_called_once_with("teste")


@patch("agent.copywriter.run")
def test_acionar_copywriter(mock_run, mock_agent_response):
    mock_run.return_value = mock_agent_response
    assert acionar_copywriter("instrucao") == "Resposta Mockada"
    mock_run.assert_called_once_with("instrucao")


@patch("agent.juridico.run")
def test_acionar_juridico(mock_run, mock_agent_response):
    mock_run.return_value = mock_agent_response
    assert acionar_juridico("conteudo") == "Resposta Mockada"
    mock_run.assert_called_once_with("conteudo")


@patch("agent.criador_experts.run")
def test_acionar_criador_experts(mock_run, mock_agent_response):
    mock_run.return_value = mock_agent_response
    assert acionar_criador_experts("tarefa") == "Resposta Mockada"
    mock_run.assert_called_once_with("tarefa")


@patch("agent.criador_midia.run")
def test_acionar_criador_midia(mock_run, mock_agent_response):
    mock_run.return_value = mock_agent_response
    assert acionar_criador_midia("imagem") == "Resposta Mockada"
    mock_run.assert_called_once_with("imagem")


@patch("agent.agente_pdf.run")
def test_acionar_agente_pdf(mock_run, mock_agent_response):
    mock_run.return_value = mock_agent_response
    assert acionar_agente_pdf("pergunta sobre pdf") == "Resposta Mockada"
    mock_run.assert_called_once_with("pergunta sobre pdf")
