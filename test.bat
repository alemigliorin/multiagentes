@echo off
setlocal enabledelayedexpansion

echo #################################################
echo #  Multiagentes - Suite de Testes              #
echo #################################################
echo.

:: 1. Verificação de Arquivo .env
if not exist "%~dp0backend\.env" (
    if exist "%~dp0.env" (
        echo [INFO] Copiando .env da raiz para a pasta backend...
        copy "%~dp0.env" "%~dp0backend\.env" >nul
    ) else (
        echo [AVISO] Arquivo .env nao encontrado. Alguns testes de diagnostico podem falhar.
        echo         Crie um arquivo .env baseado no .env.example para testes completos.
        echo.
    )
)

set PASS=0
set FAIL=0

echo ============================================================
echo  DIAGNOSTICOS DE INTEGRACAO (requerem variaveis de ambiente)
echo ============================================================
echo.

echo [1/4] Testando conexao com o banco de dados...
cd /d %~dp0backend
uv run test_db_conn.py
if %errorlevel% == 0 ( set /a PASS+=1 ) else ( set /a FAIL+=1 )
echo.

echo [2/4] Testando inicializacao do RAG (PgVector)...
set SKIP_PDF_LOAD=0
uv run test_pdf_init.py
if %errorlevel% == 0 ( set /a PASS+=1 ) else ( set /a FAIL+=1 )
echo.

echo [3/4] Testando busca web (Tavily + Pesquisador)...
set SKIP_PDF_LOAD=1
uv run test_search.py
if %errorlevel% == 0 ( set /a PASS+=1 ) else ( set /a FAIL+=1 )
echo.

echo [4/4] Testando orquestrador...
set SKIP_PDF_LOAD=1
uv run test_orq.py
if %errorlevel% == 0 ( set /a PASS+=1 ) else ( set /a FAIL+=1 )
echo.

echo ============================================================
echo  TESTES AUTOMATIZADOS (pytest)
echo ============================================================
echo.

echo Rodando suite pytest (unit + integration)...
uv run pytest --tb=short -v
if %errorlevel% == 0 ( set /a PASS+=1 ) else ( set /a FAIL+=1 )
echo.

echo ============================================================
echo  RESULTADO FINAL
echo ============================================================
echo.
echo  Etapas OK:     %PASS%
echo  Etapas com erro: %FAIL%
echo.
if %FAIL% == 0 (
    echo  Todos os testes passaram com sucesso!
) else (
    echo  Atencao: %FAIL% etapa(s) apresentaram erros. Verifique os logs acima.
)
echo.
pause
