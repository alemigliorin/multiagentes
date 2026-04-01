# Deploy

## Ambientes

| Ambiente | Arquivo | Imagens |
|----------|---------|---------|
| Desenvolvimento | `docker-compose.yml` | Buildadas localmente com `--reload` |
| Produção | `docker-compose.prod.yml` | Buildadas localmente na Hostinger via código fonte |

---

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (ou em `backend/.env`). O `start.bat` copia automaticamente da raiz para `backend/` se necessário.

### Backend

```env
# Provedores de LLM (ao menos OPENAI_API_KEY é obrigatória)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...
DEEPSEEK_API_KEY=...
TAVILY_API_KEY=tvly-...

# Timeouts da API Tavily (em segundos, fallback DuckDuckGo)
TAVILY_TIMEOUT_RAPIDA=10
TAVILY_TIMEOUT_PROFUNDA=20

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_DB_URL=postgresql://postgres:senha@db.xxxxx.supabase.co:5432/postgres

# App
CORS_ORIGINS=http://localhost:3000,https://multiagentes.migliorinlabs.cloud
SKIP_PDF_LOAD=0   # Defina 1 para pular o RAG (útil em testes)
```

### 4. Supabase Storage (Mídia)

O backend agora armazena imagens e vídeos gerados diretamente no Supabase Storage:
1. No painel do Supabase, vá em **Storage** > **New Bucket**
2. Nomeie o bucket como **`media`**
3. Marque a opção **Public bucket** para que as imagens sejam acessíveis sem autenticação

### 5. Setup do Frontend (injetado em build time)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
NEXT_PUBLIC_OS_SECURITY_KEY=...   # Opcional
```

> Em produção, as variáveis tanto do frontend quanto do backend devem ficar centralizadas no arquivo `.env` (ou outro método de injeção direto de envs) na raiz do servidor, já que o build ocorre localmente na Hostinger.

> **⚠️ CRÍTICO — `.env` da VPS deve conter `SUPABASE_DB_URL`!**  
> Sem essa variável no `.env` do servidor, o backend não inicializa o banco PostgreSQL, resultando em **histórico de chats desativado** e **RAG global (PDF) quebrado**. O `docker-compose.prod.yml` passa essa variável explicitamente para o container backend.

---

## Desenvolvimento Local (Windows)

```bat
:: Inicia backend (8000) e frontend (3000)
start.bat

:: Encerra tudo
stop.bat
```

O `start.bat`:
1. Verifica a existência do `.env` (copia da raiz para `backend/` se necessário)
2. Abre Backend API em janela `cmd` separada via `uv run main.py`
3. Abre Frontend em janela `cmd` separada via `npm run dev`

### Portas

| Serviço | Porta |
|---------|-------|
| Backend (FastAPI) | 8000 |
| Frontend (Next.js) | 3000 |

---

## CI/CD — GitHub Actions

Fluxo automático em todo push para `main`:

```text
Push para main
    ↓
GitHub Actions
    ├── Linting (ruff, eslint)
    ├── Segurança (bandit, audit)
    └── Testes (pytest)
```

Neste modelo simplificado, as imagens Docker não são enviadas para um Registry externo. Em vez disso, a própria VPS da Hostinger faz o pull do novo código e builda as imagens localmente. 

As variáveis do frontend (`NEXT_PUBLIC_*`) não precisam mais ser cadastradas como secrets no GitHub, elas são injetadas diretamente durante o build local na VPS usando o arquivo `.env`.

---

## Produção (Hostinger VPS)

### Pré-requisitos

```bash
# Docker e Docker Compose instalados
docker --version
docker compose version

# Rede nginx-proxy (se usar Nginx Proxy Manager)
docker network create nginx-proxy
```

### Novo Servidor (Deploy Inicial)

```bash
git clone https://github.com/alemigliorin/multiagentes.git
cd multiagentes

# Criar .env com as variáveis de backend e frontend
cp .env.example .env
nano .env  # Preencher as chaves

chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Atualizar após novo código (Push para main)

Acesse a VPS na pasta do projeto e rode:

```bash
./scripts/deploy.sh
```

O script automaticamente fará o `git pull` com o código mais recente, realizará o build local das imagens de produção (`docker compose ... --build`) e reiniciará os containers necessários.

### Recriar Ambiente do Zero (Hard Reset)

Se o build continuar utilizando cache antigo e as alterações não refletirem em produção, force uma recriação limpa:

1. Acesse a pasta do projeto:
   ```bash
   cd ~/multiagentes
   ```
2. Derrube todos os containers e apague as redes/volumes locais:
   ```bash
   docker compose -f docker-compose.prod.yml down -v
   ```
3. Garanta que seu código local é idêntico ao remoto (destrói modificações locais não commitadas):
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```
4. Recrie a rede externa (se necessário):
   ```bash
   docker network create nginx-proxy || true
   ```
5. Rebuilde as imagens forçando a não utilizar nenhum cache anterior (pode demorar):
   ```bash
   docker compose -f docker-compose.prod.yml build --no-cache
   ```
6. Suba a aplicação recriada:
   ```bash
   ./scripts/deploy.sh
   ```
---

## Verificação Pré-push

Simula o build do GitHub Actions localmente antes de fazer push:

```powershell
.\scripts\verify-build.bat
```

---

## Troubleshooting

### "URL and Key are required" (Supabase)

O Next.js foi compilado sem as variáveis de ambiente.

**Causa:** Secrets não configurados no GitHub Actions ou cache de imagem antiga.

**Solução — rebuild sem cache na VPS:**
```bash
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

**Verificar variáveis no container:**
```bash
docker exec -it multiagentes-frontend-1 env | grep SUPABASE
docker exec -it multiagentes-backend-1 env | grep SUPABASE
```

### Histórico de chats não retorna / RAG PDF "Base de conhecimento não inicializada"

**Causa:** `SUPABASE_DB_URL` ausente no `.env` da VPS. O backend não consegue conectar ao PostgreSQL.

**Diagnóstico:**
```bash
# Deve imprimir a URL do banco
docker exec -it multiagentes-backend-1 printenv SUPABASE_DB_URL
```

**Solução:** Adicionar ao `.env` da VPS (na raiz do projeto):
```env
SUPABASE_DB_URL=postgresql://postgres.PROJECT_REF:SENHA@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```
Depois reiniciar o container:
```bash
docker compose -f docker-compose.prod.yml up -d backend
```

### "Invalid Refresh Token: Refresh Token Not Found" (Frontend SSR)

**Causa:** O middleware do Next.js (`src/middleware.ts`) não existia — estava nomeado incorretamente como `src/proxy.ts`. Sem o middleware, a sessão do Supabase jamais era renovada pelo servidor.

**Verificação:** O arquivo `src/middleware.ts` deve existir e exportar a função `middleware` (não `proxy`). Este arquivo foi corrigido no código — basta fazer deploy.

### Backend não inicia

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs backend --tail=50

# Verificar variáveis
docker exec -it multiagentes-backend-1 env | grep OPENAI
```

### Health check falha

```bash
curl https://api.migliorinlabs.cloud/health
# Deve retornar: {"status": "ok"}
```

### Aviso: "Missing columns {'run_status'} in table ai.agno_approvals"

**Causa:** Inconsistência de schema após atualização da biblioteca Agno.

**Solução:** Executar as seguintes queries no SQL Editor do Supabase:
```sql
ALTER TABLE ai.sessions ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE ai.agno_approvals ADD COLUMN IF NOT EXISTS run_status TEXT;
```

---

## Arquivos de Configuração Docker

| Arquivo | Uso |
|---------|-----|
| `docker-compose.yml` | Desenvolvimento local (build local, reload) |
| `docker-compose.prod.yml` | Produção (Build source via Docker, restart: unless-stopped) |
| `frontend/Dockerfile` | Multi-stage build do Next.js |
| `backend/Dockerfile` | Build do FastAPI com uv |
| `.github/workflows/` | Pipelines de CI/CD |
