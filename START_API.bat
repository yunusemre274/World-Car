@echo off
REM Quick Start Script for WorldCar Routing API (Windows)

echo.
echo ======================================================================
echo           WorldCar Routing API - Quick Start (Phase 1)
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
echo.

REM Check if FastAPI is installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo FastAPI not found. Installing dependencies...
    pip install -r requirements-api.txt
) else (
    echo Dependencies already installed.
)

echo.
echo [2/3] Starting FastAPI server...
echo.
echo The API will:
echo   - Load the road network (15-30 seconds on first run)
echo   - Start server on http://localhost:8000
echo.
echo Available endpoints:
echo   - http://localhost:8000/         - API information
echo   - http://localhost:8000/docs     - Interactive documentation
echo   - http://localhost:8000/health   - Health check
echo   - http://localhost:8000/route    - Compute routes
echo.
echo Press Ctrl+C to stop the server
echo.
echo ======================================================================
echo.

REM Start the API
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
