# Instruções para Agentes de IA — Multiagentes

Este arquivo contém regras obrigatórias para qualquer agente de IA que atue neste projeto. Leia antes de fazer qualquer alteração.

---

## Regra Principal

**Toda alteração de código que impacte comportamento, estrutura ou configuração deve ser acompanhada da atualização da documentação correspondente.**

Não finalize uma tarefa sem verificar se a documentação está consistente com o que foi alterado.

---

## Mapa: Código → Documentação

Use esta tabela para saber qual documento atualizar para cada tipo de mudança:

| Você alterou... | Atualize... |
|----------------|-------------|
| `agents/` — novos agentes, ferramentas, modelos, delegações | `docs/ARCHITECTURE.md` (seção Agentes) e `docs/FUNCTIONALITIES.md` (seção Agentes) |
| `routers/` — novos endpoints ou mudança de contrato | `docs/FUNCTIONALITIES.md` (seção Endpoints) |
| `config/settings.py` — novas variáveis ou defaults | `docs/DEPLOY.md` (seção Variáveis de Ambiente) |
| `middleware/` — comportamento de auth, CORS, headers | `docs/ARCHITECTURE.md` (seção Middlewares) e `docs/FUNCTIONALITIES.md` (seção Autenticação) |
| `knowledge/` — RAG, busca, indexação | `docs/FUNCTIONALITIES.md` (seções RAG e Busca Web) |
| `docker-compose*.yml` — novos serviços ou portas | `docs/DEPLOY.md` e `README.md` (tabela de portas) |
| `.github/workflows/` — mudanças no CI/CD | `docs/DEPLOY.md` (seção CI/CD) e `docs/TESTING.md` (seção CI/CD) |
| `tests/` — novos testes ou mudança de estratégia | `docs/TESTING.md` (tabela de cobertura) |
| `start.bat`, `stop.bat`, novos scripts `.bat` | `README.md` (tabela de scripts) e `docs/DEPLOY.md` |
| Qualquer mudança que afete o fluxo geral | `docs/ARCHITECTURE.md` (seção Fluxo de uma Requisição) |

---

## Documentos e o que cada um cobre

| Arquivo | Conteúdo |
|---------|---------|
| `README.md` | Índice, início rápido, tabela de scripts |
| `docs/ARCHITECTURE.md` | Diagrama do sistema, estrutura de diretórios, decisões de design |
| `docs/FUNCTIONALITIES.md` | Agentes, endpoints, RAG, autenticação, estado do frontend |
| `docs/TESTING.md` | Scripts de diagnóstico, testes pytest, cobertura, qualidade |
| `docs/DEPLOY.md` | Variáveis de ambiente, CI/CD, deploy VPS, troubleshooting |

---

## Regras de Consistência

### Agentes

Ao adicionar ou remover um agente:
- Atualize a tabela de agentes em `docs/FUNCTIONALITIES.md`
- Atualize o diagrama ASCII em `docs/ARCHITECTURE.md`
- Se houver novo arquivo de prompt em `backend/prompts/`, documente-o

### Endpoints

Ao adicionar, remover ou alterar um endpoint:
- Documente o path, método HTTP, parâmetros e resposta esperada em `docs/FUNCTIONALITIES.md`
- Se o endpoint for público, verifique se o CORS está configurado corretamente

### Variáveis de Ambiente

Ao adicionar uma nova variável em `config/settings.py`:
- Adicione-a na tabela de variáveis em `docs/DEPLOY.md`
- Indique se é obrigatória ou opcional e qual o valor padrão

### Scripts `.bat`

Ao criar um novo script `.bat` na raiz:
- Adicione-o à tabela de scripts em `README.md`
- Siga o mesmo padrão dos existentes: header com nome, etapas numeradas `[N/N]`, `pause` ao final

### Testes

Ao criar novos testes:
- Atualize a tabela de cobertura em `docs/TESTING.md`
- Marque como "implementado" os itens da tabela "Próximos testes a implementar"

---

## O que NÃO documentar

- Código interno de funções auxiliares sem impacto externo
- Mudanças de formatação/linting sem alteração de comportamento
- Mensagens de log internas
- Arquivos `.venv/`, `node_modules/`, `__pycache__/`

---

## Antes de Finalizar uma Tarefa

Responda mentalmente:

1. O comportamento visível do sistema mudou? → Atualizar `FUNCTIONALITIES.md`
2. A estrutura ou arquitetura mudou? → Atualizar `ARCHITECTURE.md`
3. A configuração de ambiente ou deploy mudou? → Atualizar `DEPLOY.md`
4. Novos testes foram criados ou removidos? → Atualizar `TESTING.md`
5. O `README.md` continua sendo um índice preciso? → Verificar links e tabelas

Se a resposta for "não" para todas, a documentação está OK.
