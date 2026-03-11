@echo off
echo Iniciando multiagentes backend e Next.js frontend...
echo Pressione CTRL+C para fechar os servidores.

start "Backend API" cmd /k "cd /d %~dp0backend && uv run python main.py"
start "Agent UI" cmd /k "cd /d %~dp0frontend && npm run dev"
