@echo off
echo ========================================
echo  Starting Backend Server
echo ========================================
echo.

cd /d "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent"

REM Set environment variables to fix encoding issues
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo Starting FastAPI server on http://localhost:8000
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause
