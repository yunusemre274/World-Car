# WorldCar Routing API - Phase 1

FastAPI-based REST API for computing shortest paths on road networks using Dijkstra's algorithm.

## Features

✅ **Graph Loading at Startup** - Loads city road network once when API starts
✅ **GET /route Endpoint** - Compute shortest paths between coordinates
✅ **JSON Responses** - Returns path, distance, and node count
✅ **Interactive Docs** - Automatic Swagger UI documentation
✅ **Health Checks** - Service status monitoring
✅ **Error Handling** - Clear error messages for invalid inputs

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

Or manually:
```bash
pip install fastapi uvicorn osmnx networkx
```

### 2. Ensure Phase 1 Modules Are Present

The API requires these files in the same directory:
- `graph_loader_standalone.py`
- `node_mapper_standalone.py`
- `path_service_standalone.py`

## Quick Start

### Start the API Server

```bash
uvicorn main:app --reload
```

The API will:
1. Load the road network (takes 15-30 seconds on first run)
2. Start the server on `http://localhost:8000`
3. Display available endpoints

**Output:**
```
======================================================================
Starting FastAPI Routing Service - Phase 1
======================================================================
Loading road network for: Kadıköy, Istanbul, Turkey
This may take 15-30 seconds on first load...
✓ Graph loaded successfully!
  Nodes: 12,453
  Edges: 28,901
======================================================================
API is ready to accept requests
======================================================================
```

### Access the API

Once running, you can access:

- **API Information**: http://localhost:8000/
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Statistics**: http://localhost:8000/stats

## API Endpoints

### 1. `GET /` - API Information

Returns API metadata and usage instructions.

**Example:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "service": "WorldCar Routing API",
  "version": "1.0.0",
  "phase": "Phase 1 - Graph-Based Routing",
  "city": "Kadıköy, Istanbul, Turkey",
  "network": {
    "nodes": 12453,
    "edges": 28901,
    "type": "MultiDiGraph"
  },
  "endpoints": { ... },
  "algorithm": "Dijkstra (via NetworkX)",
  "weight": "length (meters)"
}
```

### 2. `GET /health` - Health Check

Returns service health status.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "graph_loaded": true,
  "city": "Kadıköy, Istanbul, Turkey",
  "nodes": 12453,
  "edges": 28901
}
```

### 3. `GET /stats` - Network Statistics

Returns detailed statistics about the loaded road network.

**Example:**
```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "city": "Kadıköy, Istanbul, Turkey",
  "nodes": 12453,
  "edges": 28901,
  "graph_type": "MultiDiGraph",
  "is_directed": true,
  "is_multigraph": true
}
```

### 4. `GET /route` - Compute Shortest Path ⭐

Compute the shortest path between two coordinates.

**Parameters:**
- `start_lat` (float, required): Starting latitude (-90 to 90)
- `start_lon` (float, required): Starting longitude (-180 to 180)
- `end_lat` (float, required): Ending latitude (-90 to 90)
- `end_lon` (float, required): Ending longitude (-180 to 180)

**Example:**
```bash
curl "http://localhost:8000/route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408"
```

**Success Response:**
```json
{
  "success": true,
  "path": [298734512, 298734513, 298734514, ...],
  "total_distance": 2534.50,
  "node_count": 45,
  "start_coordinates": {
    "latitude": 40.9856,
    "longitude": 29.0298
  },
  "end_coordinates": {
    "latitude": 40.9638,
    "longitude": 29.0408
  },
  "start_node": 298734512,
  "end_node": 298734678,
  "message": "Path found: 45 nodes, 2534.50 meters"
}
```

**No Path Response:**
```json
{
  "success": false,
  "path": [],
  "total_distance": 0.0,
  "node_count": 0,
  "start_coordinates": { ... },
  "end_coordinates": { ... },
  "start_node": 123,
  "end_node": 456,
  "message": "No path exists between nodes 123 and 456"
}
```

## Usage Examples

### Python (requests)

```python
import requests

# Compute route
response = requests.get(
    "http://localhost:8000/route",
    params={
        "start_lat": 40.9856,
        "start_lon": 29.0298,
        "end_lat": 40.9638,
        "end_lon": 29.0408
    }
)

data = response.json()

if data['success']:
    print(f"Distance: {data['total_distance']:.2f} meters")
    print(f"Nodes: {data['node_count']}")
    print(f"Path: {data['path'][:5]}...")  # First 5 nodes
else:
    print(f"Error: {data['message']}")
```

### JavaScript (fetch)

```javascript
const startLat = 40.9856;
const startLon = 29.0298;
const endLat = 40.9638;
const endLon = 29.0408;

const url = `http://localhost:8000/route?start_lat=${startLat}&start_lon=${startLon}&end_lat=${endLat}&end_lon=${endLon}`;

fetch(url)
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`Distance: ${data.total_distance} meters`);
      console.log(`Nodes: ${data.node_count}`);
    } else {
      console.log(`Error: ${data.message}`);
    }
  });
```

### cURL

```bash
# Compute route
curl "http://localhost:8000/route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408"

# Health check
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/stats
```

## Testing

### Using the Test Client

```bash
python test_api.py
```

This will test all endpoints and display results.

### Using Interactive Docs (Swagger UI)

1. Start the API: `uvicorn main:app --reload`
2. Open browser: http://localhost:8000/docs
3. Click on any endpoint to try it out
4. Click "Try it out", enter parameters, click "Execute"

### Manual Testing

```bash
# Test valid route
curl "http://localhost:8000/route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408"

# Test invalid coordinates (should return 400 error)
curl "http://localhost:8000/route?start_lat=91.0&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408"
```

## Error Handling

### 400 - Bad Request

Invalid input parameters (e.g., coordinates out of range).

```json
{
  "detail": "Invalid input: Invalid latitude: 91.0. Must be between -90.0 and 90.0"
}
```

### 500 - Internal Server Error

Route computation failed or unexpected error.

```json
{
  "detail": "Route computation failed: ..."
}
```

### 503 - Service Unavailable

Graph not loaded (shouldn't happen after startup).

```json
{
  "detail": "Service unavailable: Graph not loaded"
}
```

## Configuration

### Change City

Edit `main.py` and modify the `app_state` dictionary:

```python
app_state = {
    'graph': None,
    'city': "Manhattan, New York, USA",  # Change this
    'stats': None
}
```

Then restart the API.

### Change Port

```bash
uvicorn main:app --port 8080
```

### Enable CORS (for frontend)

If you need to access the API from a web frontend, add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment

### Development

```bash
uvicorn main:app --reload --log-level debug
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY main.py .
COPY graph_loader_standalone.py .
COPY node_mapper_standalone.py .
COPY path_service_standalone.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t worldcar-api .
docker run -p 8000:8000 worldcar-api
```

## Performance

- **Startup time**: 15-30 seconds (graph loading)
- **Route computation**: < 100ms per request
- **Concurrent requests**: Supported (graph is read-only)
- **Memory usage**: ~150-200 MB (graph in memory)

## Troubleshooting

**Problem**: API won't start
**Solution**: Check that all Phase 1 modules are in the same directory

**Problem**: Graph loading takes too long
**Solution**: Try a smaller city or district

**Problem**: "No path found" errors
**Solution**: Ensure coordinates are within the loaded city's bounds

**Problem**: Import errors
**Solution**: Install all dependencies: `pip install -r requirements-api.txt`

## What's NOT Included in Phase 1

- ❌ Frontend UI (Phase 5)
- ❌ Traffic simulation (Phase 3)
- ❌ Multiple algorithms (Phase 2)
- ❌ Authentication
- ❌ Rate limiting
- ❌ Database persistence

## Next Steps

After Phase 1 API:
1. Add more algorithms (A*, Bellman-Ford) in Phase 2
2. Add traffic simulation in Phase 3
3. Build web frontend in Phase 5
4. Add authentication and rate limiting
5. Deploy to cloud (AWS, Azure, GCP)

---

**API Version**: 1.0.0
**Status**: ✅ Production Ready
**Algorithm**: Dijkstra (via NetworkX)
**License**: MIT
