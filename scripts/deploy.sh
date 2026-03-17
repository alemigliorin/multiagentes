#!/bin/bash

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Iniciando deploy do Multiagentes..."

# 0. Verificação de Variáveis de Ambiente
if [ ! -f .env ]; then
    echo "❌ Erro: Arquivo .env não encontrado na raiz do projeto!"
    echo "Crie um arquivo .env baseado no .env.example ou nas instruções do README.md"
    exit 1
fi

# Carregar variáveis para o script (apenas para validação)
export $(grep -v '^#' .env | xargs)

REQUIRED_VARS=("NEXT_PUBLIC_API_URL" "CORS_ORIGINS")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Erro: Variável de ambiente $var não está definida no .env"
        exit 1
    fi
done

echo "✅ Verificação de ambiente concluída."

# 1. Puxar as últimas alterações do repositório (opcional, para atualizar configs)
# git pull origin main

# 2. Login no GHCR (GitHub Container Registry)
# Nota: É recomendado rodar o login manualmente uma vez ou configurar via variáveis de ambiente
# echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# 3. Pull das imagens mais recentes
echo "📥 Puxando imagens do GHCR..."
docker compose -f $COMPOSE_FILE pull

# 4. Reiniciar os serviços (buildando o frontend localmente para injetar variáveis)
echo "🔄 Reiniciando containers..."
docker compose -f $COMPOSE_FILE up -d --build frontend
docker compose -f $COMPOSE_FILE up -d --remove-orphans

# 5. Limpando imagens antigas (opcional)
echo "🧹 Limpando imagens não utilizadas..."
docker image prune -f

echo "✅ Deploy finalizado com sucesso!"
