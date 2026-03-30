@echo off
echo #################################################
echo #  Encerrando Multiagentes (Cleanup Total)      #
echo #################################################
echo.

echo [1/4] Fechando janelas dos terminais...
taskkill /F /T /FI "WINDOWTITLE eq Backend API*" >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq Agent UI*" >nul 2>&1

echo [2/4] Matando processos Python/Uvicorn na porta 8000...
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr "LISTENING" ^| findstr ":8000 "') do (
    echo   Encerrando PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo [3/4] Matando processos Node/Next.js na porta 3000...
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr "LISTENING" ^| findstr ":3000 "') do (
    echo   Encerrando PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo [4/4] Aguardando liberacao das portas...
timeout /t 2 /nobreak >nul

echo.
echo Todos os servidores foram encerrados com sucesso!
echo.
pause
