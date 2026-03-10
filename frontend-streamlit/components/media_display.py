import re
import os
import glob
import streamlit as st

# Pasta onde o backend salva imagens e vídeos
BACKEND_TMP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "tmp"))
BACKEND_VIDEOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "videos"))

# Regex: detecta caminho de arquivo no texto de resposta do agente
IMAGE_PATH_PATTERN = re.compile(r"(?:tmp[\\/])?(imagem_\d+\.png)")
VIDEO_PATH_PATTERN = re.compile(r"(?:videos[\\/])?(video_\d+\.mp4)")

def detect_and_render_media(text: str):
    """
    Varre o texto de resposta do assistente e renderiza inline
    imagens ou vídeos mencionados pelo criador_midia.
    
    Args:
        text (str): Texto da resposta do assistente.
    """
    # --- Imagens ---
    for match in IMAGE_PATH_PATTERN.finditer(text):
        filename = match.group(1)
        img_path = os.path.join(BACKEND_TMP, filename)
        if os.path.exists(img_path):
            st.image(img_path, caption=f"🎨 Imagem gerada: {filename}", use_container_width=True)
        else:
            st.info(f"🎨 Imagem `{filename}` ainda está sendo gerada ou não foi encontrada.")

    # --- Vídeos ---
    for match in VIDEO_PATH_PATTERN.finditer(text):
        filename = match.group(1)
        vid_path = os.path.join(BACKEND_VIDEOS, filename)
        if os.path.exists(vid_path):
            st.video(vid_path)
            st.caption(f"🎬 Vídeo gerado: {filename}")
        else:
            st.info(f"⏳ Vídeo `{filename}` ainda está sendo processado na nuvem (Veo pode levar até 15 min).")
