import streamlit as st

def extract_metrics(run_completed_event: dict) -> dict:
    """
    Extrai métricas do evento RunCompleted do AgentOS.
    
    Args:
        run_completed_event (dict): O evento de RunCompleted com campo 'metrics'.
        
    Returns:
        dict: Dicionário com as métricas extraídas.
    """
    metrics = run_completed_event.get("metrics", {})
    return {
        "time": metrics.get("time", 0.0),
        "input_tokens": metrics.get("input_tokens", metrics.get("prompt_tokens", 0)),
        "output_tokens": metrics.get("output_tokens", metrics.get("completion_tokens", 0)),
    }

def count_agents_used(agents_used: list) -> int:
    """
    Conta os agentes especialistas que foram acionados.
    
    Args:
        agents_used (list): Lista de tool names.
        
    Returns:
        int: Número de agentes acionados.
    """
    return len(agents_used)

def render_metrics(run_completed_event: dict, agents_used: list):
    """
    Renderiza um painel de métricas após a conclusão de uma run.
    
    Args:
        run_completed_event (dict): O evento RunCompleted do SSE.
        agents_used (list): Lista de agentes acionados durante a run.
    """
    metrics = extract_metrics(run_completed_event)
    total_tokens = metrics["input_tokens"] + metrics["output_tokens"]
    elapsed = metrics["time"]
    n_agents = count_agents_used(agents_used)

    with st.expander("📊 Métricas da Execução", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏱️ Tempo", f"{elapsed:.1f}s")
        with col2:
            st.metric("🔢 Tokens", f"{total_tokens:,}")
        with col3:
            st.metric("🤖 Agentes", n_agents)
        
        if metrics["input_tokens"] or metrics["output_tokens"]:
            st.caption(f"↑ Entrada: {metrics['input_tokens']:,} tokens  |  ↓ Saída: {metrics['output_tokens']:,} tokens")
