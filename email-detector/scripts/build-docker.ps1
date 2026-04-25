# Build and Run Email Security Detector (Single Container)

Write-Host "Building Email Security Detector (Single Container)..." -ForegroundColor Cyan

# Change to project root
Set-Location -Path "$PSScriptRoot\.."

# Build the Docker image
docker build -f Dockerfile -t email-detector:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run the container, use:" -ForegroundColor Yellow
    Write-Host "  .\run-docker.ps1" -ForegroundColor White
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
