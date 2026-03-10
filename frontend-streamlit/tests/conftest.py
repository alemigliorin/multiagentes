import pytest
import json

@pytest.fixture
def mock_tool_call_event():
    def _create_event(tool_name="acionar_pesquisador", tool_args=None):
        if tool_args is None:
            tool_args = {"query": "test"}
        return {
            "event": "ToolCallStarted",
            "tool": {
                "tool_name": tool_name,
                "tool_args": tool_args
            }
        }
    return _create_event

@pytest.fixture
def mock_sse_response():
    events = [
        {"event": "RunStarted"},
        {"event": "ToolCallStarted", "tool": {"tool_name": "acionar_pesquisador", "tool_args": {"query": "test"}}},
        {"event": "ToolCallCompleted"},
        {"event": "RunContent", "content": "Olá! "},
        {"event": "RunContent", "content": "Esta é uma resposta de teste."},
        {"event": "RunCompleted", "metrics": {"time": 1.5, "prompt_tokens": 10}}
    ]
    
    # Simula as linhas que o request.iter_lines() retornaria
    lines = []
    for event in events:
        data_str = json.dumps(event)
        lines.append(f"data: {data_str}".encode('utf-8'))
        lines.append(b"") # linha vazia comum no SSE
        
    return lines

@pytest.fixture
def sample_messages_history():
    return [
        {"role": "user", "content": "Pesquise sobre Python"},
        {"role": "assistant", "content": "Aqui estão as informações sobre Python..."}
    ]
