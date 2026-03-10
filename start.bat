@echo off
echo Iniciando multiagentes backend e Streamlit frontend...
echo Pressione CTRL+C para fechar os servidores.

start "Backend API" cmd /k "cd /d %~dp0backend && uv run python main.py"
start "Streamlit UI" cmd /k "cd /d %~dp0frontend-streamlit && uv run streamlit run app.py"
