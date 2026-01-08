"""
WorldCar - Interactive Pathfinding Simulation

This example demonstrates the complete game architecture:
1. Load a real-world map from OpenStreetMap
2. Compute a shortest path using A* or Dijkstra
3. Run an interactive simulation with animated car movement
4. Display statistics and visualization

This is a professional, CV-level implementation showing:
- Clean separation of concerns
- Game engine architecture
- Real-world algorithm application
- Production-quality code structure

Usage:
    python examples/play_game.py

Controls:
    - Watch the car traverse the computed path
    - Statistics displayed in real-time
    - Final summary shown at completion
"""

import osmnx as ox
import networkx as nx
import random
from math import radians, sin, cos, sqrt, atan2

# Import algorithms
from src.algorithms.astar import AStarAlgorithm
from src.algorithms.dijkstra import DijkstraAlgorithm

# Import game system
from src.game.game_loop import GameLoop, GameConfig


def haversine_distance(graph, node1, node2):
    """Calculate Haversine distance between two nodes."""
    lon1, lat1 = graph.nodes[node1]["x"], graph.nodes[node1]["y"]
    lon2, lat2 = graph.nodes[node2]["x"], graph.nodes[node2]["y"]

    R = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    h = (sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2)
    return 2 * R * atan2(sqrt(h), sqrt(1 - h))


def load_map(place_name: str = "Moda, Kadıköy, Istanbul, Turkey"):
    """
    Load a real-world road network from OpenStreetMap.

    Args:
        place_name: Location to load

    Returns:
        NetworkX MultiDiGraph of the road network
    """
    print(f"Loading map: {place_name}")
    graph = ox.graph_from_place(place_name, network_type="drive")

    # Use largest connected component for guaranteed path existence
    largest_cc = max(nx.weakly_connected_components(graph), key=len)
    graph = graph.subgraph(largest_cc).copy()

    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    return graph


def select_route(graph, min_distance: float = 1000, max_distance: float = 3000):
    """
    Select a good source and target for demonstration.

    Args:
        graph: Road network
        min_distance: Minimum straight-line distance in meters
        max_distance: Maximum straight-line distance in meters

    Returns:
        Tuple of (source_node, target_node)
    """
    print("Selecting route...")
    nodes = list(graph.nodes)

    for _ in range(100):
        source, target = random.sample(nodes, 2)
        dist = haversine_distance(graph, source, target)

        if min_distance <= dist <= max_distance:
            print(f"  Source: {source}")
            print(f"  Target: {target}")
            print(f"  Straight-line distance: {dist:.0f}m")
            return source, target

    # Fallback: use first and middle node
    return nodes[0], nodes[len(nodes) // 2]


def compute_path(graph, source, target, algorithm: str = "astar"):
    """
    Compute shortest path using specified algorithm.

    Args:
        graph: Road network
        source: Source node ID
        target: Target node ID
        algorithm: "astar" or "dijkstra"

    Returns:
        Tuple of (path, distance, visited_nodes, time_ms, algorithm_name)
    """
    print(f"\nComputing path using {algorithm.upper()}...")

    if algorithm.lower() == "astar":
        # Use weighted A* for better performance
        algo = AStarAlgorithm(heuristic_weight=1.5)
        algorithm_name = "Weighted A* (w=1.5)"
    elif algorithm.lower() == "dijkstra":
        algo = DijkstraAlgorithm()
        algorithm_name = "Dijkstra"
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    # Compute path
    path, distance, visited, time_ms = algo.run(graph, source, target)

    print(f"  Algorithm: {algorithm_name}")
    print(f"  Path length: {len(path)} nodes")
    print(f"  Total distance: {distance:.0f}m")
    print(f"  Nodes explored: {visited}")
    print(f"  Computation time: {time_ms:.2f}ms")

    return path, distance, visited, time_ms, algorithm_name


def configure_game(speed: str = "normal"):
    """
    Create game configuration.

    Args:
        speed: "slow", "normal", or "fast"

    Returns:
        GameConfig instance
    """
    speed_settings = {
        "slow": {"tick_rate": 20, "move_interval": 20},
        "normal": {"tick_rate": 30, "move_interval": 10},
        "fast": {"tick_rate": 60, "move_interval": 3}
    }

    settings = speed_settings.get(speed, speed_settings["normal"])

    return GameConfig(
        tick_rate=settings["tick_rate"],
        move_interval=settings["move_interval"],
        auto_close=False,
        show_final_screen=True
    )


def main():
    """
    Main entry point for the pathfinding simulation game.

    Demonstrates the complete workflow:
    1. Load real-world map
    2. Select source and target
    3. Compute shortest path
    4. Run interactive simulation
    """
    print("="*60)
    print("WORLDCAR - PATHFINDING SIMULATION GAME")
    print("="*60)
    print()

    # Configuration
    PLACE = "Moda, Kadıköy, Istanbul, Turkey"
    ALGORITHM = "astar"  # "astar" or "dijkstra"
    SPEED = "normal"  # "slow", "normal", or "fast"

    try:
        # Step 1: Load map
        print("[1/4] Loading map...")
        graph = load_map(PLACE)
        print()

        # Step 2: Select route
        print("[2/4] Selecting route...")
        source, target = select_route(graph, min_distance=1000, max_distance=3000)
        print()

        # Step 3: Compute path
        print("[3/4] Computing path...")
        path, distance, visited, time_ms, algorithm_name = compute_path(
            graph, source, target, ALGORITHM
        )
        print()

        # Step 4: Run simulation
        print("[4/4] Starting simulation...")
        print()
        config = configure_game(SPEED)

        game = GameLoop(
            graph=graph,
            path=path,
            algorithm_name=algorithm_name,
            config=config
        )

        game.run()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\nThank you for using WorldCar!")
    return 0


if __name__ == "__main__":
    exit(main())
