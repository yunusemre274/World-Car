"""
Side-by-side comparison visualization of exploration patterns:
- Dijkstra (uniform expansion)
- A* standard (directed search)
- Weighted A* (focused search)
"""

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import random
from math import radians, sin, cos, sqrt, atan2
from src.algorithms.dijkstra import DijkstraAlgorithm
from src.algorithms.astar import AStarAlgorithm


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


def get_visited_nodes_from_algorithm(algo, G, source, target):
    """
    Run algorithm and track visited nodes.
    Returns path, distance, visited set
    """
    # For tracking visited nodes, we need to instrument the algorithm
    # For now, we'll use the algorithm's run method and get visited count
    path, dist, visited_count, time_ms = algo.run(G, source, target)
    return path, dist, visited_count, time_ms


def compare_exploration():
    """
    Create side-by-side comparison of exploration patterns
    """
    print("Loading graph...")
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    # Use largest connected component
    largest_cc = max(nx.weakly_connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

    print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

    # Select nodes with reasonable distance (2-4 km for good visualization)
    nodes = list(G.nodes)
    pos = {n: (G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes}

    max_attempts = 100
    for attempt in range(max_attempts):
        source, target = random.sample(nodes, 2)
        pos_s = (G.nodes[source]["x"], G.nodes[source]["y"])
        pos_t = (G.nodes[target]["x"], G.nodes[target]["y"])
        straight_line_dist = haversine_distance(pos_s, pos_t)
        if 1500 < straight_line_dist < 3500:  # 1.5-3.5 km
            break

    print(f"\nRoute selected: {source} -> {target}")
    print(f"Straight-line distance: {straight_line_dist:.0f} meters")

    # Run all algorithms
    print("\nRunning algorithms...")
    dijkstra = DijkstraAlgorithm()
    astar_standard = AStarAlgorithm(heuristic_weight=1.0)
    astar_weighted = AStarAlgorithm(heuristic_weight=1.8)

    d_path, d_dist, d_visited, d_time = dijkstra.run(G, source, target)
    a_path, a_dist, a_visited, a_time = astar_standard.run(G, source, target)
    w_path, w_dist, w_visited, w_time = astar_weighted.run(G, source, target)

    print(f"  Dijkstra: {d_visited} nodes, {d_dist:.1f}m, {d_time:.2f}ms")
    print(f"  A* (w=1.0): {a_visited} nodes, {a_dist:.1f}m, {a_time:.2f}ms")
    print(f"  A* (w=1.8): {w_visited} nodes, {w_dist:.1f}m, {w_time:.2f}ms")

    # Create visualization
    print("\nCreating visualization...")
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    algorithms = [
        ("Dijkstra", d_path, d_visited, d_time, d_dist, "red"),
        ("A* (w=1.0)", a_path, a_visited, a_time, a_dist, "orange"),
        ("Weighted A* (w=1.8)", w_path, w_visited, w_time, w_dist, "yellowgreen")
    ]

    for idx, (name, path, visited, time_ms, dist, color) in enumerate(algorithms):
        ax = axes[idx]

        # Plot road network (light background)
        ox.plot_graph(G, ax=ax, show=False, close=False,
                     node_size=0, edge_color="#e0e0e0", edge_linewidth=0.5)

        # Plot path
        if len(path) > 1:
            path_coords = [(pos[node][0], pos[node][1]) for node in path]
            path_x, path_y = zip(*path_coords)
            ax.plot(path_x, path_y, color='blue', linewidth=3, alpha=0.8, zorder=3)

        # Plot source and target
        ax.scatter(pos[source][0], pos[source][1],
                  c='blue', s=200, marker='o', edgecolors='white', linewidths=2,
                  label='Source', zorder=5)
        ax.scatter(pos[target][0], pos[target][1],
                  c='green', s=300, marker='*', edgecolors='white', linewidths=2,
                  label='Target', zorder=5)

        # Title and metrics
        reduction = ((d_visited - visited) / d_visited) * 100 if idx > 0 else 0
        speedup = d_time / time_ms if idx > 0 and time_ms > 0 else 1.0
        quality = (dist / d_dist) * 100 if idx > 0 else 100.0

        title = f"{name}\n"
        title += f"Visited: {visited} nodes"
        if idx > 0:
            title += f" ({reduction:.1f}% reduction)\n"
            title += f"Speedup: {speedup:.2f}x | Quality: {quality:.1f}%"
        else:
            title += f"\nDistance: {dist:.1f}m | Time: {time_ms:.2f}ms"

        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.legend(loc='upper right')

    # Overall title
    fig.suptitle(f'Exploration Pattern Comparison\nRoute: {straight_line_dist:.0f}m straight-line distance',
                 fontsize=14, fontweight='bold')

    plt.tight_layout()

    # Save
    output_file = "comparison_exploration.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_file}")

    # Show
    plt.show()


if __name__ == "__main__":
    compare_exploration()
