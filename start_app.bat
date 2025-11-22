@echo off
echo Starting GeoMind AI...

start "GeoMind Backend" cmd /k "cd backend/src && uvicorn main:app --reload --port 8000"
start "GeoMind Frontend" cmd /k "cd frontend && npm run dev"

echo Servers started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
echo Press any key to exit this launcher (servers will keep running)...
pause >nul
