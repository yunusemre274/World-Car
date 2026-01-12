"""
WorldCar - Step-by-Step Algorithm Visualization

This example demonstrates ANIMATED pathfinding algorithm execution.

Unlike the regular game (which shows the car moving on a pre-computed path),
this visualization shows the algorithm DISCOVERING the path in real-time.

You'll see:
- Gray nodes: Already explored
- Yellow nodes: In the frontier (open set)
- Red node: Currently being explored
- Blue dashed line: Current path being considered
- Green line: Final discovered path

Usage:
    python examples/visualize_algorithm.py

Controls:
    - Watch the algorithm explore the graph step-by-step
    - Adjust SPEED below to control visualization speed
    - Close window to exit

Educational Value:
    - See how A* uses heuristics to guide search toward target
    - Compare Weighted A* vs standard A* exploration patterns
    - Understand why A* explores fewer nodes than Dijkstra
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import osmnx as ox
import networkx as nx
import random
from math import radians, sin, cos, sqrt, atan2

from src.algorithms.astar import AStarAlgorithm
from src.game.algorithm_game_loop import (
    AlgorithmGameLoop,
    AlgorithmVisualizationConfig,
    create_slow_config,
    create_normal_config,
    create_fast_config,
    create_turbo_config
)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Location to visualize
PLACE = "Moda, Kadıköy, Istanbul, Turkey"

# Algorithm configuration
HEURISTIC_WEIGHT = 1.5  # 1.0 = A*, >1.0 = Weighted A* (faster but less optimal)

# Visualization speed - ADJUST THIS TO CONTROL ANIMATION SPEED
SPEED = "normal"  # Options: "slow", "normal", "fast", "turbo"

# Distance range for route selection (meters)
MIN_DISTANCE = 1000
MAX_DISTANCE = 2500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def haversine_distance(graph, node1, node2):
    """Calculate straight-line distance between two nodes."""
    lon1, lat1 = graph.nodes[node1]["x"], graph.nodes[node1]["y"]
    lon2, lat2 = graph.nodes[node2]["x"], graph.nodes[node2]["y"]

    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    h = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(h), sqrt(1 - h))


def load_map(place_name: str):
    """Load road network from OpenStreetMap."""
    print(f"📍 Loading map: {place_name}")
    graph = ox.graph_from_place(place_name, network_type="drive")

    # Use largest connected component
    largest_cc = max(nx.weakly_connected_components(graph), key=len)
    graph = graph.subgraph(largest_cc).copy()

    print(f"   ✓ Loaded {len(graph.nodes):,} nodes, {len(graph.edges):,} edges")
    return graph


def select_route(graph, min_dist: float, max_dist: float):
    """Select a good source and target for visualization."""
    print(f"\n🎯 Selecting route ({min_dist}m - {max_dist}m)...")
    nodes = list(graph.nodes)

    for attempt in range(100):
        source, target = random.sample(nodes, 2)
        dist = haversine_distance(graph, source, target)

        if min_dist <= dist <= max_dist:
            print(f"   ✓ Source: {source}")
            print(f"   ✓ Target: {target}")
            print(f"   ✓ Straight-line distance: {dist:.0f}m")
            return source, target

    # Fallback
    print(f"   ⚠ Using fallback route")
    return nodes[0], nodes[len(nodes) // 2]


def get_speed_config(speed: str) -> AlgorithmVisualizationConfig:
    """Get visualization config for speed preset."""
    configs = {
        "slow": create_slow_config(),
        "normal": create_normal_config(),
        "fast": create_fast_config(),
        "turbo": create_turbo_config()
    }
    return configs.get(speed.lower(), create_normal_config())


# ============================================================================
# MAIN VISUALIZATION
# ============================================================================

def main():
    """
    Main entry point for algorithm visualization.

    Flow:
    1. Load map
    2. Select source and target
    3. Create algorithm
    4. Run step-by-step visualization
    5. Show final statistics
    """
    print()
    print("="*70)
    print("WORLDCAR - ALGORITHM VISUALIZATION".center(70))
    print("Step-by-Step Pathfinding Exploration".center(70))
    print("="*70)
    print()

    try:
        # Step 1: Load map
        graph = load_map(PLACE)

        # Step 2: Select route
        source, target = select_route(graph, MIN_DISTANCE, MAX_DISTANCE)

        # Step 3: Create algorithm
        print(f"\n⚙️  Configuring algorithm...")
        algorithm = AStarAlgorithm(heuristic_weight=HEURISTIC_WEIGHT)

        if HEURISTIC_WEIGHT == 1.0:
            algorithm_name = "A* (Optimal)"
        else:
            algorithm_name = f"Weighted A* (w={HEURISTIC_WEIGHT})"

        print(f"   ✓ Algorithm: {algorithm_name}")
        print(f"   ✓ Speed: {SPEED.upper()}")

        # Step 4: Create visualization config
        config = get_speed_config(SPEED)
        print(f"   ✓ Step delay: {config.step_delay*1000:.1f}ms")

        # Step 5: Run visualization
        print()
        print("="*70)
        print("STARTING VISUALIZATION")
        print("="*70)
        print()
        print("🔍 Watch the algorithm explore the graph:")
        print("   • Gray nodes = Already explored")
        print("   • Yellow nodes = In frontier (open set)")
        print("   • Red node = Currently exploring")
        print("   • Blue dashed line = Current path")
        print("   • Green line = Final path (when found)")
        print()

        # ⭐ THIS IS THE MAIN CALL ⭐
        # This runs the algorithm step-by-step with visualization
        game_loop = AlgorithmGameLoop(
            graph=graph,
            algorithm=algorithm,
            source=source,
            target=target,
            algorithm_name=algorithm_name,
            config=config
        )

        result = game_loop.run()

        if result:
            path, distance, visited_count, time_ms = result
            print()
            print("="*70)
            print("✅ VISUALIZATION COMPLETE!")
            print("="*70)
            print()
            print(f"📊 Algorithm Efficiency:")
            print(f"   • Path found: {len(path)} nodes")
            print(f"   • Distance: {distance:.0f} meters")
            print(f"   • Nodes explored: {visited_count}")
            print(f"   • Computation time: {time_ms:.2f}ms")
            print(f"   • Exploration ratio: {visited_count}/{len(graph.nodes)} "
                  f"({100*visited_count/len(graph.nodes):.1f}%)")
            print()

            # Compare with other algorithms
            if HEURISTIC_WEIGHT > 1.0:
                print("💡 TIP: Try HEURISTIC_WEIGHT = 1.0 to see standard A*")
                print("         (explores more nodes but guarantees optimal path)")
            else:
                print("💡 TIP: Try HEURISTIC_WEIGHT = 1.5 to see Weighted A*")
                print("         (explores fewer nodes, near-optimal path)")

            print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print()
    print("="*70)
    print("Thank you for using WorldCar Algorithm Visualization!")
    print("="*70)
    print()
    return 0


# ============================================================================
# COMPARISON MODE (BONUS)
# ============================================================================

def compare_algorithms():
    """
    Compare different algorithm configurations side-by-side.

    Runs the same route with:
    - Standard A* (w=1.0)
    - Weighted A* (w=1.5)
    - Weighted A* (w=2.0)

    This helps understand the trade-off between optimality and speed.
    """
    print("\n🔬 ALGORITHM COMPARISON MODE\n")

    # Load map once
    graph = load_map(PLACE)
    source, target = select_route(graph, MIN_DISTANCE, MAX_DISTANCE)

    configs = [
        (1.0, "A* (Optimal)"),
        (1.5, "Weighted A* (Balanced)"),
        (2.0, "Weighted A* (Fast)")
    ]

    results = []

    for weight, name in configs:
        print(f"\n{'='*70}")
        print(f"Running: {name}")
        print(f"{'='*70}\n")

        algo = AStarAlgorithm(heuristic_weight=weight)
        loop = AlgorithmGameLoop(
            graph, algo, source, target, name,
            create_fast_config()  # Use fast config for comparison
        )

        result = loop.run()
        if result:
            results.append((name, result))

        input("\nPress ENTER to continue to next algorithm...")

    # Show comparison
    print("\n" + "="*70)
    print("COMPARISON RESULTS")
    print("="*70 + "\n")

    print(f"{'Algorithm':<30} {'Path':<10} {'Distance':<12} {'Explored':<10} {'Time':<10}")
    print("-" * 70)

    for name, (path, dist, visited, time_ms) in results:
        print(f"{name:<30} {len(path):<10} {dist:<12.0f} {visited:<10} {time_ms:<10.2f}")

    print("\n" + "="*70 + "\n")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # To run comparison mode, uncomment the line below:
    # exit(compare_algorithms())

    # Default: single algorithm visualization
    exit(main())
