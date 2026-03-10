FROM python:3.12-slim

WORKDIR /app

# Instala o uv para gerenenciamento de dependências
RUN pip install uv

# Copia os arquivos de projeto
COPY pyproject.toml .
COPY . .

# Instala dependências (sem extras de dev/test)
RUN uv sync --no-dev

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Entrypoint
CMD ["uv", "run", "streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
