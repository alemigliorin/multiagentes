# Instruções para Claude Code — Multiagentes

Leia `AGENTS.md` antes de qualquer tarefa. Ele contém as regras universais do projeto, incluindo o mapa obrigatório de código → documentação.

---

## Comportamento Esperado

- Sempre leia os arquivos relevantes antes de propor ou executar mudanças
- Prefira editar arquivos existentes a criar novos
- Não adicione comentários, docstrings ou type annotations em código que você não alterou
- Não adicione tratamento de erro para cenários impossíveis — confie nos contratos internos
- Respostas curtas e diretas; sem resumo do que foi feito ao final

## Testes

- Antes de criar um teste, leia o arquivo que será testado
- Mocks devem refletir o comportamento real — não invente retornos arbitrários
- Scripts de diagnóstico (`test_*.py` na raiz de `backend/`) requerem `.env` com chaves reais

## Ferramentas Preferidas

- Busca de arquivos → `Glob` (não `find`)
- Busca de conteúdo → `Grep` (não `grep` via Bash)
- Leitura → `Read` (não `cat`)
- Edição → `Edit` para mudanças parciais, `Write` apenas para arquivos novos ou reescrita completa

## Ambiente

- Shell: bash (sintaxe Unix, mesmo no Windows)
- Gerenciador Python: `uv` (não `pip` diretamente)
- Testes Python: `uv run pytest` a partir de `backend/`
- Frontend: `npm` a partir de `frontend/`
