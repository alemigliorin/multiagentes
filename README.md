# Multiagentes — Plataforma de Agentes de IA

Sistema de múltiplos agentes de IA especializados, orquestrados de forma inteligente para executar tarefas complexas de pesquisa, geração de conteúdo, análise jurídica, criação de mídia e análise de documentos.

## Visão Geral

| Camada | Tecnologia | Porta |
|--------|-----------|-------|
| Backend (API) | Python, FastAPI, Agno | 8000 |
| Frontend | Next.js 16, React 18, TypeScript | 3000 |
| Banco de Dados | Supabase (Auth + DB) + PgVector | — |

## Documentação

- [Arquitetura](docs/ARCHITECTURE.md) — Estrutura do sistema, agentes e fluxo de dados
- [Funcionalidades](docs/FUNCTIONALITIES.md) — Agentes, ferramentas e endpoints
- [Estratégia de Testes](docs/TESTING.md) — Tipos de testes, cobertura e como rodar
- [Deploy](docs/DEPLOY.md) — Ambientes, CI/CD e instruções para VPS

## Início Rápido

### Pré-requisitos

- Python 3.12+ com [uv](https://github.com/astral-sh/uv)
- Node.js 18+
- Arquivo `.env` configurado (veja [docs/DEPLOY.md](docs/DEPLOY.md#variáveis-de-ambiente))

### Rodar Localmente (Windows)

```bat
start.bat
```

Inicia backend (porta 8000) e frontend (porta 3000) em janelas separadas.

```bat
stop.bat
```

### Rodar Manualmente

```bash
# Backend
cd backend
uv run main.py

# Frontend
cd frontend
npm run dev
```

## Scripts Utilitários

| Script | O que faz |
|--------|-----------|
| `start.bat` | Inicia backend + frontend |
| `stop.bat` | Encerra todos os processos |
| `test.bat` | Roda diagnósticos + pytest |
| `quality.bat` | Linting, segurança e auditoria de deps |
| `scripts/validate-local.bat` | Simula build de produção localmente |

## Diagnóstico Rápido

```powershell
cd backend

# Testa busca web (Tavily + Pesquisador + Orquestrador)
$env:SKIP_PDF_LOAD="1"; uv run test_search.py

# Testa conexão com banco de dados
uv run test_db_conn.py

# Testa inicialização do RAG (PDF Knowledge)
uv run test_pdf_init.py
```

## Verificação Antes do Push

```powershell
.\scripts\verify-build.bat
```
*(Se tudo der certo no GitHub, não se esqueça de validar o Docker rodando `.\scripts\validate-local.bat` antes de puxar na Hostinger)*


## Stack Resumida

**Backend:** Python · FastAPI · Agno · OpenAI · Anthropic · Google AI · Groq · Tavily · Supabase · PgVector · FFmpeg

**Frontend:** Next.js · React · TypeScript · Tailwind CSS · Zustand · Radix UI · Framer Motion

**DevOps:** Docker · GitHub Actions · GHCR · Hostinger VPS
