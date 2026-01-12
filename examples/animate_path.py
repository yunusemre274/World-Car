"""
Example: Smooth car animation on computed path.

Demonstrates how to add smooth car animation to an existing
pathfinding visualization using the animation module.

Usage:
    python examples/animate_path.py

This example shows:
1. Loading a map from OSMnx
2. Computing a path with A* or Dijkstra
3. Visualizing the road network
4. Animating a car smoothly along the path
5. Optional camera follow effect
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random

from src.algorithms.astar import AStarAlgorithm
from src.algorithms.dijkstra import DijkstraAlgorithm
from src.animation import (
    AnimationController,
    InterpolationMethod,
    CameraMode
)


def load_map(place_name: str = "Moda, Kadıköy, Istanbul, Turkey"):
    """Load road network from OpenStreetMap."""
    print(f"Loading map: {place_name}")
    graph = ox.graph_from_place(place_name, network_type="drive")

    # Use largest connected component
    largest_cc = max(nx.weakly_connected_components(graph), key=len)
    graph = graph.subgraph(largest_cc).copy()

    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    return graph


def select_random_route(graph, min_distance: float = 1000, max_distance: float = 3000):
    """Select random source and target nodes."""
    from math import radians, sin, cos, sqrt, atan2

    def haversine(node1, node2):
        lon1, lat1 = graph.nodes[node1]['x'], graph.nodes[node1]['y']
        lon2, lat2 = graph.nodes[node2]['x'], graph.nodes[node2]['y']
        R = 6371000
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlambda = radians(lon2 - lon1)
        h = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
        return 2 * R * atan2(sqrt(h), sqrt(1 - h))

    nodes = list(graph.nodes)
    for _ in range(100):
        source, target = random.sample(nodes, 2)
        dist = haversine(source, target)
        if min_distance <= dist <= max_distance:
            print(f"  Source: {source}")
            print(f"  Target: {target}")
            print(f"  Straight-line distance: {dist:.0f}m")
            return source, target

    return nodes[0], nodes[len(nodes)//2]


def compute_path(graph, source, target, algorithm='astar'):
    """Compute shortest path."""
    print(f"\nComputing path using {algorithm.upper()}...")

    if algorithm == 'astar':
        algo = AStarAlgorithm(heuristic_weight=1.5)
        name = "Weighted A*"
    else:
        algo = DijkstraAlgorithm()
        name = "Dijkstra"

    path, distance, visited, time_ms = algo.run(graph, source, target)

    print(f"  Path: {len(path)} nodes")
    print(f"  Distance: {distance:.0f}m")
    print(f"  Explored: {visited} nodes")
    print(f"  Time: {time_ms:.2f}ms")

    return path, distance, name


def visualize_static(ax, graph, path):
    """Draw static map with path (no animation)."""
    # Draw road network
    ox.plot_graph(
        graph, ax=ax, show=False, close=False,
        node_size=0, edge_color='#e8e8e8', edge_linewidth=0.5
    )

    # Draw path
    if len(path) > 1:
        path_coords = [(graph.nodes[node]['x'], graph.nodes[node]['y'])
                      for node in path]
        path_x, path_y = zip(*path_coords)
        ax.plot(path_x, path_y, color='#4a90e2', linewidth=2.5,
               alpha=0.6, zorder=2, label='Path')

    # Draw start and end
    start_pos = (graph.nodes[path[0]]['x'], graph.nodes[path[0]]['y'])
    end_pos = (graph.nodes[path[-1]]['x'], graph.nodes[path[-1]]['y'])

    ax.scatter(*start_pos, c='green', s=200, marker='o',
              edgecolors='white', linewidths=2, zorder=4, label='Start')
    ax.scatter(*end_pos, c='orange', s=250, marker='*',
              edgecolors='white', linewidths=2, zorder=4, label='End')

    ax.legend(loc='upper right', fontsize=10)
    ax.set_title('Pathfinding with Smooth Car Animation',
                fontsize=14, fontweight='bold')


def example_basic_animation():
    """
    Example 1: Basic animation with default settings.

    Simple car animation on computed path.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: BASIC ANIMATION")
    print("="*60)

    # Load map
    graph = load_map()

    # Select route
    source, target = select_random_route(graph)

    # Compute path
    path, distance, algo_name = compute_path(graph, source, target, 'astar')

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Draw static elements
    visualize_static(ax, graph, path)

    # Create animation controller
    print("\nSetting up animation...")
    controller = AnimationController(
        ax=ax,
        graph=graph,
        path=path,
        steps_per_edge=30,              # Smooth interpolation
        car_color='red',                 # Red car
        car_size=150,                    # Car size
        show_trail=False,                # No trail
        camera_mode=CameraMode.STATIC    # Static camera
    )

    # Animate
    anim = controller.animate(interval=50)  # 50ms per frame = ~20 FPS

    print("\nAnimation ready! Close window to continue...")
    plt.show()

    return anim  # Keep reference


def example_with_trail():
    """
    Example 2: Animation with trail effect.

    Car leaves a trail showing where it has been.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: ANIMATION WITH TRAIL")
    print("="*60)

    graph = load_map()
    source, target = select_random_route(graph)
    path, distance, algo_name = compute_path(graph, source, target)

    fig, ax = plt.subplots(figsize=(12, 10))
    visualize_static(ax, graph, path)

    print("\nSetting up animation with trail...")
    controller = AnimationController(
        ax=ax,
        graph=graph,
        path=path,
        steps_per_edge=30,
        car_color='#ff4444',
        car_size=150,
        show_trail=True,          # Enable trail
        trail_length=40,          # Length of trail
        camera_mode=CameraMode.STATIC
    )

    anim = controller.animate(interval=50)

    print("\nAnimation with trail ready!")
    plt.show()

    return anim


def example_camera_follow():
    """
    Example 3: Animation with camera follow.

    Camera smoothly follows the car as it moves.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: CAMERA FOLLOW")
    print("="*60)

    graph = load_map()
    source, target = select_random_route(graph, min_distance=2000, max_distance=4000)
    path, distance, algo_name = compute_path(graph, source, target)

    fig, ax = plt.subplots(figsize=(12, 10))
    visualize_static(ax, graph, path)

    print("\nSetting up animation with camera follow...")
    controller = AnimationController(
        ax=ax,
        graph=graph,
        path=path,
        steps_per_edge=40,                    # More steps for longer path
        car_color='#ff4444',
        car_size=200,                         # Larger car
        show_trail=True,
        trail_length=50,
        camera_mode=CameraMode.FOLLOW_SMOOTH, # Smooth camera follow
        camera_smoothing=0.2                  # Smoothing factor
    )

    anim = controller.animate(interval=40)  # Slightly faster

    print("\nCamera will follow the car!")
    print("Note: Camera follow works best with longer paths.")
    plt.show()

    return anim


def example_fast_animation():
    """
    Example 4: Fast animation with linear interpolation.

    Fast-paced animation for quick visualization.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: FAST ANIMATION")
    print("="*60)

    graph = load_map()
    source, target = select_random_route(graph)
    path, distance, algo_name = compute_path(graph, source, target)

    fig, ax = plt.subplots(figsize=(12, 10))
    visualize_static(ax, graph, path)

    print("\nSetting up fast animation...")
    controller = AnimationController(
        ax=ax,
        graph=graph,
        path=path,
        steps_per_edge=15,        # Fewer steps = faster
        interpolation_method=InterpolationMethod.LINEAR,
        car_color='yellow',
        car_size=180,
        show_trail=True,
        trail_length=25,
        camera_mode=CameraMode.STATIC
    )

    anim = controller.animate(interval=20)  # 20ms per frame = 50 FPS

    print("\nFast animation ready!")
    plt.show()

    return anim


def example_custom_styling():
    """
    Example 5: Custom visual styling.

    Demonstrates customization options.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: CUSTOM STYLING")
    print("="*60)

    graph = load_map()
    source, target = select_random_route(graph)
    path, distance, algo_name = compute_path(graph, source, target)

    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#1a1a1a')
    ax.set_facecolor('#1a1a1a')

    # Draw road network in light color
    ox.plot_graph(
        graph, ax=ax, show=False, close=False,
        node_size=0, edge_color='#444444', edge_linewidth=0.5
    )

    # Draw path in bright color
    path_coords = [(graph.nodes[node]['x'], graph.nodes[node]['y'])
                  for node in path]
    path_x, path_y = zip(*path_coords)
    ax.plot(path_x, path_y, color='#00ffff', linewidth=3,
           alpha=0.7, zorder=2, label='Path')

    # Neon-style markers
    start_pos = (graph.nodes[path[0]]['x'], graph.nodes[path[0]]['y'])
    end_pos = (graph.nodes[path[-1]]['x'], graph.nodes[path[-1]]['y'])
    ax.scatter(*start_pos, c='#00ff00', s=200, marker='o',
              edgecolors='white', linewidths=2, zorder=4, label='Start')
    ax.scatter(*end_pos, c='#ff00ff', s=250, marker='*',
              edgecolors='white', linewidths=2, zorder=4, label='End')

    ax.legend(loc='upper right', fontsize=10, facecolor='#2a2a2a',
             edgecolor='white', labelcolor='white')
    ax.set_title('Neon-Style Pathfinding Animation',
                fontsize=14, fontweight='bold', color='white')

    print("\nSetting up custom-styled animation...")
    controller = AnimationController(
        ax=ax,
        graph=graph,
        path=path,
        steps_per_edge=30,
        car_color='#ff00ff',      # Neon pink car
        car_size=200,
        show_trail=True,
        trail_length=30,
        camera_mode=CameraMode.STATIC
    )

    anim = controller.animate(interval=50)

    print("\nNeon-style animation ready!")
    plt.show()

    return anim


def main():
    """
    Main entry point - run examples.
    """
    print("\n" + "="*70)
    print(" "*15 + "WORLDCAR - SMOOTH CAR ANIMATION EXAMPLES")
    print("="*70)

    print("\nSelect an example:")
    print("1. Basic Animation (simple)")
    print("2. Animation with Trail")
    print("3. Camera Follow (cinematic)")
    print("4. Fast Animation")
    print("5. Custom Styling (neon theme)")
    print("0. Run all examples sequentially")

    try:
        choice = input("\nEnter choice (0-5): ").strip()

        examples = {
            '1': example_basic_animation,
            '2': example_with_trail,
            '3': example_camera_follow,
            '4': example_fast_animation,
            '5': example_custom_styling
        }

        if choice == '0':
            # Run all
            for key in sorted(examples.keys()):
                examples[key]()
        elif choice in examples:
            examples[choice]()
        else:
            print("Invalid choice. Running basic example...")
            example_basic_animation()

    except KeyboardInterrupt:
        print("\nExiting...")
        return 1

    print("\nAll examples complete!")
    return 0


if __name__ == "__main__":
    exit(main())
