# Phase 1 Quick Start Guide

## Overview

Phase 1 provides three core modules for graph-based routing:

1. **graph_loader** - Load road networks from OpenStreetMap
2. **node_mapper** - Map coordinates to graph nodes
3. **path_service** - Compute shortest paths using Dijkstra

## Installation

```bash
pip install osmnx>=1.9.0 networkx>=3.2
```

## Quick Example

```python
from graph_loader_standalone import load_city_graph
from node_mapper_standalone import find_nearest_node
from path_service_standalone import compute_shortest_path

# 1. Load road network
graph = load_city_graph("Kadıköy, Istanbul, Turkey")

# 2. Map coordinates to nodes
start_node = find_nearest_node(graph, 40.9856, 29.0298)  # Moda
end_node = find_nearest_node(graph, 40.9638, 29.0408)    # Fenerbahçe

# 3. Compute shortest path
result = compute_shortest_path(graph, start_node, end_node)

# 4. Display results
if result['success']:
    print(f"Distance: {result['path_length_m']:.2f} meters")
    print(f"Nodes: {result['num_nodes']}")
else:
    print(f"No path found: {result['message']}")
```

## Module Details

### graph_loader_standalone.py

**Functions:**
- `load_city_graph(city_name: str) -> nx.MultiDiGraph`
- `get_graph_stats(graph) -> Dict[str, Any]`

**Example:**
```python
graph = load_city_graph("Manhattan, New York, USA")
stats = get_graph_stats(graph)
print(f"Loaded {stats['num_nodes']} nodes")
```

### node_mapper_standalone.py

**Functions:**
- `find_nearest_node(graph, lat, lon) -> int`
- `get_node_coordinates(graph, node_id) -> Tuple[float, float]`
- `validate_coordinates(lat, lon) -> None`
- `batch_find_nearest_nodes(graph, coords) -> List[int]`

**Example:**
```python
# Find nearest node
node_id = find_nearest_node(graph, 40.9856, 29.0298)

# Get node's coordinates
lat, lon = get_node_coordinates(graph, node_id)

# Validate coordinates (raises ValueError if invalid)
validate_coordinates(40.9856, 29.0298)

# Batch processing
coords = [(40.9856, 29.0298), (40.9638, 29.0408)]
nodes = batch_find_nearest_nodes(graph, coords)
```

### path_service_standalone.py

**Functions:**
- `compute_shortest_path(graph, start_node, end_node) -> Dict[str, Any]`
- `calculate_path_length(graph, path) -> float`
- `has_path(graph, start_node, end_node) -> bool`

**Example:**
```python
# Compute shortest path
result = compute_shortest_path(graph, start_node, end_node)

# Check result
if result['success']:
    print(f"Path: {result['node_ids']}")
    print(f"Length: {result['path_length_m']} meters")
    print(f"Nodes: {result['num_nodes']}")
else:
    print(f"Error: {result['message']}")

# Quick path existence check
if has_path(graph, start_node, end_node):
    print("Path exists!")
```

## Return Value Structures

### compute_shortest_path() returns:
```python
{
    'success': bool,              # True if path found
    'node_ids': List[int],        # List of node IDs in path
    'path_length_m': float,       # Total length in meters
    'num_nodes': int,             # Number of nodes in path
    'start_node': int,            # Starting node ID
    'end_node': int,              # Ending node ID
    'message': str                # Success/error message
}
```

### get_graph_stats() returns:
```python
{
    'num_nodes': int,             # Number of intersections
    'num_edges': int,             # Number of road segments
    'graph_type': str,            # 'MultiDiGraph'
    'is_directed': bool,          # True for road networks
    'is_multigraph': bool         # True
}
```

## Running Demos

### Test individual modules:
```bash
python graph_loader_standalone.py
python node_mapper_standalone.py
python path_service_standalone.py
```

### Run complete Phase 1 demo:
```bash
python complete_phase1_demo.py
```

### Run Phase 1 example:
```bash
python example_phase1.py
```

## Error Handling

### Invalid Coordinates
```python
from node_mapper_standalone import validate_coordinates

try:
    validate_coordinates(91.0, 29.0)  # Invalid latitude
except ValueError as e:
    print(f"Error: {e}")
# Output: Invalid latitude: 91.0. Must be between -90.0 and 90.0
```

### No Path Exists
```python
result = compute_shortest_path(graph, start_node, end_node)

if not result['success']:
    print(f"No path: {result['message']}")
    # Nodes may be in disconnected components
```

### Node Not Found
```python
try:
    result = compute_shortest_path(graph, 999999, 123456)
except ValueError as e:
    print(f"Error: {e}")
# Output: Start node 999999 not found in graph
```

## Common Use Cases

### 1. Route Planning
```python
# Load city
graph = load_city_graph("Istanbul, Turkey")

# Find route between two addresses
start = find_nearest_node(graph, 41.0082, 28.9784)  # Sultanahmet
end = find_nearest_node(graph, 41.0255, 28.9744)    # Taksim

# Compute route
result = compute_shortest_path(graph, start, end)

if result['success']:
    print(f"Route: {result['path_length_m']/1000:.2f} km")
```

### 2. Batch Route Computation
```python
# Find nodes for multiple locations
locations = [
    (40.9856, 29.0298),
    (40.9638, 29.0408),
    (40.9904, 29.0255)
]

nodes = batch_find_nearest_nodes(graph, locations)

# Compute routes between consecutive points
for i in range(len(nodes) - 1):
    result = compute_shortest_path(graph, nodes[i], nodes[i+1])
    if result['success']:
        print(f"Segment {i+1}: {result['path_length_m']:.2f}m")
```

### 3. Distance Matrix
```python
# Compute all-pairs distances
locations = [(lat1, lon1), (lat2, lon2), (lat3, lon3)]
nodes = batch_find_nearest_nodes(graph, locations)

for i, start in enumerate(nodes):
    for j, end in enumerate(nodes):
        if i != j:
            result = compute_shortest_path(graph, start, end)
            if result['success']:
                print(f"{i}→{j}: {result['path_length_m']:.0f}m")
```

## Performance Notes

- **First load**: 15-30 seconds (downloads from OSM)
- **Subsequent loads**: OSMnx caches data automatically
- **Node mapping**: < 1ms per coordinate
- **Path computation**: < 100ms for typical routes

## Coordinate Systems

- **Input**: WGS84 (latitude, longitude)
- **Latitude range**: -90.0 to 90.0
- **Longitude range**: -180.0 to 180.0
- **Distance units**: Meters

## What's NOT Included in Phase 1

- ❌ A* algorithm (Phase 2)
- ❌ Bellman-Ford algorithm (Phase 2)
- ❌ Traffic simulation (Phase 3)
- ❌ Dynamic weights (Phase 3)
- ❌ REST API (Phase 4)
- ❌ Web frontend (Phase 5)

Phase 1 provides the foundation - graph loading, coordinate mapping, and basic shortest path routing.

## Troubleshooting

**Problem**: OSM download fails
**Solution**: Check internet connection, try smaller area

**Problem**: "No path exists" error
**Solution**: Nodes may be in disconnected components. Use `has_path()` to check first.

**Problem**: Coordinates not mapping to nodes
**Solution**: Ensure coordinates are within the loaded city's bounds

**Problem**: Import errors
**Solution**: Install dependencies: `pip install osmnx networkx`

## Next Steps

After Phase 1, you can:
1. Implement additional algorithms (A*, Bellman-Ford)
2. Add traffic simulation
3. Build REST API
4. Create web frontend
5. Deploy to production

---

**Phase 1 Status**: ✅ Complete
**Ready for**: Phase 2 - Multiple Algorithms & Metrics
