@echo off
echo Encerrando servidores Multiagentes (Backend e Frontend)...

echo.
echo [1/3] Fechando janelas dos terminais...
taskkill /F /T /FI "WINDOWTITLE eq Backend API*" >nul 2>&1
taskkill /F /T /FI "WINDOWTITLE eq Agent UI*" >nul 2>&1

echo.
echo [2/3] Liberando porta 8000 (Backend - Python/Uvicorn)...
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [3/3] Liberando porta 3000 (Frontend - Node)...
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Servidores encerrados com sucesso!
pause
