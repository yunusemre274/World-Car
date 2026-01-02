"""
Basic Routing Example for WorldCar Phase 1

This script demonstrates the core functionality of the WorldCar routing system:
1. Loading a road network from OpenStreetMap
2. Displaying network statistics
3. Computing shortest paths between coordinates
4. Extracting and displaying route information

Example routes use landmarks in Kadıköy, Istanbul.
"""

import sys
from pathlib import Path

# Add parent directory to path to import worldcar
sys.path.insert(0, str(Path(__file__).parent.parent))

from worldcar.graph_loader import GraphLoader
from worldcar.node_mapper import NodeMapper
from worldcar.algorithms import Router
from worldcar.statistics import print_graph_summary, compute_graph_statistics
from worldcar.config import DEFAULT_LOCATION
from worldcar.utils import format_distance


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("WorldCar - Graph-Based Routing System (Phase 1 Demo)".center(70))
    print("=" * 70)

    # ========================================================================
    # Step 1: Load Road Network
    # ========================================================================
    print(f"\n[1/5] Loading road network for {DEFAULT_LOCATION}...")
    print("-" * 70)

    loader = GraphLoader(DEFAULT_LOCATION)
    G = loader.get_or_create_graph()

    print(f"✓ Graph loaded successfully!")
    print(f"  Nodes: {G.number_of_nodes():,}")
    print(f"  Edges: {G.number_of_edges():,}")

    # ========================================================================
    # Step 2: Display Network Statistics
    # ========================================================================
    print(f"\n[2/5] Computing network statistics...")
    print("-" * 70)

    stats = compute_graph_statistics(G)
    print_graph_summary(G)

    # ========================================================================
    # Step 3: Initialize Mapper and Router
    # ========================================================================
    print(f"\n[3/5] Initializing coordinate mapper and router...")
    print("-" * 70)

    mapper = NodeMapper(G)
    router = Router(G, mapper)

    print(f"✓ NodeMapper initialized with KDTree")
    print(f"✓ Router ready for shortest path computation")

    # ========================================================================
    # Step 4: Example Routes in Kadıköy
    # ========================================================================
    print(f"\n[4/5] Computing example routes...")
    print("-" * 70)

    # Define example routes with Kadıköy landmarks
    routes = [
        {
            'name': 'Moda to Fenerbahçe',
            'origin': (40.9856, 29.0298),  # Moda neighborhood
            'destination': (40.9638, 29.0408),  # Fenerbahçe Park
        },
        {
            'name': 'Kadıköy Square to Bağdat Avenue',
            'origin': (40.9904, 29.0255),  # Kadıköy Square (center)
            'destination': (40.9780, 29.0450),  # Bağdat Avenue
        },
        {
            'name': 'Kadıköy Ferry Terminal to Altıyol',
            'origin': (40.9928, 29.0254),  # Ferry terminal
            'destination': (40.9850, 29.0350),  # Altıyol intersection
        },
    ]

    for i, route_info in enumerate(routes, 1):
        print(f"\nRoute {i}: {route_info['name']}")
        print("-" * 40)

        origin = route_info['origin']
        destination = route_info['destination']

        print(f"Origin: {origin[0]:.6f}, {origin[1]:.6f}")
        print(f"Destination: {destination[0]:.6f}, {destination[1]:.6f}")

        # Compute route
        result = router.compute_shortest_path(
            origin[0], origin[1],
            destination[0], destination[1]
        )

        if result['success']:
            print(f"\n✓ Route found!")
            print(f"  Distance: {format_distance(result['distance'])}")
            print(f"  Number of nodes: {len(result['path'])}")
            print(f"  Origin node: {result['origin_node']}")
            print(f"  Destination node: {result['dest_node']}")
            print(f"  Computation time: {result['computation_time']*1000:.2f} ms")

            # Show first few waypoints
            print(f"\n  First 5 waypoints:")
            for j, (lat, lon) in enumerate(result['nodes'][:5], 1):
                print(f"    {j}. ({lat:.6f}, {lon:.6f})")

            if len(result['nodes']) > 5:
                print(f"    ... and {len(result['nodes']) - 5} more waypoints")
        else:
            print(f"\n✗ Route failed: {result['message']}")

    # ========================================================================
    # Step 5: Summary
    # ========================================================================
    print(f"\n[5/5] Summary")
    print("=" * 70)

    print(f"\n✓ Phase 1 Implementation Complete!")
    print(f"\nKey Features Demonstrated:")
    print(f"  • OSM road network loading and caching")
    print(f"  • Graph statistics and analysis")
    print(f"  • Coordinate-to-node mapping with KDTree")
    print(f"  • Dijkstra shortest path routing")
    print(f"  • Route distance and waypoint extraction")

    print(f"\nNetwork Information:")
    print(f"  Location: {DEFAULT_LOCATION}")
    print(f"  Nodes: {stats['num_nodes']:,} intersections")
    print(f"  Edges: {stats['num_edges']:,} road segments")
    print(f"  Total Length: {stats['total_length_km']:.2f} km")
    print(f"  Connected Components: {stats['num_connected_components']}")

    print(f"\nNext Steps (Future Phases):")
    print(f"  • Phase 2: Multiple algorithms (A*, Bellman-Ford) with metrics")
    print(f"  • Phase 3: Traffic simulation and dynamic weights")
    print(f"  • Phase 4: RESTful API backend")
    print(f"  • Phase 5: Interactive map-based frontend")

    print("\n" + "=" * 70)
    print("Demo Complete!".center(70))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
