"""
FastAPI Main Application - Phase 1 Routing API

A REST API for computing shortest paths on road networks using Dijkstra's algorithm.

Requirements:
- Python 3.10+
- fastapi>=0.104.0
- uvicorn>=0.24.0
- osmnx>=1.9.0
- networkx>=3.2

Usage:
    uvicorn main:app --reload

Endpoints:
    GET /route - Compute shortest path between two coordinates
    GET /health - Health check
    GET / - API information
"""

from typing import Optional, Dict, Any, List
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import networkx as nx

# Import Phase 1 modules
from graph_loader_standalone import load_city_graph, get_graph_stats
from node_mapper_standalone import find_nearest_node, validate_coordinates
from path_service_standalone import compute_shortest_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Global State
# ============================================================================

# Graph will be loaded at startup and stored globally
app_state = {
    'graph': None,
    'city': "Kadıköy, Istanbul, Turkey",
    'stats': None
}


# ============================================================================
# Lifespan Context Manager (Startup/Shutdown)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Loads the graph once at startup and keeps it in memory.
    """
    # Startup: Load graph
    logger.info("=" * 70)
    logger.info("Starting FastAPI Routing Service - Phase 1")
    logger.info("=" * 70)

    city = app_state['city']
    logger.info(f"Loading road network for: {city}")
    logger.info("This may take 15-30 seconds on first load...")

    try:
        # Load graph from OpenStreetMap
        graph = load_city_graph(city)
        app_state['graph'] = graph

        # Get statistics
        stats = get_graph_stats(graph)
        app_state['stats'] = stats

        logger.info("✓ Graph loaded successfully!")
        logger.info(f"  Nodes: {stats['num_nodes']:,}")
        logger.info(f"  Edges: {stats['num_edges']:,}")
        logger.info("=" * 70)
        logger.info("API is ready to accept requests")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Failed to load graph: {str(e)}")
        raise RuntimeError(f"Cannot start API without graph: {str(e)}")

    yield  # Application runs here

    # Shutdown: Cleanup
    logger.info("Shutting down API...")
    app_state['graph'] = None
    app_state['stats'] = None


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="WorldCar Routing API",
    description="Phase 1 - Shortest path routing using Dijkstra's algorithm",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """
    API information and usage instructions.
    """
    stats = app_state.get('stats', {})

    return {
        "service": "WorldCar Routing API",
        "version": "1.0.0",
        "phase": "Phase 1 - Graph-Based Routing",
        "city": app_state['city'],
        "network": {
            "nodes": stats.get('num_nodes', 0),
            "edges": stats.get('num_edges', 0),
            "type": stats.get('graph_type', 'Unknown')
        },
        "endpoints": {
            "route": {
                "method": "GET",
                "path": "/route",
                "description": "Compute shortest path between coordinates",
                "parameters": {
                    "start_lat": "Starting latitude (-90 to 90)",
                    "start_lon": "Starting longitude (-180 to 180)",
                    "end_lat": "Ending latitude (-90 to 90)",
                    "end_lon": "Ending longitude (-180 to 180)"
                },
                "example": "/route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408"
            },
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Health check endpoint"
            }
        },
        "algorithm": "Dijkstra (via NetworkX)",
        "weight": "length (meters)"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns service status and graph availability.
    """
    graph = app_state.get('graph')
    stats = app_state.get('stats')

    is_healthy = graph is not None and stats is not None

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "graph_loaded": graph is not None,
        "city": app_state['city'],
        "nodes": stats.get('num_nodes', 0) if stats else 0,
        "edges": stats.get('num_edges', 0) if stats else 0
    }


@app.get("/route")
async def compute_route(
    start_lat: float = Query(..., description="Starting latitude", ge=-90, le=90),
    start_lon: float = Query(..., description="Starting longitude", ge=-180, le=180),
    end_lat: float = Query(..., description="Ending latitude", ge=-90, le=90),
    end_lon: float = Query(..., description="Ending longitude", ge=-180, le=180)
) -> Dict[str, Any]:
    """
    Compute shortest path between two geographic coordinates.

    Uses Dijkstra's algorithm to find the optimal route between the starting
    and ending coordinates. The route is computed on the road network graph
    loaded at startup.

    Args:
        start_lat: Starting latitude in decimal degrees (-90 to 90)
        start_lon: Starting longitude in decimal degrees (-180 to 180)
        end_lat: Ending latitude in decimal degrees (-90 to 90)
        end_lon: Ending longitude in decimal degrees (-180 to 180)

    Returns:
        JSON response with:
        - success: Whether route was found
        - path: List of node IDs forming the route
        - total_distance: Total distance in meters
        - node_count: Number of nodes in the path
        - start_coordinates: Starting coordinates
        - end_coordinates: Ending coordinates
        - message: Success or error message

    Example:
        GET /route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408

    Raises:
        HTTPException: If graph is not loaded or route computation fails
    """
    # Check if graph is loaded
    graph = app_state.get('graph')
    if graph is None:
        logger.error("Graph not loaded")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable: Graph not loaded"
        )

    logger.info(
        f"Route request: ({start_lat}, {start_lon}) -> ({end_lat}, {end_lon})"
    )

    try:
        # Step 1: Validate coordinates
        validate_coordinates(start_lat, start_lon)
        validate_coordinates(end_lat, end_lon)

        # Step 2: Map coordinates to nodes
        start_node = find_nearest_node(graph, start_lat, start_lon)
        end_node = find_nearest_node(graph, end_lat, end_lon)

        logger.info(f"Mapped to nodes: {start_node} -> {end_node}")

        # Step 3: Compute shortest path
        result = compute_shortest_path(graph, start_node, end_node)

        # Step 4: Format response
        response = {
            "success": result['success'],
            "path": result['node_ids'],
            "total_distance": result['path_length_m'],
            "node_count": result['num_nodes'],
            "start_coordinates": {
                "latitude": start_lat,
                "longitude": start_lon
            },
            "end_coordinates": {
                "latitude": end_lat,
                "longitude": end_lon
            },
            "start_node": result['start_node'],
            "end_node": result['end_node'],
            "message": result['message']
        }

        if result['success']:
            logger.info(
                f"Route found: {result['num_nodes']} nodes, "
                f"{result['path_length_m']:.2f}m"
            )
        else:
            logger.warning(f"Route failed: {result['message']}")

        return response

    except ValueError as e:
        # Validation error (invalid coordinates)
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )

    except RuntimeError as e:
        # Node mapping or path computation error
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Route computation failed: {str(e)}"
        )

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# Optional: Additional Endpoints
# ============================================================================

@app.get("/stats")
async def get_statistics():
    """
    Get graph statistics.
    Returns information about the loaded road network.
    """
    stats = app_state.get('stats')

    if stats is None:
        raise HTTPException(
            status_code=503,
            detail="Graph not loaded"
        )

    return {
        "city": app_state['city'],
        "nodes": stats['num_nodes'],
        "edges": stats['num_edges'],
        "graph_type": stats['graph_type'],
        "is_directed": stats['is_directed'],
        "is_multigraph": stats['is_multigraph']
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("WorldCar Routing API - Phase 1".center(70))
    print("=" * 70)
    print("\nStarting server...")
    print("API will be available at: http://localhost:8000")
    print("\nEndpoints:")
    print("  • http://localhost:8000/         - API info")
    print("  • http://localhost:8000/docs     - Interactive documentation")
    print("  • http://localhost:8000/health   - Health check")
    print("  • http://localhost:8000/route    - Compute route")
    print("  • http://localhost:8000/stats    - Network statistics")
    print("\nExample:")
    print("  http://localhost:8000/route?start_lat=40.9856&start_lon=29.0298&end_lat=40.9638&end_lon=29.0408")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
