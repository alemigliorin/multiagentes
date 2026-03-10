import streamlit as st

# Mapeamento visual para cada agente do projeto
AGENT_INFO_MAP = {
    "acionar_pesquisador": {"icon": "🔍", "name": "Pesquisador", "desc": "Buscando dados na internet"},
    "acionar_copywriter": {"icon": "✍️", "name": "Copywriter", "desc": "Escrevendo com a voz do Expert"},
    "acionar_juridico": {"icon": "⚖️", "name": "Jurídico", "desc": "Revisando compliance e limites legais"},
    "acionar_criador_experts": {"icon": "🧠", "name": "Criador Experts", "desc": "Pensando na estratégia e Big Idea"},
    "acionar_criador_midia": {"icon": "🎨", "name": "Criador de Mídia", "desc": "Gerando imagens e vídeos com IA"},
}

def render_tool_call(tool_name: str, tool_args: dict):
    """
    Renderiza um evento de Tool Call com o ícone e nome do agente acionado.
    
    Args:
        tool_name (str): O nome da ferramenta/agente (ex: 'acionar_pesquisador')
        tool_args (dict): Os argumentos JSON passados para a ferramenta.
    """
    info = AGENT_INFO_MAP.get(
        tool_name, 
        {"icon": "⚙️", "name": tool_name.replace("acionar_", "").capitalize(), "desc": "Processando"}
    )
    
    # st.status cria um bloco expansível animado simulando "carregando"
    with st.status(f"{info['icon']} **{info['name']}** — {info['desc']}...", expanded=False):
        st.caption("Argumentos enviados:")
        st.json(tool_args)
