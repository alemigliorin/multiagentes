# AI Multi-Agentes Projeto

Este projeto consiste em um ecossistema de múltiplos agentes de IA com Backend em Python (FastAPI/Agno) e Frontends em Next.js e Streamlit.

## 🚀 Como Rodar Localmente

Consulte as instruções nos diretórios `backend/`, `frontend/` e `frontend-streamlit/`.

---

## 🛡️ Verificação Local (Antes do Push)

Para garantir que o build não quebrará no GitHub Actions nem na produção, recomendamos rodar o script de verificação local. Ele simula o build que será feito na nuvem:

```powershell
.\scripts\verify-build.bat
```

Se este script terminar com sucesso, você pode fazer o `git push` com a certeza de que a imagem será gerada corretamente.

---

## 🏗️ Deployment (Hostinger / VPS)

Para evitar erros de compilação no servidor, utilizamos imagens pré-compiladas hospedadas no **GitHub Container Registry (GHCR)**.

### 1. Requisitos Prévios
- Docker e Docker Compose instalados na VPS.
- Um **Personal Access Token (PAT)** do GitHub com permissão `read:packages`.
- Uma rede Docker externa chamada `nginx-proxy` (comum em setups com Nginx Manager):
  ```bash
  docker network create nginx-proxy
  ```

### 2. Login no GitHub Container Registry
No seu servidor, execute o login para permitir que o Docker baixe as imagens privadas:
```bash
echo "SEU_GITHUB_TOKEN" | docker login ghcr.io -u SEU_USUARIO_GITHUB --password-stdin
```

### 3. Realizando o Deploy
Subimos o projeto usando o arquivo de produção que aponta para as imagens do GHCR:

```bash
# Clone o repositório (apenas para pegar os arquivos de config)
git clone https://github.com/alemigliorin/multiagentes.git
cd multiagentes

# Execute o script de deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 4. Atualizando o Projeto
Sempre que você fizer um `push` para a branch `main`, o GitHub Actions irá buildar as novas imagens. Para atualizar o servidor, basta rodar o script de deploy novamente:
```bash
./scripts/deploy.sh
```

---

## 🛠️ Tecnologias
- **Backend**: Python, FastAPI, Agno, OpenAI/Google AI.
- **Frontend**: Next.js, React, Tailwind CSS.
- **Streamlit**: Para monitoramento e prototipagem rápida.
- **DevOps**: Docker, GitHub Actions, GHCR.
