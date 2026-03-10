# Multi-stage build para manter a imagem leve
FROM python:3.12-slim AS builder

# Instala o utilitário 'uv'
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copia os arquivos de dependência
COPY pyproject.toml uv.lock* ./

# Instala as dependências de produção num environment isolado
RUN uv sync --frozen --no-install-project --no-dev

# ==========================================

FROM python:3.12-slim AS runtime

# Instala ffmpeg no Ubuntu (necessário para transcripter.py)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia as dependências do builder
COPY --from=builder /app/.venv /app/.venv

# Copia o código fonte do backend
COPY . .

# Adiciona o venv ao PATH global
ENV PATH="/app/.venv/bin:$PATH"

# Expõe a porta 8000
EXPOSE 8000

# Roda o servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
