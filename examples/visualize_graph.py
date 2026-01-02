"""
Graph Visualization Example for WorldCar Phase 1

This script demonstrates how to visualize the road network and computed routes
using OSMnx's built-in plotting capabilities with matplotlib.

The script creates visualizations showing:
1. The complete road network
2. A specific route highlighted on the network
3. Saves the visualization as a PNG file
"""

import sys
from pathlib import Path

# Add parent directory to path to import worldcar
sys.path.insert(0, str(Path(__file__).parent.parent))

import osmnx as ox
import matplotlib.pyplot as plt

from worldcar.graph_loader import GraphLoader
from worldcar.node_mapper import NodeMapper
from worldcar.algorithms import Router
from worldcar.config import DEFAULT_LOCATION


def visualize_network(G, save_path="kadiköy_network.png"):
    """
    Visualize the complete road network.

    Args:
        G: NetworkX graph
        save_path: Path to save the visualization
    """
    print(f"\nVisualizing road network...")

    fig, ax = ox.plot_graph(
        G,
        node_size=0,
        edge_linewidth=0.5,
        edge_color='#333333',
        bgcolor='white',
        figsize=(12, 12),
        show=False,
        close=False,
    )

    plt.title(f"Road Network: {DEFAULT_LOCATION}", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Network visualization saved to: {save_path}")
    plt.close()


def visualize_route(G, route_path, save_path="kadiköy_route.png"):
    """
    Visualize a specific route on the road network.

    Args:
        G: NetworkX graph
        route_path: List of node IDs forming the route
        save_path: Path to save the visualization
    """
    print(f"\nVisualizing route with {len(route_path)} nodes...")

    fig, ax = ox.plot_graph_route(
        G,
        route_path,
        route_color='red',
        route_linewidth=4,
        route_alpha=0.7,
        node_size=0,
        edge_linewidth=0.5,
        edge_color='#333333',
        bgcolor='white',
        figsize=(12, 12),
        show=False,
        close=False,
    )

    plt.title(
        f"Shortest Path Route: {DEFAULT_LOCATION}",
        fontsize=16,
        fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Route visualization saved to: {save_path}")
    plt.close()


def visualize_multiple_routes(G, routes_info, save_path="kadiköy_routes.png"):
    """
    Visualize multiple routes on the same network.

    Args:
        G: NetworkX graph
        routes_info: List of dicts with 'path' and 'color' keys
        save_path: Path to save the visualization
    """
    print(f"\nVisualizing {len(routes_info)} routes...")

    # Plot base network
    fig, ax = ox.plot_graph(
        G,
        node_size=0,
        edge_linewidth=0.5,
        edge_color='#CCCCCC',
        bgcolor='white',
        figsize=(14, 14),
        show=False,
        close=False,
    )

    # Plot each route
    for i, route_info in enumerate(routes_info):
        route_path = route_info['path']
        color = route_info.get('color', f'C{i}')
        label = route_info.get('label', f'Route {i+1}')

        # Get route edges
        route_edges = [(route_path[j], route_path[j+1])
                       for j in range(len(route_path)-1)]

        # Plot route
        for u, v in route_edges:
            # Get edge geometry if available, otherwise straight line
            if 'geometry' in G[u][v][0]:
                # Handle MultiDiGraph
                x = [G.nodes[u]['x'], G.nodes[v]['x']]
                y = [G.nodes[u]['y'], G.nodes[v]['y']]
            else:
                x = [G.nodes[u]['x'], G.nodes[v]['x']]
                y = [G.nodes[u]['y'], G.nodes[v]['y']]

            ax.plot(x, y, color=color, linewidth=3, alpha=0.7, label=label if u == route_path[0] else "")

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        # Remove duplicate labels
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=10)

    plt.title(
        f"Multiple Routes: {DEFAULT_LOCATION}",
        fontsize=16,
        fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Multiple routes visualization saved to: {save_path}")
    plt.close()


def main():
    """Main visualization demonstration."""
    print("=" * 70)
    print("WorldCar - Graph Visualization Demo".center(70))
    print("=" * 70)

    # Load graph
    print(f"\n[1/4] Loading road network for {DEFAULT_LOCATION}...")
    print("-" * 70)

    loader = GraphLoader(DEFAULT_LOCATION)
    G = loader.get_or_create_graph()

    print(f"✓ Graph loaded: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    # Initialize mapper and router
    print(f"\n[2/4] Initializing router...")
    print("-" * 70)

    mapper = NodeMapper(G)
    router = Router(G, mapper)

    print(f"✓ Router initialized")

    # Visualize network
    print(f"\n[3/4] Creating network visualization...")
    print("-" * 70)

    visualize_network(G, "kadiköy_network.png")

    # Compute and visualize example route
    print(f"\n[4/4] Computing and visualizing example route...")
    print("-" * 70)

    # Example route: Moda to Fenerbahçe
    origin = (40.9856, 29.0298)  # Moda
    destination = (40.9638, 29.0408)  # Fenerbahçe

    print(f"Origin: {origin[0]:.6f}, {origin[1]:.6f} (Moda)")
    print(f"Destination: {destination[0]:.6f}, {destination[1]:.6f} (Fenerbahçe)")

    result = router.compute_shortest_path(
        origin[0], origin[1],
        destination[0], destination[1]
    )

    if result['success']:
        print(f"\n✓ Route computed successfully")
        print(f"  Distance: {result['distance']:.2f} meters")
        print(f"  Nodes: {len(result['path'])}")

        visualize_route(G, result['path'], "kadiköy_route.png")
    else:
        print(f"\n✗ Route computation failed: {result['message']}")

    # Compute multiple routes for comparison
    print(f"\n[Bonus] Creating multiple routes visualization...")
    print("-" * 70)

    routes = [
        {
            'name': 'Moda to Fenerbahçe',
            'origin': (40.9856, 29.0298),
            'destination': (40.9638, 29.0408),
            'color': 'red',
        },
        {
            'name': 'Kadıköy Square to Bağdat Avenue',
            'origin': (40.9904, 29.0255),
            'destination': (40.9780, 29.0450),
            'color': 'blue',
        },
    ]

    routes_info = []
    for route in routes:
        result = router.compute_shortest_path(
            route['origin'][0], route['origin'][1],
            route['destination'][0], route['destination'][1]
        )
        if result['success']:
            routes_info.append({
                'path': result['path'],
                'color': route['color'],
                'label': route['name'],
            })
            print(f"  ✓ {route['name']}: {result['distance']:.2f} m")

    if routes_info:
        visualize_multiple_routes(G, routes_info, "kadiköy_routes.png")

    # Summary
    print(f"\n{'='*70}")
    print("Visualization Complete!".center(70))
    print(f"{'='*70}")

    print(f"\nGenerated files:")
    print(f"  • kadiköy_network.png - Complete road network")
    print(f"  • kadiköy_route.png - Single route example")
    print(f"  • kadiköy_routes.png - Multiple routes comparison")

    print(f"\nNote: Visualizations are saved in the current directory.")
    print(f"      Open them with any image viewer.")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVisualization interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
