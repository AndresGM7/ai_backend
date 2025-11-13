@echo off
cd /d "%~dp0"
echo ========================================
echo   Iniciando Servidor HTTP
echo ========================================
echo.
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause

