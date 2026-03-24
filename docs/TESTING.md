# Estratégia de Testes

## Visão Geral

A estratégia é dividida em duas camadas complementares:

| Camada | Ferramenta | Quando usar |
|--------|-----------|-------------|
| Diagnóstico | Scripts manuais (`test_*.py`) | Verificar integrações externas em tempo real |
| Automatizado | pytest (unit + integration) | CI/CD, antes de todo push |

---

## Scripts de Diagnóstico

Localizados na raiz do `backend/`. Usam os módulos refatorados (`agents/`, `config/`, `knowledge/`) e requerem variáveis de ambiente reais configuradas no `.env`.

### `test_search.py` — Busca Web

Testa três camadas em sequência:
1. Conexão direta com a Tavily API
2. Agente Pesquisador (`agents/specialists.py` → `get_pesquisador()`)
3. Orquestrador delegando para o Pesquisador (`agents/orchestrator.py`)

### `test_orq.py` — Orquestrador

Envia uma mensagem diretamente para o orquestrador (`orquestrador.run(...)`). Útil para testar delegação para o Criador de Mídia ou outros agentes.

### `test_db_conn.py` — Banco de Dados

Verifica conectividade com o PostgreSQL via `settings.SUPABASE_DB_URL` usando `psycopg2`.

### `test_pdf_init.py` — RAG / PgVector

Chama `get_pdf_knowledge()` de `knowledge/pdf_knowledge.py` e verifica se a base inicializa sem erros.

### Como rodar

```powershell
# Windows — todos os diagnósticos de uma vez
test.bat

# Individual
cd backend
$env:SKIP_PDF_LOAD="1"; uv run test_search.py
$env:SKIP_PDF_LOAD="1"; uv run test_orq.py
uv run test_db_conn.py
uv run test_pdf_init.py
```

> `SKIP_PDF_LOAD=1` ignora o carregamento do RAG quando não é o foco do teste.

---

## Testes Automatizados (pytest)

```
backend/tests/
├── conftest.py                        # Fixtures globais (env vars mock, VCR config, tmp_dir)
├── unit/
│   ├── test_get_model.py              # agents/factory.py — get_model() para cada provider
│   ├── test_cors.py                   # config/cors.py — parse_allowed_origins()
│   ├── test_agent_wrappers.py         # Wrappers dos agentes especialistas
│   ├── test_media_tools.py            # media_tools.py
│   ├── test_reels_tools.py            # reels_tools.py
│   └── test_transcripter.py          # transcripter.py
└── integration/
    ├── test_api.py                    # Endpoints principais (health, CORS, OPTIONS)
    ├── test_uploads.py                # POST /upload-pdf e /upload-video
    ├── test_vcr_agent.py              # Agentes com cassettes VCR
    └── cassettes/                     # Respostas gravadas para VCR
```

### Fixtures globais (`conftest.py`)

- **`mock_env`** (autouse): Define variáveis de ambiente falsas para todos os testes. Evita uso de chaves reais.
- **`vcr_config`**: Filtra headers sensíveis das gravações VCR.
- **`tmp_dir`**: Diretório temporário para testes que escrevem arquivos.
- **`sample_transcriptions`**: Dicionário de exemplo para testes de reels.

### Como rodar

```bash
cd backend

# Todos os testes
uv run pytest

# Com cobertura
uv run pytest --cov=. --cov-report=term-missing

# Apenas unitários
uv run pytest tests/unit/ -v

# Apenas integração
uv run pytest tests/integration/ -v

# Teste específico
uv run pytest tests/unit/test_cors.py -v
```

### Configuração (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]         # Permite imports como "from agents.factory import ..."
addopts = "-v --tb=short"

[tool.coverage.run]
omit = ["main.py", "test_*.py", "tests/*", ".venv/*"]
```

> **Nota para o IDE:** O IDE pode mostrar erros de import nos arquivos de teste porque não lê `pythonpath` do pytest. Os testes funcionam corretamente via `uv run pytest`. Para corrigir no IDE, configure o interpretador Python para apontar para `backend/.venv`.

---

## Qualidade de Código

```powershell
# Todos os checks de uma vez
quality.bat

# Individual
cd backend
uv run ruff check . --exclude .venv     # Linting
uv run ruff format .                    # Formatação
uv run bandit -r . -x .venv,tests/ -ll  # Segurança
uv run pip-audit                        # CVEs nas dependências
```

---

## CI/CD

O GitHub Actions executa em todo push para `main`:

1. `ruff check` — linting
2. `bandit` — análise de segurança
3. `pytest` — suite completa
4. Build das imagens Docker

Se qualquer etapa falhar, o build é bloqueado e as imagens não são publicadas no GHCR.

---

## Cobertura dos Testes

### O que está coberto

| Módulo | Tipo | Status |
|--------|------|--------|
| `agents/factory.py` — `get_model()` | Unit | 9 casos |
| `config/cors.py` — `parse_allowed_origins()` | Unit | 10 casos |
| `routers/uploads.py` — PDF e vídeo | Integration | 7 casos |
| `routers/health.py` | Integration | 2 casos |
| CORS preflight | Integration | 2 casos |

### Próximos testes a implementar

| Módulo | Teste | Prioridade |
|--------|-------|-----------|
| `middleware/auth_logging.py` | Token inválido → 401; OPTIONS → passa sem auth | Alta |
| `agents/specialists.py` | Lazy-load instancia agente apenas na primeira chamada | Média |
| `knowledge/pdf_knowledge.py` | `SKIP_PDF_LOAD=1` retorna None; conectado retorna instância | Média |
| `agents/factory.py` — `create_agent()` | Agente criado com instruções lidas do arquivo `.md` | Média |
