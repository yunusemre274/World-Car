@echo off
REM cURL Examples for WorldCar Routing API (Windows)
REM Make sure the API is running: uvicorn main:app --reload

echo ============================================================
echo WorldCar Routing API - cURL Examples (Windows)
echo ============================================================
echo.

REM 1. API Information
echo [1/6] GET / - API Information
echo --------------------------------------------------------------
curl -s http://localhost:8000/
echo.
echo.

REM 2. Health Check
echo [2/6] GET /health - Health Check
echo --------------------------------------------------------------
curl -s http://localhost:8000/health
echo.
echo.

REM 3. Network Statistics
echo [3/6] GET /stats - Network Statistics
echo --------------------------------------------------------------
curl -s http://localhost:8000/stats
echo.
echo.

REM 4. Valid Route (Moda to Fenerbahçe)
echo [4/6] GET /route - Valid Route (Moda to Fenerbahce)
echo --------------------------------------------------------------
curl -s "http://localhost:8000/route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408"
echo.
echo.

REM 5. Another Valid Route
echo [5/6] GET /route - Another Route (Kadiköy Square to Bagdat Ave)
echo --------------------------------------------------------------
curl -s "http://localhost:8000/route?start_lat=40.9904&start_lon=29.0255&end_lat=40.9780&end_lon=29.0450"
echo.
echo.

REM 6. Invalid Coordinates (should return error)
echo [6/6] GET /route - Invalid Coordinates (Expected Error)
echo --------------------------------------------------------------
curl -s "http://localhost:8000/route?start_lat=91.0&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408"
echo.
echo.

echo ============================================================
echo All tests complete!
echo ============================================================
pause
