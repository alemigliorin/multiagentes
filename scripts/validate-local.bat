@echo off
echo =======================================================
echo VALIDACAO DE DEPLOY LOCAL (SIMULANDO HOSTINGER)
echo =======================================================
echo.
echo Este script usa o arquivo docker-compose.prod.yml para 
echo buildar as imagens localmente e confirmar que estao prontas
echo para ir para a producao.
echo.

if not exist .env (
    echo [ERRO] Arquivo .env nao encontrado na raiz.
    echo Certifique-se de configurar suas variaveis.
    pause
    exit /b 1
)

echo [1/3] Limpando eventuais sessoes anteriores do compose de producao...
docker compose -f docker-compose.prod.yml down

echo.
echo [2/3] Buildando as imagens de producao...
docker compose -f docker-compose.prod.yml build
if errorlevel 1 (
    echo [ERRO] Falha no build! Corrija os erros e tente novamente.
    pause
    exit /b 1
)

echo.
echo [3/3] Subindo os containers temporariamente...
docker compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo [ERRO] Falha ao subir os containers.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo [SUCESSO] Validacao concluida!
echo =======================================================
echo As imagens buildaram e rodaram com sucesso. Pressione 
echo qualquer tecla para derrubar os containers de teste
echo para que voce possa voltar ao ambiente de dev.
echo.
echo Apos encerrar, voce pode fazer commit/push do seu codigo
echo e rodar o script deploy.sh na VPS.
echo.
pause >nul

docker compose -f docker-compose.prod.yml down
echo.
echo Containers de validacao removidos. Finalizado.
pause
