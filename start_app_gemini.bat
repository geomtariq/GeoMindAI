@echo off
echo Starting GeoMind AI with Gemini AI and Mock Database...

start "GeoMind Backend (Gemini+Mock)" cmd /k "cd backend/src && set USE_MOCK_DB=True && uvicorn main:app --reload --port 8000"
start "GeoMind Frontend" cmd /k "cd frontend && npm run dev"

echo Servers started with Gemini AI and Mock Database!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo.
echo Press any key to exit this launcher (servers will keep running)...
pause >nul

