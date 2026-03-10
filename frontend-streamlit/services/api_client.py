import requests
import json
from config import AGENT_RUN_ENDPOINT

def get_response_stream(message: str, session_id: str = "default_session"):
    """
    Sends a message to the AgentOS backend and yields the SSE events.
    
    Args:
        message (str): The user message.
        session_id (str): Optional session identifier to maintain history.
        
    Yields:
        dict: The parsed JSON event from the SSE stream.
    """
    try:
        response = requests.post(
            url=AGENT_RUN_ENDPOINT,
            data={
                "message": message,
                "stream": "true",
                "session_id": session_id
            },
            stream=True,
            timeout=(10, 300)  # (connect timeout 10s, read timeout 5min para cadeia multi-agente)
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                # SSE lines start with 'data: '
                if line.startswith(b'data: '):
                    data_str = line[6:].decode('utf-8')
                    try:
                        event = json.loads(data_str)
                        yield event
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.RequestException as e:
        yield {"event": "RunError", "error_message": f"Erro de conexão com o backend: {str(e)}"}
