@echo off
echo #################################################
echo #  Encerrando Multiagentes (Cleanup Total)      #
echo #################################################
echo.

echo [1/3] Fechando janelas dos terminais...
taskkill /F /T /FI "WINDOWTITLE eq Backend API*" >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq Agent UI*" >nul 2>&1

echo [2/3] Liberando porta 8000 (Backend - Python/Uvicorn)...
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [3/3] Liberando porta 3000 (Frontend - Next.js)...
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Todos os servidores foram encerrados com sucesso!
echo.
pause
