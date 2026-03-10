import json
from unittest.mock import patch, MagicMock
from services.api_client import get_response_stream
from config import AGENT_RUN_ENDPOINT

@patch("services.api_client.requests.post")
def test_parse_sse_valid_events(mock_post, mock_sse_response):
    # Setup mock response iterator
    mock_resp = MagicMock()
    mock_resp.iter_lines.return_value = mock_sse_response
    mock_post.return_value = mock_resp
    
    events = list(get_response_stream("teste"))
    
    assert len(events) == 6
    assert events[0]["event"] == "RunStarted"
    assert events[1]["event"] == "ToolCallStarted"
    assert events[3]["content"] == "Olá! "

@patch("services.api_client.requests.post")
def test_parse_sse_ignores_invalid(mock_post):
    invalid_lines = [
        b"data: {invalid json}",
        b"just some text",
        b"data: {\"event\": \"Valid\"}",
        b""
    ]
    mock_resp = MagicMock()
    mock_resp.iter_lines.return_value = invalid_lines
    mock_post.return_value = mock_resp
    
    events = list(get_response_stream("teste"))
    assert len(events) == 1
    assert events[0]["event"] == "Valid"

@patch("services.api_client.requests.post")
def test_connection_error_handling(mock_post):
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection Refused")
    
    events = list(get_response_stream("teste"))
    assert len(events) == 1
    assert events[0]["event"] == "RunError"
    assert "Connection Refused" in events[0]["error_message"]

@patch("services.api_client.requests.post")
def test_endpoint_configuration(mock_post):
    mock_resp = MagicMock()
    mock_resp.iter_lines.return_value = []
    mock_post.return_value = mock_resp
    
    list(get_response_stream("teste", session_id="123"))
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["url"] == AGENT_RUN_ENDPOINT
    assert kwargs["data"]["message"] == "teste"
    assert kwargs["data"]["session_id"] == "123"
