# Guia de Deploy - Multiagentes

Este guia resume o processo de atualização e deploy da aplicação na Hostinger VPS.

## 🚀 Fluxo de Trabalho (Workflow)

Para garantir que as variáveis do frontend (Supabase) sejam injetadas corretamente no código do navegador, siga este fluxo:

1.  **Localmente:** Realize suas alterações e faça o push:
    ```bash
    git push origin main
    ```
2.  **GitHub Actions:** Aguarde a finalização do build da imagem (ícone verde no GitHub).
    - *Nota: As chaves do Supabase e a API URL estão configuradas nas 'Repository Secrets'.*
3.  **Na Hostinger:** Execute os comandos de atualização:
    ```bash
    cd ~/multiagentes
    git pull origin main
    docker compose -f docker-compose.prod.yml pull frontend
    docker compose -f docker-compose.prod.yml up -d --force-recreate frontend
    ```

## 🛠️ Solução de Problemas (Troubleshooting)

### "URL and Key are required" (Supabase Error)
Este erro ocorre se o Next.js foi compilado sem as variáveis de ambiente.
- **Causa:** Imagem do GitHub sem secrets ou cache de imagem antiga.
- **Solução Rápida (Build Local na VPS):**
    ```bash
    docker compose -f docker-compose.prod.yml build --no-cache frontend
    docker compose -f docker-compose.prod.yml up -d frontend
    ```

### Verificar Variáveis no Container
Para checar se o container está recebendo as variáveis corretamente:
```bash
docker exec -it multiagentes-frontend-1 env | grep SUPABASE
```

## 📄 Arquivos de Configuração
- **Raiz (`.env`):** Usado pelo Docker Compose para o processo de build.
- **Frontend (`.env.production`):** Usado para variáveis de runtime no servidor.
- **Backend (`.env`):** Configurações específicas da API e chaves de IA.
