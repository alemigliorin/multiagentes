@echo off

echo Iniciando verificacao local do build Docker...

:: 1. Verifica se o Docker esta rodando
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Erro: O Docker nao parece estar rodando ou nao esta no PATH.
    echo Certifique-se de que o daemon do Docker (ou WSL) esta ativo.
    pause
    exit /b 1
)

:: 2. Muda para a raiz do projeto (um nivel acima de /scripts)
pushd "%~dp0.."

echo.
echo 1/2 Verificando build do BACKEND...
docker build ./backend -t backend-test-local --quiet
if %ERRORLEVEL% NEQ 0 (
    echo Erro no build do Backend!
    popd
    pause
    exit /b %ERRORLEVEL%
)
echo Backend buildado com sucesso!

echo.
echo 2/2 Verificando build do FRONTEND...
docker build ./frontend -t frontend-test-local --quiet
if %ERRORLEVEL% NEQ 0 (
    echo Erro no build do Frontend!
    popd
    pause
    exit /b %ERRORLEVEL%
)
echo Frontend buildado com sucesso!

:: Volta para o diretorio original
popd

echo.
echo Tudo certo! Seu projeto esta pronto para ser enviado ao GitHub.
echo Voce pode dar o git push com seguranca.
echo.

pause
