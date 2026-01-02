#!/bin/bash
# cURL Examples for WorldCar Routing API
# Make sure the API is running: uvicorn main:app --reload

echo "============================================================"
echo "WorldCar Routing API - cURL Examples"
echo "============================================================"
echo ""

# 1. API Information
echo "[1/6] GET / - API Information"
echo "--------------------------------------------------------------"
curl -s http://localhost:8000/ | python -m json.tool
echo ""
echo ""

# 2. Health Check
echo "[2/6] GET /health - Health Check"
echo "--------------------------------------------------------------"
curl -s http://localhost:8000/health | python -m json.tool
echo ""
echo ""

# 3. Network Statistics
echo "[3/6] GET /stats - Network Statistics"
echo "--------------------------------------------------------------"
curl -s http://localhost:8000/stats | python -m json.tool
echo ""
echo ""

# 4. Valid Route (Moda to Fenerbahçe)
echo "[4/6] GET /route - Valid Route (Moda to Fenerbahçe)"
echo "--------------------------------------------------------------"
curl -s "http://localhost:8000/route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408" | python -m json.tool
echo ""
echo ""

# 5. Another Valid Route
echo "[5/6] GET /route - Another Route (Kadıköy Square to Bağdat Ave)"
echo "--------------------------------------------------------------"
curl -s "http://localhost:8000/route?start_lat=40.9904&start_lon=29.0255&end_lat=40.9780&end_lon=29.0450" | python -m json.tool
echo ""
echo ""

# 6. Invalid Coordinates (should return error)
echo "[6/6] GET /route - Invalid Coordinates (Expected Error)"
echo "--------------------------------------------------------------"
curl -s "http://localhost:8000/route?start_lat=91.0&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408" | python -m json.tool
echo ""
echo ""

echo "============================================================"
echo "All tests complete!"
echo "============================================================"
