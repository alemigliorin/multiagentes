from components.metrics import extract_metrics, count_agents_used, render_metrics
from unittest.mock import patch, MagicMock

# --- Evento de RunCompleted de exemplo ---
SAMPLE_RUN_COMPLETED = {
    "event": "RunCompleted",
    "metrics": {
        "time": 3.72,
        "input_tokens": 850,
        "output_tokens": 420,
        "prompt_tokens": 850,       # alias alternativo
        "completion_tokens": 420    # alias alternativo
    }
}

def test_metrics_extracted_from_run_completed():
    m = extract_metrics(SAMPLE_RUN_COMPLETED)
    assert m["time"] == 3.72
    assert m["input_tokens"] == 850
    assert m["output_tokens"] == 420

def test_metrics_with_empty_event():
    m = extract_metrics({"event": "RunCompleted"})
    assert m["time"] == 0.0
    assert m["input_tokens"] == 0
    assert m["output_tokens"] == 0

def test_agents_used_count():
    agents = ["acionar_pesquisador", "acionar_copywriter", "acionar_juridico"]
    assert count_agents_used(agents) == 3

def test_agents_used_count_empty():
    assert count_agents_used([]) == 0

def test_metrics_display_format():
    m = extract_metrics(SAMPLE_RUN_COMPLETED)
    # Valida que o tempo é formatável como "X.Xs"
    assert f"{m['time']:.1f}s" == "3.7s"
    # Total de tokens
    total = m["input_tokens"] + m["output_tokens"]
    assert f"{total:,}" == "1,270"

@patch("components.metrics.st")
def test_render_metrics_calls_expander(mock_st):
    mock_expander = MagicMock()
    mock_expander.__enter__ = lambda s: s
    mock_expander.__exit__ = MagicMock(return_value=False)
    mock_st.expander.return_value = mock_expander

    mock_col = MagicMock()
    mock_col.__enter__ = lambda s: s
    mock_col.__exit__ = MagicMock(return_value=False)
    mock_st.columns.return_value = [mock_col, mock_col, mock_col]
    
    render_metrics(SAMPLE_RUN_COMPLETED, ["acionar_pesquisador"])
    mock_st.expander.assert_called_once()
    mock_st.columns.assert_called_once_with(3)
    assert mock_st.metric.call_count == 3
