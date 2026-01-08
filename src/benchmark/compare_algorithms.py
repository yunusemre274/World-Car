import osmnx as ox
import networkx as nx
import random
from math import radians, sin, cos, sqrt, atan2

from src.algorithms.dijkstra import DijkstraAlgorithm
from src.algorithms.astar import AStarAlgorithm


def clean(x):
    return float(x)


def haversine_distance(pos1, pos2):
    """Calculate Haversine distance between two (lon, lat) positions"""
    lon1, lat1 = pos1
    lon2, lat2 = pos2
    R = 6371000  # Earth radius in meters

    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    h = (sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2)
    return 2 * R * atan2(sqrt(h), sqrt(1 - h))


def compare():
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    # Use largest connected component
    largest_cc = max(nx.weakly_connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

    # Select nodes with reasonable distance (1-5 km)
    nodes = list(G.nodes)
    max_attempts = 100
    for _ in range(max_attempts):
        source, target = random.sample(nodes, 2)
        pos_s = (G.nodes[source]["x"], G.nodes[source]["y"])
        pos_t = (G.nodes[target]["x"], G.nodes[target]["y"])
        straight_line_dist = haversine_distance(pos_s, pos_t)
        if 1000 < straight_line_dist < 5000:  # 1-5 km
            break

    # Create multiple algorithm variants
    dijkstra = DijkstraAlgorithm()
    astar_standard = AStarAlgorithm(heuristic_weight=1.0)
    astar_weighted_15 = AStarAlgorithm(heuristic_weight=1.5)
    astar_weighted_20 = AStarAlgorithm(heuristic_weight=2.0)

    algorithms = [
        ("dijkstra", dijkstra),
        ("astar_w1.0", astar_standard),
        ("astar_w1.5", astar_weighted_15),
        ("astar_w2.0", astar_weighted_20)
    ]

    results = {"source": source, "target": target, "results": {}}

    # Run all algorithms
    for name, algo in algorithms:
        path, dist, visited, time_ms = algo.run(G, source, target)
        results["results"][name] = {
            "distance": clean(dist),
            "visited_nodes": visited,
            "execution_time_ms": round(time_ms, 2),
            "path_length": len(path)
        }

    # Calculate improvements relative to Dijkstra
    dijkstra_nodes = results["results"]["dijkstra"]["visited_nodes"]
    dijkstra_time = results["results"]["dijkstra"]["execution_time_ms"]
    dijkstra_dist = results["results"]["dijkstra"]["distance"]

    for name in ["astar_w1.0", "astar_w1.5", "astar_w2.0"]:
        r = results["results"][name]

        # Node reduction
        reduction = ((dijkstra_nodes - r["visited_nodes"]) / dijkstra_nodes) * 100
        r["node_reduction_pct"] = round(reduction, 1)

        # Speedup
        speedup = dijkstra_time / r["execution_time_ms"] if r["execution_time_ms"] > 0 else 1.0
        r["speedup"] = round(speedup, 2)

        # Path quality (optimality)
        path_quality = (r["distance"] / dijkstra_dist) * 100 if dijkstra_dist > 0 else 100.0
        r["path_quality_pct"] = round(path_quality, 2)

    # Print formatted results
    print("\n" + "="*60)
    print("ALGORITHM COMPARISON RESULTS")
    print("="*60)
    print(f"Route: {source} -> {target}")
    print(f"Straight-line distance: {straight_line_dist:.0f} meters\n")

    for name, algo in algorithms:
        r = results["results"][name]
        print(f"{name.upper():15} | Nodes: {r['visited_nodes']:4} | Time: {r['execution_time_ms']:6.2f}ms | Dist: {r['distance']:7.1f}m")

        if name != "dijkstra":
            print(f"{'':15} | Reduction: {r['node_reduction_pct']:5.1f}% | Speedup: {r['speedup']:5.2f}x | Quality: {r['path_quality_pct']:6.2f}%")
        print()

    return results


if __name__ == "__main__":
    compare()
