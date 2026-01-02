# WorldCar - Graph-Based Intelligent Route & Traffic Simulation System

A professional, phase-based implementation of an intelligent routing system that models real-world road networks as weighted graphs and computes optimal routes using classical shortest-path algorithms.

## Project Status

**Current Phase:** Phase 1 - Road Network & Graph Modeling ✅ COMPLETED

Phase 1 has been successfully implemented with all deliverables completed.

## Overview

WorldCar is designed to demonstrate core computer science concepts in graph theory and algorithms through a real-world application. The system:

- Models real-world road networks using graph theory
- Applies shortest-path algorithms on spatial data
- Provides clean, modular, and well-documented code
- Is suitable for academic, portfolio, and demonstration purposes

## Features (Phase 1)

✅ **Road Network Extraction**
- Downloads real-world road data from OpenStreetMap using OSMnx
- Supports any location worldwide
- Automatic caching for efficient repeated use

✅ **Graph Modeling**
- Represents roads as weighted directed graphs using NetworkX
- Nodes = road intersections
- Edges = road segments with distance (meters) weights
- Supports one-way streets and complex road networks

✅ **Coordinate Mapping**
- Efficient mapping of latitude/longitude to graph nodes
- KDTree spatial indexing for O(log n) nearest neighbor queries
- Configurable search radius for coordinate snapping

✅ **Shortest Path Routing**
- Dijkstra's algorithm implementation via NetworkX
- Routes between any two geographic coordinates
- Returns complete route information (path, distance, waypoints)

✅ **Network Statistics**
- Comprehensive graph analysis (nodes, edges, total length)
- Connectivity analysis
- Geographic extent calculation
- Network density and degree statistics

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Clone or download the repository:
```bash
cd WorldCar
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. For development (includes testing and visualization tools):
```bash
pip install -r requirements-dev.txt
```

## Quick Start

### Basic Routing Example

```python
from worldcar.graph_loader import GraphLoader
from worldcar.node_mapper import NodeMapper
from worldcar.algorithms import Router

# Load road network for Kadıköy, Istanbul
loader = GraphLoader("Kadıköy, Istanbul, Turkey")
G = loader.get_or_create_graph()

# Initialize mapper and router
mapper = NodeMapper(G)
router = Router(G, mapper)

# Compute shortest path
result = router.compute_shortest_path(
    40.9856, 29.0298,  # Origin (Moda)
    40.9638, 29.0408   # Destination (Fenerbahçe)
)

if result['success']:
    print(f"Distance: {result['distance']:.2f} meters")
    print(f"Route has {len(result['path'])} waypoints")
```

### Run Complete Demo

```bash
python examples/basic_routing.py
```

This will:
1. Load the Kadıköy road network
2. Display network statistics
3. Compute multiple example routes
4. Show route details and performance metrics

### Visualize Routes

```bash
python examples/visualize_graph.py
```

This creates PNG visualizations of:
- The complete road network
- Example routes highlighted on the network
- Multiple routes for comparison

## Project Structure

```
WorldCar/
├── worldcar/                  # Main package
│   ├── config.py             # Configuration settings
│   ├── graph_loader.py       # OSM data extraction
│   ├── node_mapper.py        # Coordinate mapping
│   ├── algorithms.py         # Routing algorithms
│   ├── statistics.py         # Graph analysis
│   └── utils.py              # Helper functions
│
├── data/                     # Data storage (gitignored)
│   ├── raw/                  # OSM cache
│   └── processed/            # Processed graphs
│
├── tests/                    # Test suite
│   ├── test_utils.py
│   └── test_integration.py
│
├── examples/                 # Demo scripts
│   ├── basic_routing.py
│   └── visualize_graph.py
│
├── docs/                     # Documentation
│   ├── architecture.md
│   ├── api_reference.md
│   └── phase1_report.md
│
└── requirements.txt          # Dependencies
```

## Configuration

Edit `worldcar/config.py` to customize:

- **Location**: Change `DEFAULT_LOCATION` to any city/region
- **Network Type**: 'drive', 'walk', 'bike', or 'all'
- **Search Radius**: Maximum distance for coordinate snapping
- **Caching**: Enable/disable graph caching

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=worldcar --cov-report=html

# Run only unit tests (fast)
pytest tests/test_utils.py

# Run integration tests (requires OSM download)
pytest tests/test_integration.py -v
```

## API Documentation

See `docs/api_reference.md` for complete API documentation.

### Core Classes

- **GraphLoader**: Download and manage road network graphs
- **NodeMapper**: Map coordinates to graph nodes
- **Router**: Compute shortest paths between coordinates
- **Statistics Functions**: Analyze graph properties

## Architecture

WorldCar follows a modular architecture with clear separation of concerns:

1. **Data Layer** (`graph_loader.py`): Handles OSM data extraction and caching
2. **Spatial Layer** (`node_mapper.py`): Manages coordinate-to-node mapping
3. **Algorithm Layer** (`algorithms.py`): Implements routing algorithms
4. **Analysis Layer** (`statistics.py`): Provides graph analytics

See `docs/architecture.md` for detailed architecture documentation.

## Performance

**Kadıköy, Istanbul Network:**
- Nodes: ~12,000-15,000 intersections
- Edges: ~25,000-35,000 road segments
- Total length: ~450-500 km

**Performance Metrics:**
- Graph loading: < 30s (first time), < 2s (cached)
- Coordinate mapping: < 1ms per query
- Route computation: < 100ms per query
- Memory usage: < 150 MB

## Roadmap

### Phase 1: Road Network & Graph Modeling ✅ COMPLETED
- ✅ OSM data extraction with OSMnx
- ✅ Graph modeling with NetworkX
- ✅ Coordinate-to-node mapping with KDTree
- ✅ Dijkstra's shortest path algorithm
- ✅ Network statistics and analysis

### Phase 2: Shortest Path Algorithms & Performance Metrics 🔜 PLANNED
- Implement A* algorithm with heuristics
- Implement Bellman-Ford algorithm
- Performance comparison metrics
- Algorithm benchmarking

### Phase 3: Traffic Simulation & Dynamic Weights 🔜 PLANNED
- Dynamic edge weight adjustment
- Traffic congestion simulation
- Time-of-day modeling

### Phase 4: Backend API Layer 🔜 PLANNED
- RESTful API with FastAPI
- Input validation and error handling
- API documentation with Swagger

### Phase 5: Frontend Visualization 🔜 PLANNED
- Interactive map interface with Leaflet.js
- Route visualization
- Algorithm comparison UI

### Phase 6: Deployment & Final Documentation 🔜 PLANNED
- Docker containerization
- Deployment configuration
- Final benchmarks and reports

## Technical Stack

**Core:**
- Python 3.10+
- NetworkX (graph data structure)
- OSMnx (OpenStreetMap data)
- Scipy (KDTree spatial indexing)

**Data Processing:**
- Geopandas (spatial data)
- Shapely (geometric operations)
- Numpy (numerical computations)

**Development:**
- Pytest (testing)
- Black (code formatting)
- Matplotlib (visualization)

## Contributing

This is currently a solo educational/portfolio project. However, suggestions and feedback are welcome!

## Known Limitations

- Phase 1 only implements Dijkstra's algorithm (A* and others in Phase 2)
- Static edge weights only (dynamic traffic in Phase 3)
- Command-line interface only (web interface in Phase 5)
- Single-threaded (may add parallelization in future phases)

## Troubleshooting

### OSM Download Fails

If OSM download fails:
1. Check internet connection
2. Try a smaller area (specific neighborhood instead of entire city)
3. Check OSMnx documentation for server status

### Graph Not Found

If cached graph is not found:
1. Delete `data/processed/*.graphml` to force re-download
2. Check that `DEFAULT_LOCATION` in config is correct
3. Ensure write permissions in project directory

### Import Errors

If you get import errors:
1. Ensure virtual environment is activated
2. Run `pip install -r requirements.txt` again
3. Check Python version (must be 3.10+)

## License

MIT License - See LICENSE file for details

## Author

**Your Name**

## Acknowledgments

- OSMnx for OpenStreetMap integration
- NetworkX for graph algorithms
- OpenStreetMap contributors for map data

## References

- [OSMnx Documentation](https://osmnx.readthedocs.io/)
- [NetworkX Documentation](https://networkx.org/)
- [Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)

---

**Project Created:** January 2026
**Current Version:** 0.1.0 (Phase 1 Complete)
**Status:** ✅ Ready for Use
