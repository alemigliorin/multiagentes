from components.agent_monitor import track_agent_used, render_agent_pipeline, PIPELINE_ORDER
from unittest.mock import patch, MagicMock

class MockSessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

@patch("components.agent_monitor.st")
def test_pipeline_tracks_agents(mock_st):
    mock_st.session_state = MockSessionState({"agents_used": []})
    
    track_agent_used("acionar_pesquisador")
    track_agent_used("acionar_copywriter")
    
    assert "acionar_pesquisador" in mock_st.session_state["agents_used"]
    assert "acionar_copywriter" in mock_st.session_state["agents_used"]

@patch("components.agent_monitor.st")
def test_pipeline_no_duplicates(mock_st):
    mock_st.session_state = MockSessionState({"agents_used": []})
    
    track_agent_used("acionar_pesquisador")
    track_agent_used("acionar_pesquisador")  # Duplicate
    
    assert mock_st.session_state["agents_used"].count("acionar_pesquisador") == 1

@patch("components.agent_monitor.st")
def test_pipeline_shows_order(mock_st):
    # Passamos copywriter e pesquisador fora de ordem — deve render na ordem do pipeline
    agents = ["acionar_copywriter", "acionar_pesquisador"]
    render_agent_pipeline(agents)
    
    # Verifica que markdown foi chamado com conteúdo que inclui ambos os agentes
    calls = [str(c) for c in mock_st.markdown.call_args_list]
    combined = " ".join(calls)
    assert "Pesquisador" in combined
    assert "Copywriter" in combined
    # Pesquisador vem antes na ordem canônica PIPELINE_ORDER
    pesq_pos = combined.find("Pesquisador")
    copy_pos = combined.find("Copywriter")
    assert pesq_pos < copy_pos

@patch("components.agent_monitor.st")
def test_pipeline_handles_no_agents(mock_st):
    render_agent_pipeline([])
    mock_st.markdown.assert_not_called()
