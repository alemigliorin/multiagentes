import re

from config.settings import settings


def parse_allowed_origins(raw_origins: str = None) -> list[str]:
    """
    Parses a string of allowed origins (comma or semicolon separated).
    Ensures domains are cleaned of quotes and trailing slashes.
    """
    raw = raw_origins or settings.CORS_ORIGINS

    # Suporte a múltiplos separadores (vírgula ou ponto e vírgula) e limpeza de espaços/aspas
    origins = [
        o.strip().strip("'").strip('"').rstrip('/')
        for o in re.split(r'[;,]', raw)
        if o.strip()
    ]

    return origins
