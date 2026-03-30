import logging
from auth import get_supabase
from config.settings import settings

logger = logging.getLogger(__name__)

# O nome do bucket a ser usado no Supabase Storage
MEDIA_BUCKET = "media"

def _ensure_bucket_exists():
    """Garante que o bucket de mídia existe e tem configuração pública. Retorna True se pronto."""
    supabase = get_supabase()
    if not supabase:
        logger.error("Supabase client não inicializado.")
        return False
        
    try:
        # Tenta listar os buckets para verificar
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if MEDIA_BUCKET not in bucket_names:
            logger.info(f"Criando bucket '{MEDIA_BUCKET}' no Supabase...")
            supabase.storage.create_bucket(MEDIA_BUCKET, options={"public": True})
            return True
        return True
    except Exception as e:
        # Se falhar por falta de permissão (403), mas o bucket já tiver sido criado manualmente (ou via SQL),
        # deixamos o fluxo seguir pois o upload/download pode estar liberado via RLS no bucket.
        if "403" in str(e) or "Unauthorized" in str(e):
            logger.warning(f"Aviso de permissão ao verificar bucket {MEDIA_BUCKET} (403). Continuando mesmo assim...")
            return True
        logger.error(f"Erro ao verificar/criar bucket {MEDIA_BUCKET}: {e}")
        return False

def upload_media(file_bytes: bytes, filename: str, content_type: str = None) -> str:
    """
    Faz upload de um arquivo para o Supabase Storage.
    
    Args:
        file_bytes: O conteúdo do arquivo em bytes
        filename: O caminho/nome do arquivo (ex: 'images/imagem_123.png' ou 'videos/video_123.mp4')
        content_type: O MIME type (ex: 'image/png' ou 'video/mp4')
        
    Returns:
        str: A URL pública direta para o arquivo, ou None em caso de erro.
    """
    _ensure_bucket_exists()
    supabase = get_supabase()
    
    if not supabase:
        return None
        
    try:
        # Se um content_type for fornecido, a gente envia. Senão deixa o Supabase inferir (pode ser application/octet-stream)
        file_options = {"content-type": content_type} if content_type else {}
        
        logger.info(f"Fazendo upload para Supabase: {filename}")
        res = supabase.storage.from_(MEDIA_BUCKET).upload(
            path=filename,
            file=file_bytes,
            file_options=file_options
        )
        
        # Recupera a URL pública
        public_url = supabase.storage.from_(MEDIA_BUCKET).get_public_url(filename)
        return str(public_url)
    except Exception as e:
        logger.error(f"Erro no upload para Supabase ({filename}): {e}")
        # A própria lib pode levantar StorageException se o arquivo já existir ou houver problema com as políticas (RLS)
        return None

def list_media() -> list:
    """
    Lista os arquivos de mídia (imagens e vídeos) do Supabase Storage.
    Note: Supabase storage.list() lista apenas dentro do folder, precisaremos consultar
    'images' e 'videos' que são os prefixos lógicos que vamos usar.
    """
    _ensure_bucket_exists()
    supabase = get_supabase()
    
    if not supabase:
        return []
        
    all_files = []
    
    try:
        # Buscar imagens
        images_res = supabase.storage.from_(MEDIA_BUCKET).list("images")
        for f in images_res:
            if f.get("name") and f.get("name") != ".emptyFolderPlaceholder":
                # get_public_url expects the full path including the folder
                full_path = f"images/{f['name']}"
                public_url = str(supabase.storage.from_(MEDIA_BUCKET).get_public_url(full_path))
                
                # Supabase retorna `created_at` (str ISO) ou metadados na query. 
                # Vamos converter o metadata retornado pelo list.
                # O formato exato depende do cliente postgrest.
                
                # O list normalmente retorna [{"name": "file.png", "created_at": "...", "metadata": {"size": ...}}]
                size = f.get("metadata", {}).get("size", 0) if isinstance(f.get("metadata"), dict) else 0
                
                # Para simplificar a compatibilidade com nossa feature existente, fake created timestamp based on object
                import dateutil.parser
                created_ts = 0
                if f.get("created_at"):
                    try:
                        created_ts = dateutil.parser.isoparse(f["created_at"]).timestamp()
                    except:
                        pass
                
                all_files.append({
                    "filename": f["name"],
                    "type": "image",
                    "size": size,
                    "created": created_ts,
                    "url": public_url
                })
                
        # Buscar vídeos
        videos_res = supabase.storage.from_(MEDIA_BUCKET).list("videos")
        for f in videos_res:
            if f.get("name") and f.get("name") != ".emptyFolderPlaceholder":
                full_path = f"videos/{f['name']}"
                public_url = str(supabase.storage.from_(MEDIA_BUCKET).get_public_url(full_path))
                
                size = f.get("metadata", {}).get("size", 0) if isinstance(f.get("metadata"), dict) else 0
                import dateutil.parser
                created_ts = 0
                if f.get("created_at"):
                    try:
                        created_ts = dateutil.parser.isoparse(f["created_at"]).timestamp()
                    except:
                        pass
                
                all_files.append({
                    "filename": f["name"],
                    "type": "video",
                    "size": size,
                    "created": created_ts,
                    "url": public_url
                })
                
    except Exception as e:
        logger.error(f"Erro ao listar mídias no Supabase: {e}")
        
    # Ordenar por data (recente primeiro)
    all_files.sort(key=lambda x: x["created"], reverse=True)
    return all_files
