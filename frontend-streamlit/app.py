import streamlit as st
import uuid
import os
from components.chat import render_chat
from components.sidebar import render_sidebar

# --- Page Config ---
st.set_page_config(
    page_title="Multiagentes — Expert AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Injetar CSS customizado ---
css_path = os.path.join(os.path.dirname(__file__), "styles", "theme.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Inicializa estado global ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agents_used" not in st.session_state:
    st.session_state.agents_used = []

# --- Sidebar ---
render_sidebar()

# --- Header ---
st.title("🤖 Orquestrador de Experts")
st.markdown(
    "Sua equipe de IA para **pesquisa**, **copywriting**, **conformidade legal**, "
    "**identidade de Expert** e **criação de mídia** — tudo em uma só conversa."
)
st.divider()

# --- Área de Chat ---
render_chat()
