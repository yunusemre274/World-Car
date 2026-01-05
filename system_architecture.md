+---------------------+
|   OpenStreetMap     |
|   (OSM Data)        |
+----------+----------+
           |
           v
+---------------------+
|     OSMnx Loader    |
| graph_from_place()  |
+----------+----------+
           |
           v
+-----------------------------+
|   NetworkX MultiDiGraph     |
|  - Nodes (intersections)    |
|  - Edges (roads)            |
|  - length (meters)          |
+----------+------------------+
           |
           v
+----------------------------------------------+
|            Routing Engine                     |
|----------------------------------------------|
|  Dijkstra | A* | Bellman-Ford                 |
|  (manual implementations)                    |
+----------+-----------------------------------+
           |
           v
+-----------------------------+
| Performance Measurement     |
| - visited nodes             |
| - execution time (ms)       |
+----------+------------------+
           |
           v
+-----------------------------+
| Benchmark & Evaluation      |
| - algorithm comparison      |
| - output metrics            |
+-----------------------------+

src/
├── algorithms/
│   ├── dijkstra.py        # Manual Dijkstra (priority queue)
│   ├── astar.py           # A* with Haversine heuristic
│   └── bellman_ford.py    # Bellman–Ford (negative weights support)
│
├── benchmark/
│   └── compare_algorithms.py
│
├── tests/
│   ├── test_dijkstra.py
│   ├── test_astar.py
│   └── bellman_ford_test.py
│
├── performance/
│   └── timer.py           # Execution time decorator
│
└── __init__.py

