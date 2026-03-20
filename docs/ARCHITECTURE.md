# Arquitetura do Sistema

## Visão Macro

O Multiagentes é uma plataforma baseada em orquestração de agentes de IA. Um agente orquestrador central recebe as requisições do usuário e delega tarefas para agentes especializados, cada um com ferramentas e modelos de LLM próprios.

```
┌────────────────────────────────────────────────┐
│                   FRONTEND                     │
│              Next.js (:3000)                   │
└────────────────────────────────────────────────┘
                        │ HTTP / SSE
                        ▼
┌────────────────────────────────────────────────┐
│              GATEWAY HTTP (FastAPI)            │
│  CORSMiddleware · Auth Middleware · Routers    │
└────────────────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────┐
│           ORQUESTRADOR (gpt-4o-mini)           │
│    Analisa a intenção e delega para agentes    │
└────────────────────────────────────────────────┘
        │         │        │        │        │
        ▼         ▼        ▼        ▼        ▼
┌──────────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌────────────┐
│Pesquisa- │ │Copy-   │ │Jurí- │ │Cria- │ │  Criador   │
│  dor     │ │writer  │ │dico  │ │ dor  │ │  de Mídia  │
│(gpt-4o)  │ │(gpt-4o)│ │(gpt- │ │Exper │ │  (Gemini   │
│          │ │        │ │ 4o)  │ │  ts  │ │  2.5-flash)│
└──────────┘ └────────┘ └──────┘ └──────┘ └────────────┘
      │                                           │
      ▼                                           ▼
┌──────────┐                             ┌────────────────┐
│  Tavily  │                             │ Google Gen AI  │
│  Search  │                             │ (img/vídeo)    │
└──────────┘                             └────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────┐
│              DADOS & CONHECIMENTO              │
│  Supabase (Auth, Sessões) · PgVector (PDFs)   │
│  Uploads locais (vídeos)                      │
└────────────────────────────────────────────────┘
```

## Estrutura de Diretórios

```
multiagentes/
├── backend/
│   ├── agents/            # Lógica de agentes
│   │   ├── factory.py     # Registry de modelos LLM
│   │   ├── delegation.py  # Função _delegate() padronizada
│   │   ├── orchestrator.py# Agente orquestrador
│   │   └── specialists.py # Agentes especialistas (lazy-loaded)
│   ├── config/
│   │   ├── settings.py    # Pydantic BaseSettings
│   │   └── cors.py        # Parsing de CORS origins
│   ├── knowledge/
│   │   ├── pdf_knowledge.py # RAG com PgVector
│   │   └── tavily.py        # Singletons de busca web
│   ├── middleware/
│   │   ├── auth_logging.py  # Logging e autenticação
│   │   └── proxy_headers.py # Anti-buffering para SSE
│   ├── routers/
│   │   ├── health.py      # GET /health
│   │   └── uploads.py     # POST /upload-pdf, /upload-video
│   ├── prompts/           # Instruções dos agentes (.md)
│   ├── main.py            # Ponto de entrada FastAPI (43 linhas)
│   └── agent.py           # Código legado (em processo de migração)
├── frontend/              # Next.js (App Router)
│   ├── src/app/           # Páginas (chat, login)
│   ├── src/components/    # ChatArea, Sidebar, UI primitivos
│   ├── src/store.ts       # Zustand (estado global)
│   └── src/api/           # Funções de chamada à API
├── docker-compose.yml         # Desenvolvimento local
├── docker-compose.prod.yml    # Produção (imagens GHCR)
├── .github/workflows/         # CI/CD GitHub Actions
├── start.bat / stop.bat       # Scripts Windows
└── scripts/                   # Automação (verify-build, deploy)
```

## Camadas e Responsabilidades

### Config (`config/`)

Centraliza toda configuração via Pydantic `BaseSettings`. Valores são lidos de variáveis de ambiente com validação de tipo em tempo de boot. `cors.py` faz o parsing seguro da string `CORS_ORIGINS`.

### Agentes (`agents/`)

- **`factory.py`**: Registry pattern — mapeia string de provider (`"openai"`, `"anthropic"`, `"google"`, `"groq"`, `"deepseek"`) para a classe de modelo correta. Extensível sem modificar os agentes.
- **`delegation.py`**: Função `_delegate()` padronizada que todos os agentes especializados usam para chamar o sub-agente correto.
- **`specialists.py`**: Agentes são instanciados **sob demanda** (lazy-loading), evitando timeout no boot e reduzindo uso de memória.
- **`orchestrator.py`**: Agente central que recebe a requisição e decide o roteamento.

### Conhecimento (`knowledge/`)

- **`pdf_knowledge.py`**: Integração com PgVector para RAG. Inicialização lazy para não bloquear o boot caso o banco não esteja disponível.
- **`tavily.py`**: Singletons das ferramentas de busca (`busca_rapida`, `busca_profunda`). Opcionais — se `TAVILY_API_KEY` não estiver configurada, as ferramentas não são carregadas.

### Middlewares (`middleware/`)

- **`proxy_headers.py`**: Injeta `X-Accel-Buffering: no` e outros headers para garantir que o SSE (Server-Sent Events) flua sem buffering pelo proxy reverso (Nginx).
- **`auth_logging.py`**: Loga a origin de cada requisição e valida o Bearer token via Supabase.
- **`CORSMiddleware`**: (Integrado no `main.py`) Gerencia preflight requests (OPTIONS) e libera o acesso para as origins configuradas em `CORS_ORIGINS`.

### Routers (`routers/`)

- **`health.py`**: `GET /health` retorna `{"status": "ok"}`. Suporta `HEAD` e `OPTIONS` para probes de infraestrutura.
- **`uploads.py`**: Upload seguro de PDFs (com opção de indexar no RAG) e vídeos (organizados por criador).

### Frontend (`frontend/`)

- **App Router** (Next.js 13+): páginas em `src/app/`
- **Zustand** (`store.ts`): estado global do chat com persistência em `localStorage`
- **Supabase SSR**: autenticação server-side com cookies

## Fluxo de uma Requisição

```
1. Usuário digita mensagem no chat (Next.js)
2. Frontend POST /agents/{agent_id}/runs com Bearer token
3. FastAPI → CORSMiddleware → auth_logging middleware
4. Router delega para o orquestrador (via Agno)
5. Orquestrador analisa a mensagem e chama _delegate() para o(s) agente(s) correto(s)
6. Agente especialista executa ferramentas (Tavily, Google AI, PgVector...)
7. Resposta gerada em streaming via SSE
8. Frontend exibe tokens em tempo real no ChatArea
```

## Providers de LLM Suportados

| Provider | Variável de Ambiente | Uso Principal |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | Orquestrador, maioria dos agentes |
| Google | `GOOGLE_API_KEY` | Criador de Mídia (Gemini 2.5-flash) |
| Anthropic | `ANTHROPIC_API_KEY` | Disponível via factory |
| Groq | `GROQ_API_KEY` | Disponível via factory |
| DeepSeek | `DEEPSEEK_API_KEY` | Disponível via factory |

## Decisões de Design

**Por que Agno em vez de LangChain?**
Agno oferece API mais simples para multi-agentes com delegação nativa, lazy-loading de agentes e suporte a streaming SSE sem adaptadores.

**Por que lazy-loading nos agentes?**
Cada agente especialista pode demorar para inicializar (carregar ferramentas, conectar ao banco). O lazy-loading garante boot em menos de 5 segundos mesmo com banco fora do ar.

**Por que registry pattern em `factory.py`?**
Desacopla a lógica de criação do modelo do código dos agentes. Adicionar um novo provider exige apenas uma linha no dicionário do registry.

**Por que SSE em vez de WebSocket?**
SSE é mais simples de implementar com proxies reversos (Nginx), não requer handshake bidirecional e funciona perfeitamente para o caso de uso de streaming de respostas de LLM.
