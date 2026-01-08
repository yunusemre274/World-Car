"""
WorldCar - Interactive Pathfinding Game

User-driven pathfinding simulation on real-world maps.

HOW TO PLAY:
1. Click on the map to select START node (green circle appears)
2. Click on the map to select TARGET node (orange star appears)
3. Press ENTER to compute path and start simulation
4. Watch the algorithm explore and the car traverse the path
5. View final statistics
6. Press R to restart or ESC to exit

CONTROLS:
- Mouse: Click to select nodes
- ENTER: Start simulation (after selecting both nodes)
- SPACE: Pause/Resume (during simulation)
- R: Restart
- ESC/Q: Exit

This demonstrates:
- Interactive UI with matplotlib
- Real-time node selection with spatial snapping
- State machine-driven game flow
- Professional architecture for academic/portfolio projects
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import osmnx as ox
import networkx as nx

from src.algorithms.astar import AStarAlgorithm
from src.algorithms.dijkstra import DijkstraAlgorithm
from src.game.interactive.interactive_loop import InteractiveGameLoop


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

    # Use largest connected component
    largest_cc = max(nx.weakly_connected_components(graph), key=len)
    graph = graph.subgraph(largest_cc).copy()

    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    return graph


def select_algorithm(choice: str = "astar"):
    """
    Create algorithm instance.

    Args:
        choice: "astar" or "dijkstra"

    Returns:
        Tuple of (algorithm_instance, display_name)
    """
    if choice.lower() == "astar":
        algo = AStarAlgorithm(heuristic_weight=1.5)
        name = "Weighted A* (w=1.5)"
    elif choice.lower() == "dijkstra":
        algo = DijkstraAlgorithm()
        name = "Dijkstra"
    else:
        raise ValueError(f"Unknown algorithm: {choice}")

    return algo, name


def print_instructions():
    """Print game instructions."""
    print("\n" + "="*60)
    print("HOW TO PLAY")
    print("="*60)
    print("1. Click on the map to select START node")
    print("   → Green circle will appear")
    print()
    print("2. Click on the map to select TARGET node")
    print("   → Orange star will appear")
    print()
    print("3. Press ENTER to start simulation")
    print("   → Path will be computed")
    print("   → Car will move along path")
    print()
    print("4. View final statistics")
    print()
    print("KEYBOARD CONTROLS:")
    print("  ENTER - Start simulation (after selecting nodes)")
    print("  SPACE - Pause/Resume")
    print("  R     - Restart")
    print("  ESC/Q - Exit")
    print("="*60)


def main():
    """
    Main entry point for interactive game.
    """
    print("\n" + "="*70)
    print(" "*15 + "WORLDCAR - INTERACTIVE PATHFINDING GAME")
    print("="*70)

    # Configuration
    PLACE = "Moda, Kadıköy, Istanbul, Turkey"
    ALGORITHM = "astar"  # "astar" or "dijkstra"
    SNAP_DISTANCE = 100.0  # meters
    CAR_SPEED = 10  # ticks between movements

    try:
        # Print instructions
        print_instructions()

        # Load map
        print("\n[1/2] Loading map...")
        graph = load_map(PLACE)

        # Select algorithm
        print("\n[2/2] Initializing algorithm...")
        algorithm, algorithm_name = select_algorithm(ALGORITHM)
        print(f"  Algorithm: {algorithm_name}")

        # Create and run game
        print("\nStarting interactive game...")
        print("Close the window or press ESC to exit.")
        print()

        game = InteractiveGameLoop(
            graph=graph,
            algorithm=algorithm,
            algorithm_name=algorithm_name,
            snap_distance=SNAP_DISTANCE,
            car_speed=CAR_SPEED
        )

        game.run()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\nThank you for playing WorldCar!")
    return 0


if __name__ == "__main__":
    exit(main())
