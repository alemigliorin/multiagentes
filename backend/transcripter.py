import json
import os
import shutil
import subprocess  # nosec B404
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Importante: Defina a variável de ambiente GROQ_API_KEY no arquivo .env
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def get_ffmpeg_path() -> str:
    """Busca o ffmpeg no PATH do sistema, o que funciona nativamente em Windows e Linux/Docker"""
    path = shutil.which("ffmpeg")
    if path:
        return path

    raise FileNotFoundError("ffmpeg não encontrado no PATH. Instale com 'apt-get install ffmpeg' (Linux) ou 'winget install Gyan.FFmpeg' (Windows).")


def extract_audio(video_path: Path, audio_path: Path):
    """Extrai o audio do video usando ffmpeg para reduzir tamanho antes de enviar para a API."""
    command = [
        get_ffmpeg_path(),
        "-i",
        str(video_path),
        "-q:a",
        "0",  # Qualidade de áudio original
        "-map",
        "a",  # Mapear apenas os streams de áudio
        "-y",  # Sobrescreve se existir
        str(audio_path),
    ]
    # Executa o comando ocultando o output no terminal
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)  # nosec B603


def transcribe_audio(audio_path: Path) -> str:
    """Usa a API da Groq para transcrever o áudio."""
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path.name, file.read()),
            model="whisper-large-v3",  # Modelo da Groq para Whisper
            response_format="json",
            language="pt",  # Pode remover caso os vídeos sejam em inglês
        )
    return transcription.text


def process_directory(base_dir: str = "videos", output_json: str = "transcricoes.json"):
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"Diretório '{base_dir}' não encontrado.")
        return

    transcriptions = {}
    valid_extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm"}

    # Interage sobre todos os arquivos na pasta e subpastas de forma recursiva
    for video_path in base_path.rglob("*"):
        if video_path.is_file() and video_path.suffix.lower() in valid_extensions:
            # Descobre o nome do criador baseado na subpasta imediata após '@videos'
            rel_path = video_path.relative_to(base_path)
            creator = rel_path.parts[0] if len(rel_path.parts) > 1 else "desconhecido"

            print(f"Processando: {video_path.name} | Criador: {creator}")

            # Arquivo temporário de áudio
            audio_path = video_path.with_suffix(".mp3")

            try:
                print("  -> Extraindo áudio...")
                extract_audio(video_path, audio_path)

                print("  -> Transcrevendo via Groq...")
                text = transcribe_audio(audio_path)

                # Salva os dados no dicionário de resultados
                if creator not in transcriptions:
                    transcriptions[creator] = []

                transcriptions[creator].append({"arquivo": video_path.name, "caminho_completo": str(video_path), "transcricao": text})
                print("  -> Sucesso!")

            except Exception as e:
                print(f"  -> Erro ao processar {video_path.name}: {e}")
            finally:
                # Remove o arquivo de áudio temporário para economizar espaço
                if audio_path.exists():
                    audio_path.unlink()

    # Salva todos os resultados em um JSON formatado
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(transcriptions, f, ensure_ascii=False, indent=4)

    print(f"\nFinalizado! Resultados consolidados salvos em '{output_json}'.")


if __name__ == "__main__":
    process_directory()
