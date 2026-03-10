from components.tool_display import render_tool_call, AGENT_INFO_MAP
from unittest.mock import patch, MagicMock

@patch("components.tool_display.st")
def test_agent_name_mapping(mock_st):
    tool_args = {"query": "teste"}
    render_tool_call("acionar_pesquisador", tool_args)
    
    mock_st.status.assert_called_once()
    status_label = mock_st.status.call_args[0][0]
    assert "Pesquisador" in status_label
    assert "🔍" in status_label

@patch("components.tool_display.st")
def test_tool_args_displayed(mock_st):
    mock_status_context = MagicMock()
    mock_st.status.return_value.__enter__.return_value = mock_status_context
    
    tool_args = {"instrucao": "Venda agressiva"}
    render_tool_call("acionar_copywriter", tool_args)
    
    mock_st.json.assert_called_once_with({"instrucao": "Venda agressiva"})

@patch("components.tool_display.st")
def test_unknown_tool_fallback(mock_st):
    render_tool_call("acionar_desconhecido", {})
    
    status_label = mock_st.status.call_args[0][0]
    assert "⚙️" in status_label
    assert "Desconhecido" in status_label
