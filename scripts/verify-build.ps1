# PowerShell script for Docker verification with WSL fallback
# This version handles path translation correctly for WSL.

Write-Host "Iniciando verificacao local do build Docker..."

# 1. Detect Docker environment
$dockerCmd = ""
$isWsl = $false

if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker ps > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerCmd = "docker"
        Write-Host "Docker nativo detectado"
    }
}

if ($dockerCmd -eq "") {
    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        wsl docker ps > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $dockerCmd = "wsl docker"
            $isWsl = $true
            Write-Host "Docker detectado via WSL"
        }
    }
}

if ($dockerCmd -eq "") {
    Write-Host "Erro: Docker nao encontrado nativamente nem via WSL"
    exit 1
}

# 2. Get Project Root
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\.."
$root = (Get-Location).Path.Replace('\', '/')
Write-Host "Raiz do projeto: $root"

# 3. Build Backend
Write-Host ""
Write-Host "1/2 Verificando build do BACKEND..."
if ($isWsl) {
    $linuxPath = wsl wslpath -u "$root/backend"
    Write-Host "Caminho Linux: $linuxPath"
    wsl docker build "$linuxPath" -t backend-test-local --quiet
} else {
    docker build ./backend -t backend-test-local --quiet
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no build do Backend!"
    exit 1
}
Write-Host "Backend OK!"

# 4. Build Frontend
Write-Host ""
Write-Host "2/2 Verificando build do FRONTEND..."
if ($isWsl) {
    $linuxPath = wsl wslpath -u "$root/frontend"
    Write-Host "Caminho Linux: $linuxPath"
    wsl docker build "$linuxPath" -t frontend-test-local --quiet
} else {
    docker build ./frontend -t frontend-test-local --quiet
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no build do Frontend!"
    exit 1
}
Write-Host "Frontend OK!"

Write-Host ""
Write-Host "Tudo certo! Seu projeto esta pronto para ser enviado ao GitHub."
Write-Host ""
