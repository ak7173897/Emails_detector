# Run Email Security Detector (Single Container)

Write-Host "Starting Email Security Detector..." -ForegroundColor Cyan

# Change to project root
Set-Location -Path "$PSScriptRoot\.."

# Build image if missing
$imageExists = docker image inspect email-detector:latest 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Docker image not found. Building image first..." -ForegroundColor Yellow
  docker build -f Dockerfile -t email-detector:latest .
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Image build failed!" -ForegroundColor Red
    exit 1
  }
}

# Stop and remove any existing container
docker stop email-detector 2>$null
docker rm email-detector 2>$null

# Run the container
docker run -d `
  --name email-detector `
  -p 5000:5000 `
  -e FLASK_ENV=production `
  -e SECRET_KEY="$(([char[]](48..57 + 65..90 + 97..122) | Get-Random -Count 32) -join '')" `
  -e CONFIDENCE_THRESHOLD=70.0 `
  -e MAX_EMAIL_LENGTH=50000 `
  -e LOG_LEVEL=INFO `
  --restart unless-stopped `
  email-detector:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Container started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the application at: http://localhost:5000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Cyan
    Write-Host "  docker logs -f email-detector" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop the container:" -ForegroundColor Cyan
    Write-Host "  docker stop email-detector" -ForegroundColor White
} else {
    Write-Host "Failed to start container!" -ForegroundColor Red
    exit 1
}
