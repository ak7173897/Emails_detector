@echo off
REM Run the Email Security Detector locally using the workspace virtual environment
cd /d "%~dp0"
set VENV_PY="%~dp0..\.venv\Scripts\python.exe"
if not exist %VENV_PY% (
  echo Could not find python.exe in %~dp0..\.venv\Scripts\python.exe
  exit /b 1
)
set FLASK_APP=src.wsgi:application
set FLASK_ENV=development
set SECRET_KEY=dev-secret-key-32-characters!!
%VENV_PY% -m flask run --host=127.0.0.1 --port=5000
