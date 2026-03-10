import streamlit as st
import uuid
from config import BACKEND_HOST, AGENT_ID

def render_sidebar():
    """Renderiza a sidebar com controles de sessão e configuração."""
    with st.sidebar:
        st.title("🤖 Multiagentes")
        st.caption("Equipe de Agentes IA para Experts")
        st.divider()

        # --- NOVA CONVERSA ---
        if st.button("➕ Nova Conversa", use_container_width=True, type="primary"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.agents_used = []
            st.rerun()

        st.divider()

        # --- INFO DA SESSÃO ---
        st.subheader("📋 Sessão Atual")
        session_id = st.session_state.get("session_id", "—")
        st.caption(f"`{session_id[:18]}...`")
        msg_count = len(st.session_state.get("messages", []))
        st.metric("Mensagens", msg_count)

        st.divider()

        # --- AGENTES DA EQUIPE ---
        st.subheader("👥 Equipe de Agentes")
        agents_used = st.session_state.get("agents_used", [])
        agents_info = [
            {"id": "acionar_pesquisador", "icon": "🔍", "name": "Pesquisador"},
            {"id": "acionar_copywriter", "icon": "✍️", "name": "Copywriter"},
            {"id": "acionar_juridico", "icon": "⚖️", "name": "Jurídico"},
            {"id": "acionar_criador_experts", "icon": "🧠", "name": "Criador Experts"},
            {"id": "acionar_criador_midia", "icon": "🎨", "name": "Criador Mídia"},
        ]
        for agent in agents_info:
            used = agent["id"] in agents_used
            status = "🟢" if used else "⚪"
            st.markdown(f"{status} {agent['icon']} **{agent['name']}**")

        st.divider()

        # --- CONFIG DO BACKEND ---
        with st.expander("⚙️ Configuração"):
            current_host = st.text_input("Backend URL", value=BACKEND_HOST)
            if current_host != BACKEND_HOST:
                import config
                config.BACKEND_HOST = current_host
                config.AGENT_RUN_ENDPOINT = f"{current_host}/agents/{AGENT_ID}/runs"
                st.success("URL atualizada!")
