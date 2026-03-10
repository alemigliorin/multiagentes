import os
import pytest
from unittest.mock import patch, MagicMock
from components.media_display import detect_and_render_media, IMAGE_PATH_PATTERN, VIDEO_PATH_PATTERN

def test_image_path_detection():
    text = "Imagem gerada e salva em 'tmp/imagem_1234567890.png'"
    matches = IMAGE_PATH_PATTERN.findall(text)
    assert len(matches) == 1
    assert matches[0] == "imagem_1234567890.png"

def test_video_path_detection():
    text = "Vídeo salvo em videos/video_9876543210.mp4"
    matches = VIDEO_PATH_PATTERN.findall(text)
    assert len(matches) == 1
    assert matches[0] == "video_9876543210.mp4"

def test_no_media_in_plain_text():
    text = "Esta é uma resposta sem nenhuma mídia mencionada."
    assert not IMAGE_PATH_PATTERN.findall(text)
    assert not VIDEO_PATH_PATTERN.findall(text)

@patch("components.media_display.st")
@patch("components.media_display.os.path.exists")
def test_image_renders_when_exists(mock_exists, mock_st):
    mock_exists.return_value = True
    detect_and_render_media("Imagem salva em tmp/imagem_111.png")
    mock_st.image.assert_called_once()

@patch("components.media_display.st")
@patch("components.media_display.os.path.exists")
def test_missing_image_shows_placeholder(mock_exists, mock_st):
    mock_exists.return_value = False
    detect_and_render_media("Imagem salva em tmp/imagem_222.png")
    mock_st.image.assert_not_called()
    mock_st.info.assert_called_once()
    assert "222" in mock_st.info.call_args[0][0]

@patch("components.media_display.st")
@patch("components.media_display.os.path.exists")
def test_video_status_completed(mock_exists, mock_st):
    mock_exists.return_value = True
    detect_and_render_media("Vídeo gerado em videos/video_333.mp4")
    mock_st.video.assert_called_once()

@patch("components.media_display.st")
@patch("components.media_display.os.path.exists")
def test_video_status_pending(mock_exists, mock_st):
    mock_exists.return_value = False
    detect_and_render_media("Vídeo em fila: videos/video_444.mp4")
    mock_st.video.assert_not_called()
    mock_st.info.assert_called_once()
    # Verifica que a mensagem indica que está sendo processado
    info_msg = mock_st.info.call_args[0][0]
    assert "processado" in info_msg or "444" in info_msg
