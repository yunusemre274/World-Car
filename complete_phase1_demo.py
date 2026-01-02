"""
Complete Phase 1 Demo - End-to-End Routing System

Demonstrates the complete Phase 1 workflow:
1. Load city road network from OpenStreetMap
2. Map user coordinates to graph nodes
3. Compute shortest path using Dijkstra's algorithm
4. Display route information

This shows all three Phase 1 modules working together:
- graph_loader_standalone.py
- node_mapper_standalone.py
- path_service_standalone.py

Run: python complete_phase1_demo.py
"""

from graph_loader_standalone import load_city_graph, get_graph_stats
from node_mapper_standalone import find_nearest_node, get_node_coordinates, validate_coordinates
from path_service_standalone import compute_shortest_path, has_path


def format_distance(meters: float) -> str:
    """Format distance in meters to human-readable string."""
    if meters < 1000:
        return f"{meters:.2f} m"
    else:
        return f"{meters/1000:.2f} km"


def main():
    """Main demonstration of complete Phase 1 routing system."""
    print("\n" + "=" * 70)
    print("PHASE 1 COMPLETE DEMO - End-to-End Routing".center(70))
    print("=" * 70 + "\n")

    # ========================================================================
    # STEP 1: Load Road Network
    # ========================================================================
    print("STEP 1: Load Road Network")
    print("-" * 70)

    city = "Kadıköy, Istanbul, Turkey"
    print(f"City: {city}")
    print("Loading road network from OpenStreetMap...")
    print("(First download may take 15-30 seconds)\n")

    graph = load_city_graph(city)
    stats = get_graph_stats(graph)

    print("✓ Graph loaded successfully!")
    print(f"  Nodes: {stats['num_nodes']:,} intersections")
    print(f"  Edges: {stats['num_edges']:,} road segments")
    print(f"  Type: {stats['graph_type']}")
    print()

    # ========================================================================
    # STEP 2: Define Route (User Input Simulation)
    # ========================================================================
    print("STEP 2: Define Route")
    print("-" * 70)

    # Example routes in Kadıköy
    routes = [
        {
            'name': 'Moda to Fenerbahçe Park',
            'start': (40.9856, 29.0298),
            'end': (40.9638, 29.0408),
            'description': 'From Moda neighborhood to Fenerbahçe waterfront'
        },
        {
            'name': 'Kadıköy Square to Bağdat Avenue',
            'start': (40.9904, 29.0255),
            'end': (40.9780, 29.0450),
            'description': 'From city center to famous shopping street'
        },
        {
            'name': 'Short Route (Ferry Terminal to Altıyol)',
            'start': (40.9928, 29.0254),
            'end': (40.9850, 29.0350),
            'description': 'Short route through central Kadıköy'
        }
    ]

    for i, route in enumerate(routes, 1):
        print(f"\n{i}. {route['name']}")
        print(f"   {route['description']}")
        print(f"   Start: {route['start']}")
        print(f"   End:   {route['end']}")

    print()

    # ========================================================================
    # STEP 3: Process Each Route
    # ========================================================================
    print("STEP 3: Compute Routes")
    print("-" * 70 + "\n")

    for route_num, route in enumerate(routes, 1):
        print(f"{'─' * 70}")
        print(f"ROUTE {route_num}: {route['name']}")
        print(f"{'─' * 70}")

        start_lat, start_lon = route['start']
        end_lat, end_lon = route['end']

        # Validate coordinates
        print("\n1. Validating coordinates...")
        try:
            validate_coordinates(start_lat, start_lon)
            validate_coordinates(end_lat, end_lon)
            print("   ✓ All coordinates valid")
        except ValueError as e:
            print(f"   ✗ Invalid coordinates: {e}")
            continue

        # Map to nodes
        print("\n2. Mapping coordinates to road network...")
        start_node = find_nearest_node(graph, start_lat, start_lon)
        end_node = find_nearest_node(graph, end_lat, end_lon)

        print(f"   Start → Node {start_node}")
        print(f"   End   → Node {end_node}")

        # Get actual node coordinates
        start_node_coords = get_node_coordinates(graph, start_node)
        end_node_coords = get_node_coordinates(graph, end_node)

        print(f"   Start node at: ({start_node_coords[0]:.6f}, {start_node_coords[1]:.6f})")
        print(f"   End node at:   ({end_node_coords[0]:.6f}, {end_node_coords[1]:.6f})")

        # Check if path exists
        print("\n3. Checking path existence...")
        if not has_path(graph, start_node, end_node):
            print("   ✗ No path exists (disconnected network components)")
            continue
        print("   ✓ Path exists")

        # Compute shortest path
        print("\n4. Computing shortest path (Dijkstra's algorithm)...")
        result = compute_shortest_path(graph, start_node, end_node)

        if result['success']:
            print("   ✓ Path found!\n")

            # Display results
            print("   " + "=" * 66)
            print("   ROUTE DETAILS".center(66))
            print("   " + "=" * 66)
            print(f"   Total Distance:     {format_distance(result['path_length_m'])}")
            print(f"   Number of Nodes:    {result['num_nodes']}")
            print(f"   Start Node:         {result['start_node']}")
            print(f"   End Node:           {result['end_node']}")

            # Show first few waypoints
            print(f"\n   First 5 waypoints (node IDs):")
            for i, node_id in enumerate(result['node_ids'][:5], 1):
                coords = get_node_coordinates(graph, node_id)
                print(f"      {i}. Node {node_id:10} at ({coords[0]:.6f}, {coords[1]:.6f})")

            if result['num_nodes'] > 5:
                print(f"      ... and {result['num_nodes'] - 5} more waypoints")

            print("   " + "=" * 66)
        else:
            print(f"   ✗ Route failed: {result['message']}")

        print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("PHASE 1 DEMO COMPLETE".center(70))
    print("=" * 70)

    print("\n✓ Successfully Demonstrated:")
    print("  1. Loading road network from OpenStreetMap (graph_loader)")
    print("  2. Mapping lat/lon coordinates to graph nodes (node_mapper)")
    print("  3. Computing shortest paths with Dijkstra (path_service)")
    print("  4. Handling various route scenarios")

    print("\nPhase 1 Modules:")
    print(f"  • graph_loader_standalone.py - {stats['num_nodes']:,} nodes loaded")
    print("  • node_mapper_standalone.py  - Coordinate mapping with validation")
    print("  • path_service_standalone.py - Dijkstra shortest path algorithm")

    print("\nWhat Phase 1 Provides:")
    print("  ✓ Real-world road network data")
    print("  ✓ Graph-based road representation")
    print("  ✓ Coordinate-to-node mapping")
    print("  ✓ Shortest path computation")
    print("  ✓ Distance calculations in meters")

    print("\nReady for Future Phases:")
    print("  → Phase 2: Multiple algorithms (A*, Bellman-Ford)")
    print("  → Phase 3: Traffic simulation & dynamic weights")
    print("  → Phase 4: REST API backend")
    print("  → Phase 5: Interactive web frontend")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
