@echo off
echo Executando suite de testes automatizados do Backend...
uv run pytest tests/ -v --tb=short --cov=. --cov-report=term-missing
pause
