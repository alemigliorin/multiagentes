# noqa: E501
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Inicializa o client garantindo o uso do AI Studio (Free Tier) pela chave de API explicitada
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

VEO_JOBS_FILE = os.path.join("tmp", "veo_jobs.json")


def _load_jobs() -> dict:
    import json

    if not os.path.exists(VEO_JOBS_FILE):
        return {}
    try:
        with open(VEO_JOBS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_jobs(jobs: dict):
    import json

    os.makedirs(os.path.dirname(VEO_JOBS_FILE), exist_ok=True)
    with open(VEO_JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=4)


def gerar_imagem(prompt: str) -> str:
    """
    Gera uma imagem a partir de um prompt hiper-detalhado usando o modelo do Google (Nano Banana / Imagen 3).
    Sempre use essa ferramenta quando o usuário pedir para visualizar um conceito, criar uma capa, ou desenhar algo.

    Args:
        prompt (str): A descrição hiper-detalhada da imagem.

    Returns:
        str: Caminho local do arquivo da imagem gerada.
    """
    filename = f"imagem_{int(time.time())}.png"
    output_dir = "tmp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    try:
        # Utilizando o imagen-4.0 que já está disponível na SDK
        result = client.models.generate_images(
            model="imagen-4.0-fast-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9", output_mime_type="image/png"),
        )
        if result and result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            return f"Sucesso: Imagem gerada e salva em '{output_path}'"
        else:
            return "Falha ao gerar a imagem: Nenhuma imagem retornada pela API."
    except Exception as e:
        return f"Erro ao gerar imagem. Verifique se a sua API_KEY tem permissão para este modelo. Erro: {str(e)}"


def gerar_video(prompt: str, image_url: str = None) -> str:
    """
    Gera um vídeo usando o modelo Google Veo a partir de um prompt e opcionalmente guiado por uma imagem.
    Sempre use essa ferramenta quando o usuário pedir para gerar uma cena estendida, animar uma idéia ou requisitar vídeo.

    Args:
        prompt (str): A descrição cinematográfica e detalhada da cena, movimento e ambiente.
        image_url (str, optional): Um link ou base64 de uma imagem inicial (image-to-video). Opcional.

    Returns:
        str: Mensagem de status com o caminho do vídeo gerado.
    """
    filename = f"video_{int(time.time())}.mp4"
    output_dir = "videos"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    try:
        # Acesso ao modelo Veo via nova SDK google-genai.
        # Como o Veo gera midia pesada, isso tipicamente é assíncrono ou usa um LRO (Long Running Operation).
        # Este é o wrapper padrão assumindo acesso à build Vertex/AI Studio avançada.
        # No caso de acesso não estar disponível através da biblioteca Python, isso retornará o erro explicativo.

        # Este bloco é uma implementação baseada na interface experada da SDK genai
        # de Models para vídeo.
        try:
            # Retorna no LRO (Long Running Operation)
            result = client.models.generate_videos(model="veo-3.1-fast-generate-preview", prompt=prompt, config={"aspect_ratio": "16:9"})

            if result and hasattr(result, "name") and result.name:
                job_id = result.name
                jobs = _load_jobs()
                jobs[job_id] = {
                    "prompt": prompt,
                    "status": "pending",
                    "created_at": time.time(),
                    "output_path": output_path,
                }
                _save_jobs(jobs)
                return (
                    f"VÍDEO ENVIADO PARA A FILA COM SUCESSO! O vídeo está sendo gerado pela nuvem. Job ID (Operação): '{job_id}'. "
                    "Salve esse ID! Use a ferramenta 'consultar_status_video' com esse ID para verificar se o vídeo está pronto e "
                    "fazer o download final. O aviso atual é apenas de envio, o arquivo ainda não existe."
                )
            else:
                return "O comando foi enviado, mas não recebi um Job ID rastreável da API. Talvez o modelo não suporte operações assíncronas no momento."

        except AttributeError:
            return "A função client.models.generate_videos não exportou funções suportadas. A sua conta/SDK não suporta esta ação."

    except Exception as e:
        return f"Erro fatal ao despachar o vídeo com Veo. Erro: {str(e)}"


def consultar_status_video(job_id: str) -> str:
    """
    Consulta o status de uma operação de vídeo pendente no Google Veo (LRO) e faz o download quando concluída.
    Sempre chame essa ferramenta quando o usuário perguntar se um vídeo ficou pronto, ou se você mesmo acabou de enviar um prompt de vídeo há pouco tempo.

    Args:
        job_id (str): O ID da operação retornada pela ferramenta `gerar_video` anteriormente.

    Returns:
        str: Mensagem indicando o status (gerando, concluído, erro) e o local do arquivo final.
    """
    import requests

    jobs = _load_jobs()
    if job_id not in jobs:
        return f"O Job ID '{job_id}' não foi encontrado nos registros pendentes locais. Tem certeza de qual ID usar?"

    job = jobs[job_id]

    if job.get("status") == "completed" and os.path.exists(job.get("output_path", "")):
        return f"O vídeo já havia sido concluído e está salvo pronto para uso em: '{job['output_path']}'"

    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/{job_id}?key={api_key}"

        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Erro na API do Google ao consultar o Job: HTTP {response.status_code} - {response.text}"

        data = response.json()

        if data.get("done"):
            if "error" in data:
                job["status"] = "failed"
                job["error_details"] = str(data["error"])
                _save_jobs(jobs)
                return f"A geração do vídeo falhou no servidor do Google. Erro: {data['error']}"

            # Tenta extrair a URI do vídeo gerado
            try:
                video_uri = data["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]

                # Faz o download do video
                download_url = f"{video_uri}&key={api_key}" if "?" in video_uri else f"{video_uri}?key={api_key}"
                print(f"[Sistema] Baixando vídeo renderizado de {video_uri}...")

                vid_resp = requests.get(download_url, stream=True, timeout=30)
                if vid_resp.status_code == 200:
                    output_path = job["output_path"]
                    with open(output_path, "wb") as f:
                        for chunk in vid_resp.iter_content(chunk_size=8192):
                            f.write(chunk)

                    job["status"] = "completed"
                    _save_jobs(jobs)
                    return f"VÍDEO CONCLUÍDO E BAIXADO COM SUCESSO! Informar ao usuário que o vídeo está finalizado e pronto no caminho: '{output_path}'"
                else:
                    return f"Vídeo concluído, mas falhou ao baixar: HTTP {vid_resp.status_code}"

            except KeyError as e:
                job["status"] = "failed"
                _save_jobs(jobs)
                return f"Operação foi dada como terminada, mas formato de resposta inesperado: {str(e)}"
        else:
            return "O vídeo ainda está sendo PROCESSADO na fila da nuvem do Google (Veo é demorado, muitas vezes leva mais de 5 a 15 minutos). Por favor aguarde e verifique novamente mais tarde."

    except Exception as e:
        return f"Erro ao tentar consultar o job via HTTP. Erro: {str(e)}"
