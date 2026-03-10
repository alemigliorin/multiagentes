import streamlit as st

# Ordem canônica de execução da equipe  
PIPELINE_ORDER = [
    "acionar_pesquisador",
    "acionar_copywriter",
    "acionar_juridico",
    "acionar_criador_experts",
    "acionar_criador_midia",
]

AGENT_INFO = {
    "acionar_pesquisador":      {"icon": "🔍", "name": "Pesquisador",      "color": "#4A90E2"},
    "acionar_copywriter":       {"icon": "✍️", "name": "Copywriter",       "color": "#7B68EE"},
    "acionar_juridico":         {"icon": "⚖️", "name": "Jurídico",         "color": "#E2844A"},
    "acionar_criador_experts":  {"icon": "🧠", "name": "Criador Experts",  "color": "#68EE7B"},
    "acionar_criador_midia":    {"icon": "🎨", "name": "Criador Mídia",    "color": "#E24A90"},
}

def track_agent_used(tool_name: str):
    """Regista que um agente foi acionado nesta run."""
    if "agents_used" not in st.session_state:
        st.session_state.agents_used = []
    if tool_name not in st.session_state.agents_used:
        st.session_state.agents_used.append(tool_name)

def render_agent_pipeline(agents_used: list):
    """
    Renderiza um pipeline visual dos agentes acionados durante a última resposta.
    
    Args:
        agents_used (list): Lista de tool names acionados na run atual.
    """
    if not agents_used:
        return

    st.markdown("**🔗 Pipeline desta resposta:**")

    # Filtra e ordena pelos que foram usados, na ordem do pipeline
    ordered = [a for a in PIPELINE_ORDER if a in agents_used]
    # Adiciona quaisquer outros que não estejam na ordem padrão
    extras = [a for a in agents_used if a not in PIPELINE_ORDER]
    pipeline = ordered + extras

    # Renderiza em linha com setas
    parts = []
    for tool_name in pipeline:
        info = AGENT_INFO.get(tool_name, {"icon": "⚙️", "name": tool_name})
        parts.append(f"{info['icon']} **{info['name']}**")

    pipeline_str = " → ".join(parts)
    st.markdown(pipeline_str)
    st.markdown("---")
