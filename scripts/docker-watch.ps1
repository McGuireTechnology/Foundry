param(
    [switch]$NoWatch
)

$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Docker Desktop does not appear to be running." -ForegroundColor Red
    Write-Host "Start Docker Desktop, wait until the engine is ready, then retry." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting check:" -ForegroundColor Cyan
    Write-Host "  docker info"
    Write-Host ""
    Write-Host "Raw Docker error:"
    Write-Host $dockerInfo
    exit 1
}

if ($NoWatch) {
    docker compose up --build
    exit $LASTEXITCODE
}

docker compose watch
exit $LASTEXITCODE
