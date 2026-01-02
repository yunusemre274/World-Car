# WorldCar System Architecture

## Overview

WorldCar is designed with a modular, layered architecture that separates concerns and enables easy extension for future phases. The system follows clean architecture principles with clear dependencies and interfaces.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│                  (examples/basic_routing.py)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Algorithm Layer                            │
│                  (algorithms.py)                             │
│  • Router class                                              │
│  • Shortest path computation                                 │
│  • Path extraction and analysis                              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Spatial Layer                              │
│                 (node_mapper.py)                             │
│  • NodeMapper class                                          │
│  • KDTree spatial index                                      │
│  • Coordinate-to-node mapping                                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Data Layer                                │
│                (graph_loader.py)                             │
│  • GraphLoader class                                         │
│  • OSM data extraction (OSMnx)                               │
│  • Graph caching and persistence                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Supporting Modules                         │
├─────────────────────────────────────────────────────────────┤
│  • config.py - Configuration settings                        │
│  • utils.py - Helper functions                               │
│  • statistics.py - Graph analysis                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   External Dependencies                      │
├─────────────────────────────────────────────────────────────┤
│  • NetworkX - Graph data structure                           │
│  • OSMnx - OpenStreetMap integration                         │
│  • Scipy - KDTree spatial indexing                           │
│  • OpenStreetMap - Road network data                         │
└─────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### 1. User Interface Layer

**Responsibility:** Provide interfaces for users to interact with the system

**Components:**
- `examples/basic_routing.py` - Command-line demo
- `examples/visualize_graph.py` - Visualization demo

**Future Extensions:**
- Phase 4: RESTful API endpoints
- Phase 5: Web-based interactive map UI

### 2. Algorithm Layer

**Module:** `algorithms.py`

**Responsibility:** Implement routing algorithms and path computation

**Key Classes:**
- `Router` - Main routing interface

**Key Methods:**
- `compute_shortest_path()` - Calculate optimal route between coordinates
- `compute_path_length()` - Calculate total path distance
- `get_path_coordinates()` - Extract waypoint coordinates

**Design Decisions:**
- Uses dependency injection (requires `NodeMapper` instance)
- Returns comprehensive result dictionaries with success/failure info
- Implements error handling for edge cases (disconnected nodes, invalid coords)
- Uses NetworkX's Dijkstra implementation for reliability

**Future Extensions:**
- Phase 2: A* algorithm with Haversine heuristic
- Phase 2: Bellman-Ford algorithm
- Phase 2: Multi-criteria optimization (distance + time)

### 3. Spatial Layer

**Module:** `node_mapper.py`

**Responsibility:** Map geographic coordinates to graph nodes efficiently

**Key Classes:**
- `NodeMapper` - Coordinate-to-node mapping

**Key Methods:**
- `find_nearest_node()` - Find closest node to coordinates
- `snap_to_network()` - Snap coordinates with detailed metadata
- `batch_find_nearest_nodes()` - Batch processing for multiple coordinates

**Data Structures:**
- `scipy.spatial.KDTree` - O(log n) nearest neighbor queries
- Numpy arrays for efficient coordinate storage

**Design Decisions:**
- KDTree spatial indexing for performance (vs O(n) brute force)
- Configurable search radius to reject coordinates too far from roads
- Caches spatial index after first build
- Returns None for out-of-bounds coordinates

**Performance:**
- Build time: < 1 second for ~12k nodes
- Query time: < 1ms per coordinate

### 4. Data Layer

**Module:** `graph_loader.py`

**Responsibility:** Download, cache, and manage road network graphs

**Key Classes:**
- `GraphLoader` - OSM data extraction and graph management

**Key Methods:**
- `download_network()` - Download from OpenStreetMap
- `get_or_create_graph()` - Load from cache or download
- `save_graph()` / `load_from_cache()` - Persistence
- `prepare_graph()` - Validate and prepare for routing

**Data Sources:**
- OpenStreetMap via OSMnx library

**Design Decisions:**
- Automatic caching to avoid repeated OSM API calls
- GraphML format for complete attribute preservation
- Graph simplification to remove unnecessary nodes
- Validates graph structure before use

**Caching Strategy:**
- Raw OSM data cached by OSMnx in `data/raw/`
- Processed graphs saved as GraphML in `data/processed/`
- Cache hit: < 2 seconds to load
- Cache miss: < 30 seconds to download (depends on area size)

### 5. Supporting Modules

#### config.py

**Purpose:** Centralize all configuration settings

**Configuration Categories:**
- Location settings (DEFAULT_LOCATION, NETWORK_TYPE)
- Graph settings (SIMPLIFY_GRAPH, EDGE_WEIGHT_ATTRIBUTE)
- Caching settings (CACHE_DIRECTORY, SAVE_PROCESSED_GRAPH)
- Performance settings (MAX_SEARCH_RADIUS_METERS)

**Design Benefits:**
- Single source of truth for settings
- Easy to modify behavior without code changes
- Clear documentation of configurable parameters

#### utils.py

**Purpose:** Provide common helper functions

**Function Categories:**
- Distance calculations (Haversine, Euclidean)
- Coordinate validation
- Graph validation
- Formatting (distance, coordinates, time)
- Conversions (meters ↔ kilometers)

**Design Pattern:** Pure functions with no side effects

#### statistics.py

**Purpose:** Analyze graph properties

**Key Functions:**
- `compute_graph_statistics()` - Comprehensive metrics
- `analyze_connectivity()` - Connected components analysis
- `get_degree_statistics()` - Node degree distribution

**Use Cases:**
- Network quality assessment
- Performance benchmarking
- Research and analysis

## Data Flow

### Typical Routing Query Flow

```
1. User provides origin and destination coordinates
   ↓
2. Router.compute_shortest_path() called
   ↓
3. NodeMapper.find_nearest_node() maps coordinates to nodes
   ↓
4. NetworkX shortest_path() computes Dijkstra's algorithm
   ↓
5. Router extracts path coordinates and calculates distance
   ↓
6. Result dictionary returned to user
```

### Graph Loading Flow

```
1. GraphLoader.get_or_create_graph() called
   ↓
2. Check if processed graph exists in cache
   ├─ Yes → Load from GraphML (fast)
   └─ No → Continue to download
       ↓
   3. OSMnx downloads from OpenStreetMap
       ↓
   4. Graph simplification and preparation
       ↓
   5. Save to cache for future use
       ↓
   6. Return graph
```

## Design Principles

### 1. Separation of Concerns

Each module has a single, well-defined responsibility:
- `graph_loader` → Data acquisition
- `node_mapper` → Spatial operations
- `algorithms` → Route computation
- `statistics` → Analysis

### 2. Dependency Injection

- `Router` accepts `NodeMapper` as parameter (not created internally)
- Enables testing with mock objects
- Makes dependencies explicit

### 3. Configuration-Driven

- Behavior controlled by `config.py` settings
- Easy to modify without code changes
- Supports different use cases (different cities, network types)

### 4. Error Handling

- Validate inputs at layer boundaries
- Return structured error information (not just exceptions)
- Log errors for debugging
- Fail gracefully with informative messages

### 5. Caching Strategy

- Multiple cache levels (OSM data, processed graphs)
- Transparent to user (automatic cache management)
- Significant performance improvement for repeated use

### 6. Type Hints and Documentation

- All functions have type hints
- Google-style docstrings
- Usage examples in docstrings
- Clear API contracts

## Performance Considerations

### Spatial Indexing

**Choice:** KDTree from scipy.spatial

**Rationale:**
- O(log n) nearest neighbor queries
- Much faster than O(n) brute force for large graphs
- Standard, well-tested implementation

**Alternatives Considered:**
- OSMnx built-in nearest_nodes() - Good but less control
- R-tree - More complex, overkill for this use case

### Graph Representation

**Choice:** NetworkX MultiDiGraph

**Rationale:**
- Native support for directed edges (one-way streets)
- Multiple edges between nodes (different road types)
- Rich algorithm library (Dijkstra, A*, etc.)
- Direct integration with OSMnx

**Trade-offs:**
- Memory usage higher than custom implementation
- But: Development time much lower, reliability much higher

### Caching

**Impact:**
- First load: ~30 seconds (OSM download)
- Subsequent loads: ~2 seconds (GraphML file read)
- 15x speedup for repeated use

## Extensibility

The architecture is designed for easy extension:

### Phase 2: Additional Algorithms

**Changes Required:**
- Add new methods to `Router` class
- No changes to other layers
- Example: `router.compute_shortest_path_astar()`

### Phase 3: Dynamic Weights

**Changes Required:**
- Add traffic data source to `graph_loader`
- Add weight update methods to `Router`
- Minimal impact on existing code

### Phase 4: API Layer

**New Component:** FastAPI application

**Integration:**
- API layer calls existing `Router` interface
- No changes to core modules
- API handles HTTP, validation, serialization

### Phase 5: Web Frontend

**New Component:** React + Leaflet application

**Integration:**
- Consumes Phase 4 API
- No changes to backend code

## Testing Strategy

### Unit Tests

**Coverage:** Individual functions and methods
**Examples:** `test_utils.py`
**Approach:** Pure functions, mock external dependencies

### Integration Tests

**Coverage:** Complete workflows
**Examples:** `test_integration.py`
**Approach:** Use real OSM data, test end-to-end

### Performance Tests

**Coverage:** Time and resource constraints
**Approach:** Assert operations complete within target times

## Security Considerations

### Current State (Phase 1)

- Local execution only (no network exposure)
- Reads from OpenStreetMap (trusted public data)
- No user data storage
- No authentication required

### Future Phases

- Phase 4 API: Input validation, rate limiting
- Phase 5 Frontend: CORS, HTTPS, secure communications

## Monitoring and Logging

### Current Implementation

- Python logging module
- Log levels: INFO (default), DEBUG (detailed)
- Logs key operations: graph loading, routing, errors

### Log Output Examples

```
INFO:graph_loader:GraphLoader initialized for location: Kadıköy, Istanbul, Turkey
INFO:graph_loader:Downloading road network for: Kadıköy, Istanbul, Turkey
INFO:graph_loader:Successfully downloaded graph: 12453 nodes, 28901 edges
INFO:node_mapper:Building spatial index...
INFO:algorithms:Finding route from (40.985600, 29.029800) to (40.963800, 29.040800)
```

### Future Extensions

- Performance metrics collection
- Error rate tracking
- Usage analytics

## Deployment Architecture (Future)

### Phase 6 Target Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
┌──────▼──────────┐
│  React Frontend │
│  (Leaflet Maps) │
└──────┬──────────┘
       │ REST API
┌──────▼──────────┐
│  FastAPI Backend│
│  (Docker)       │
└──────┬──────────┘
       │
┌──────▼──────────┐
│  WorldCar Core  │
│  (This System)  │
└─────────────────┘
```

## Conclusion

WorldCar's architecture prioritizes:
1. **Modularity** - Clear separation of concerns
2. **Extensibility** - Easy to add new features
3. **Performance** - Efficient algorithms and caching
4. **Reliability** - Comprehensive error handling
5. **Maintainability** - Clean code with documentation

This foundation supports the planned phases while maintaining code quality and professional standards.
