import streamlit as st
from services.api_client import get_response_stream
from components.tool_display import render_tool_call
from components.agent_monitor import track_agent_used, render_agent_pipeline
from components.media_display import detect_and_render_media
from components.metrics import render_metrics

def render_chat():
    """Renderiza a interface principal de chat com streaming SSE."""

    # Inicializa histórico e lista de agentes usados
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agents_used" not in st.session_state:
        st.session_state.agents_used = []

    # Exibe histórico guardado
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("pipeline"):
                render_agent_pipeline(msg["pipeline"])
            st.markdown(msg["content"])
            detect_and_render_media(msg["content"])

    # Input do usuário
    if prompt := st.chat_input("Como posso ajudar com a operação digital do seu Expert hoje?"):
        # Armazena e exibe mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Reset da lista de agentes acionados nesta run
        current_run_agents = []

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            run_completed_event = None  # Capturado ao final da run

            try:
                for event in get_response_stream(prompt, session_id=st.session_state.get("session_id", "default")):
                    event_type = event.get("event", "")

                    if event_type == "ToolCallStarted":
                        tool_name = event.get("tool", {}).get("tool_name", "Unknown")
                        tool_args = event.get("tool", {}).get("tool_args", {})
                        render_tool_call(tool_name, tool_args)
                        # Rastreia o agente acionado
                        track_agent_used(tool_name)
                        if tool_name not in current_run_agents:
                            current_run_agents.append(tool_name)

                    elif event_type == "RunContent":
                        content = event.get("content", "")
                        if content:
                            full_response += content
                            response_placeholder.markdown(full_response + "▌")

                    elif event_type == "RunCompleted":
                        run_completed_event = event

                    elif event_type == "RunError":
                        st.error(event.get("error_message", "Ocorreu um erro na execução."))
                        break

            except Exception as e:
                st.error(f"Erro inesperado: {str(e)}")

            # Exibe pipeline desta resposta
            if current_run_agents:
                render_agent_pipeline(current_run_agents)

            # Remove cursor e exibe resposta final
            response_placeholder.markdown(full_response)

            # Renderiza mídia mencionada na resposta
            if full_response:
                detect_and_render_media(full_response)

            # Exibe métricas da run (se disponíveis)
            if run_completed_event:
                render_metrics(run_completed_event, current_run_agents)

            # Salva no histórico (com o pipeline da run)
            if full_response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "pipeline": current_run_agents
                })
