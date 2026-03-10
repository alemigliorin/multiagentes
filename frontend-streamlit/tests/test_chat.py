import pytest
import json
from unittest.mock import patch, MagicMock

class MockSessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

@patch("components.chat.st")
@patch("components.chat.get_response_stream")
def test_assistant_response_saved(mock_stream, mock_st, mock_sse_response):
    from components.chat import render_chat
    
    # Setup mock session state
    mock_st.session_state = MockSessionState({"messages": [], "session_id": "123"})
    mock_st.chat_input.return_value = "Olá"
    
    # Simulamos que os eventos do sse_response são recebidos da função mock_stream
    events = []
    for line in mock_sse_response:
        if line and line.startswith(b'data: '):
            events.append(json.loads(line[6:].decode('utf-8')))
    
    mock_stream.return_value = events
    
    render_chat()
    
    # A primeira inserção é do usuário, a segunda é do assistente
    assert len(mock_st.session_state["messages"]) == 2
    assert mock_st.session_state["messages"][0]["role"] == "user"
    assert mock_st.session_state["messages"][1]["role"] == "assistant"
    # O conteúdo concatena 'Olá! ' + 'Esta é uma resposta de teste.'
    assert "Olá! Esta é uma resposta de teste." in mock_st.session_state["messages"][1]["content"]

@patch("components.chat.st")
@patch("components.chat.get_response_stream")
def test_streaming_content_accumulates(mock_stream, mock_st):
    from components.chat import render_chat
    mock_st.session_state = MockSessionState({"messages": []})
    mock_st.chat_input.return_value = "Teste"
    
    # Retorna dois pedaços de conteúdo
    mock_stream.return_value = [
        {"event": "RunContent", "content": "Parte 1. "},
        {"event": "RunContent", "content": "Parte 2."}
    ]
    
    mock_placeholder = MagicMock()
    mock_st.empty.return_value = mock_placeholder
    
    render_chat()
    
    # Verifica que tentou anexar no espaço placeholder (que seria a tela no st)
    mock_placeholder.markdown.assert_any_call("Parte 1. ▌")
    mock_placeholder.markdown.assert_any_call("Parte 1. Parte 2.▌")
    # A chamada final sem cursor
    mock_placeholder.markdown.assert_called_with("Parte 1. Parte 2.")

@patch("components.chat.st")
@patch("components.chat.get_response_stream")
def test_empty_content_ignored(mock_stream, mock_st):
    from components.chat import render_chat
    mock_st.session_state = MockSessionState({"messages": []})
    mock_st.chat_input.return_value = "Oxe"
    
    mock_stream.return_value = [
        {"event": "RunContent", "content": ""}
    ]
    
    mock_placeholder = MagicMock()
    mock_st.empty.return_value = mock_placeholder
    
    render_chat()
    mock_placeholder.markdown.assert_called_with("")
    # O markdown só é atualizado com o "▌" se content não for vazio no if
