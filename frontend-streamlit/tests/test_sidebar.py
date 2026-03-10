from unittest.mock import patch, MagicMock
import uuid

class MockSessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

@patch("components.sidebar.st")
def test_new_conversation_clears_history(mock_st):
    from components.sidebar import render_sidebar
    state = MockSessionState({
        "messages": [{"role": "user", "content": "old"}],
        "session_id": "old-id",
        "agents_used": ["acionar_pesquisador"]
    })
    mock_st.session_state = state
    mock_st.sidebar.__enter__ = lambda s: s
    mock_st.sidebar.__exit__ = MagicMock(return_value=False)
    
    # Simula o clique no botão "Nova Conversa"
    mock_st.button.return_value = True
    
    render_sidebar()
    
    # Verifica que o histórico foi limpo
    assert mock_st.session_state["messages"] == []
    assert mock_st.session_state["agents_used"] == []
    # Um novo session_id foi gerado
    assert mock_st.session_state["session_id"] != "old-id"

@patch("components.sidebar.st")
def test_no_clear_without_button_click(mock_st):
    from components.sidebar import render_sidebar
    original_msgs = [{"role": "user", "content": "msg1"}]
    state = MockSessionState({"messages": original_msgs, "session_id": "sess-1", "agents_used": []})
    mock_st.session_state = state
    mock_st.sidebar.__enter__ = lambda s: s
    mock_st.sidebar.__exit__ = MagicMock(return_value=False)
    
    # Botão NÃO clicado
    mock_st.button.return_value = False
    
    render_sidebar()
    
    # Histórico não deve ter sido alterado
    assert mock_st.session_state["messages"] == original_msgs
