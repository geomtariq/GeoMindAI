Write-Host "Starting GeoMind AI..." -ForegroundColor Cyan

# Start Backend
Start-Process -FilePath "cmd" -ArgumentList "/k cd backend/src && uvicorn main:app --reload --port 8000" -WindowStyle Normal
Write-Host "Backend started on http://localhost:8000" -ForegroundColor Green

# Start Frontend
Start-Process -FilePath "cmd" -ArgumentList "/k cd frontend && npm run dev" -WindowStyle Normal
Write-Host "Frontend started on http://localhost:3000" -ForegroundColor Green

Write-Host "`nServers are running in separate windows." -ForegroundColor Yellow
Write-Host "Press any key to exit this launcher..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
