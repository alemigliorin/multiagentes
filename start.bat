@echo off
setlocal enabledelayedexpansion

echo #################################################
echo #  Iniciando Multiagentes (Backend + Frontend)  #
echo #################################################
echo.

:: 0. Parar instancias anteriores (evita duplicatas)
echo [0/3] Encerrando instancias anteriores...
taskkill /F /T /FI "WINDOWTITLE eq Backend API*" >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq Agent UI*" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr "LISTENING" ^| findstr ":8000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr "LISTENING" ^| findstr ":3000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: 1. Verificacao de Arquivo .env
if not exist "%~dp0backend\.env" (
    if exist "%~dp0.env" (
        echo [INFO] Copiando .env da raiz para a pasta backend...
        copy "%~dp0.env" "%~dp0backend\.env" >nul
    ) else (
        echo [ERRO] Arquivo .env nao encontrado em \backend nem na raiz!
        echo Crie um arquivo .env baseado no .env.example para continuar.
        pause
        exit /b 1
    )
)

echo [1/3] Instancias anteriores encerradas.
echo [2/3] Iniciando Backend API (Porta 8000)...
start "Backend API" cmd /k "cd /d %~dp0backend && uv run main.py"

echo [3/3] Iniciando Agent UI (Next.js - Porta 3000)...
start "Agent UI (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Servidores em processo de inicializacao!
echo Pressione CTRL+C nas janelas especificas para encerrar.
echo Use stop.bat para fechar tudo de uma vez.
echo.
pause
