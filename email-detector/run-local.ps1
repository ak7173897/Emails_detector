# Run the Email Security Detector locally using the workspace virtual environment

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$venvPython = Join-Path $projectRoot '..\.venv\Scripts\python.exe'
if (-Not (Test-Path $venvPython)) {
    Write-Error "Could not find the Python executable in ..\.venv\Scripts\python.exe"
    exit 1
}

Write-Host "Starting Email Detector from $projectRoot"
Write-Host "Using Python: $venvPython"

$env:FLASK_APP = 'src.wsgi:application'
$env:FLASK_ENV = 'development'
$env:SECRET_KEY = 'dev-secret-key-32-characters!!'

& $venvPython -m flask run --host=127.0.0.1 --port=5000
