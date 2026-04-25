@echo off
echo ====================================================
echo Starting EmailShield AI Application...
echo Rebuilding Docker to apply any new code updates...
echo ====================================================

docker-compose up -d --build

echo.
echo ====================================================
echo Done! The website is running securely.
echo Please open your browser and go to:
echo http://localhost:5000
echo ====================================================
pause
