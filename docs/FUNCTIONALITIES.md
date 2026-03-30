# Funcionalidades

## Agentes Especializados

O sistema possui 6 agentes especializados coordenados por um orquestrador central. Todos são carregados sob demanda (lazy-loading).

### Orquestrador

- **Modelo:** OpenAI gpt-4o-mini (ou gpt-5-mini se disponível)
- **Responsabilidade:** Recebe a mensagem do usuário, analisa a intenção e decide quais agentes acionar. Consolida as respostas antes de retornar ao frontend. É o agente padrão do sistema.
- **Instruções:** `backend/prompts/orquestrador.md`

### Pesquisador

- **Modelo:** OpenAI gpt-4o
- **Ferramentas:** `busca_rapida`, `busca_profunda` (Tavily API)
- **Responsabilidade:** Pesquisa web em tempo real. Usado quando a resposta requer dados atualizados que não estão no conhecimento do modelo.
- **Instruções:** `backend/prompts/pesquisador.md`

### Copywriter

- **Modelo:** OpenAI gpt-4o
- **Ferramentas:** `get_creator_transcripts`, `list_available_creators`
- **Responsabilidade:** Criação de conteúdo persuasivo, copies e textos de marketing baseados no estilo de criadores de referência.
- **Instruções:** `backend/prompts/copywriter.md`

### Jurídico

- **Modelo:** OpenAI gpt-4o
- **Ferramentas:** Nenhuma
- **Responsabilidade:** Análise de compliance, revisão de termos, avaliação de riscos legais e interpretação de legislação.
- **Instruções:** `backend/prompts/juridico.md`

### Criador de Experts

- **Modelo:** OpenAI gpt-4o
- **Ferramentas:** Nenhuma
- **Responsabilidade:** Criação de personas, big ideas, estratégias de posicionamento e frameworks de conteúdo.
- **Instruções:** `backend/prompts/criador_experts.md`

### Criador de Mídia

- **Modelo:** Google Gemini 2.5-flash
- **Ferramentas:** `gerar_imagem`, `gerar_video`, `consultar_status_video`
- **Responsabilidade:** Geração de imagens e vídeos via Google Generative AI.
- **Instruções:** `backend/prompts/criador_midia.md`

### Agente PDF

- **Modelo:** OpenAI gpt-4o
- **Ferramentas:** Knowledge base PgVector (RAG)
- **Responsabilidade:** Análise e resposta a perguntas sobre documentos PDF previamente carregados.
- **Instruções:** `backend/prompts/agente_pdf.md`

---

## Endpoints da API

### Health Check

```
GET  /health
HEAD /health
```

Retorna `{"status": "ok"}`. Usado para probes de infraestrutura.

### Arquivos Estáticos (Mídia)

Arquivos gerados pelos agentes (como o Criador de Mídia) são servidos via endpoints dedicados:
- `GET /media/list` -> Lista todos os arquivos de mídia disponíveis (imagens e vídeos) com metadados
- `GET /media/download/{filename}` -> Retorna imagem do diretório `tmp/`
- `GET /videos/download/{filename}` -> Retorna vídeo do diretório `videos/`

### Endpoints da Agno (AgentOS)

O core do sistema usa o framework Agno, que expõe os endpoints de execução dos agentes.

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET`  | `/agents` | Lista os agentes disponíveis e seus metadados. |
| `POST` | `/agents/{agent_id}/runs` | Executa um agente. Resposta em SSE. |
| `GET`  | `/sessions` | Lista as sessões de chat. |
| `GET`  | `/sessions/{session_id}/runs` | Obtém o histórico de mensagens de uma sessão. |
| `DELETE` | `/sessions/{session_id}` | Remove uma sessão. |

Headers obrigatórios para estas rotas:
```
Authorization: Bearer <supabase_access_token>
Content-Type: application/json
```

### Upload de PDF

```
POST /upload-pdf
```

Parâmetros (multipart/form-data):

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `file` | arquivo | Sim | PDF a ser processado |
| `save_to_rag` | boolean | Não | Indexar no PgVector (padrão: false) |

Validações aplicadas:
- MIME type deve ser `application/pdf`
- Nome do arquivo é substituído por UUID (proteção contra path traversal)

### Upload de Vídeo

```
POST /upload-video
```

Parâmetros (multipart/form-data):

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `file` | arquivo | Sim | Arquivo de vídeo |
| `creator` | string | Sim | Nome do criador (organiza o armazenamento) |

O nome do criador é sanitizado antes de ser usado como nome de diretório.
### Gerenciamento de Sessões

As sessões são armazenadas na tabela `ai.sessions` e as aprovações de ferramentas em `ai.agno_approvals`.

**Estrutura Importante:**
- `ai.sessions.title`: Título da sessão (adicionado para compatibilidade com Agno v2.5).
- `ai.agno_approvals.run_status`: Status de execução da aprovação.

---

## Base de Conhecimento (RAG)

O sistema utiliza PgVector (extensão do PostgreSQL) para armazenar e buscar embeddings de documentos PDF.

**Fluxo de indexação:**
1. Upload via `POST /upload-pdf` com `save_to_rag=true`
2. Texto extraído com pypdf
3. Gerado embedding via OpenAI
4. Vetor armazenado no PgVector (Supabase)

**Fluxo de consulta:**
1. Pergunta do usuário enviada para o Agente PDF
2. Embedding da pergunta gerado
3. Busca por similaridade no PgVector
4. Contexto relevante injetado no prompt do agente

---

## Ferramentas de Busca Web

Duas ferramentas com profundidades diferentes, ambas via Tavily API:

| Ferramenta | Latência | Uso |
|-----------|----------|-----|
| `busca_rapida` | ~2s | Perguntas factuais simples |
| `busca_profunda` | ~8s | Pesquisa com múltiplas fontes e análise |

Se `TAVILY_API_KEY` não estiver definida, as ferramentas não são carregadas e o Pesquisador opera apenas com o conhecimento do modelo.

---

## Geração de Mídia

O Criador de Mídia usa Google Generative AI para:

- **Imagens:** Geradas sincronamente via `gerar_imagem`
- **Vídeos:** Gerados assincronamente via `gerar_video`; o status é consultado via `consultar_status_video`

O processamento de vídeo local (cortes, transcrição) usa FFmpeg via `ffmpeg-python`.

---

## Autenticação

Autenticação baseada em Supabase Auth (JWT tokens).

**Fluxo:**
1. Usuário faz login no frontend (email/senha ou OAuth)
2. Supabase retorna `access_token` JWT
3. Frontend inclui o token no header `Authorization: Bearer <token>`
4. Middleware do backend valida o token via SDK do Supabase

> **Atenção:** A validação de token está temporariamente desativada no middleware (`auth_logging.py`). Apenas o logging de origin está ativo. Reativar antes de ir para produção com dados sensíveis.

---

## Estado do Frontend

O estado global do chat é gerenciado com **Zustand** e persiste em `localStorage`.

Estrutura do estado:
- Lista de conversas (histórico)
- Conversa ativa
- Mensagens da conversa atual
- Estado de carregamento (streaming ativo)

O componente `ChatArea` consome o estado via hooks do Zustand e renderiza mensagens em Markdown usando `react-markdown`.
