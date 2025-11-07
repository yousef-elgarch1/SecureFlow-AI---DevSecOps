@echo off
echo ========================================
echo AI Security Policy Generator - Backend
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server on http://localhost:8000...
echo Press Ctrl+C to stop the server
echo.

cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
