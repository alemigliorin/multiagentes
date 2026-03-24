@echo off
setlocal enabledelayedexpansion

echo #################################################
echo #  Multiagentes - Qualidade e Segurança        #
echo #################################################
echo.

set PASS=0
set FAIL=0

cd /d %~dp0backend

echo ============================================================
echo  [1/3] LINTING - Ruff
echo ============================================================
echo Verificando formatacao e estilo do codigo...
echo.
uv run ruff check . --exclude .venv
if %errorlevel% == 0 (
    echo  OK - Nenhum problema de estilo encontrado.
    set /a PASS+=1
) else (
    echo  AVISO - Problemas de estilo encontrados acima.
    set /a FAIL+=1
)
echo.

echo ============================================================
echo  [2/3] SEGURANÇA - Bandit
echo ============================================================
echo Analisando vulnerabilidades de segurança no codigo...
echo.
uv run bandit -r . -x .venv,tests/ -ll
if %errorlevel% == 0 (
    echo  OK - Nenhuma vulnerabilidade de alta/media severidade encontrada.
    set /a PASS+=1
) else (
    echo  AVISO - Possíveis vulnerabilidades encontradas acima.
    set /a FAIL+=1
)
echo.

echo ============================================================
echo  [3/3] AUDITORIA DE DEPENDÊNCIAS - pip-audit
echo ============================================================
echo Verificando CVEs conhecidos nas dependencias...
echo.
uv run pip-audit
if %errorlevel% == 0 (
    echo  OK - Nenhuma dependencia vulneravel encontrada.
    set /a PASS+=1
) else (
    echo  AVISO - Dependencias com CVEs encontradas acima. Atualize com: uv lock --upgrade
    set /a FAIL+=1
)
echo.

echo ============================================================
echo  RESULTADO FINAL
echo ============================================================
echo.
echo  Verificacoes OK:    %PASS%/3
echo  Verificacoes com aviso: %FAIL%/3
echo.
if %FAIL% == 0 (
    echo  Codigo aprovado em todas as verificacoes!
) else (
    echo  Revise os avisos antes de fazer push para main.
)
echo.
pause
