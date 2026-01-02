"""
Phase 1 Example - Graph Loading and Node Mapping

Demonstrates the core Phase 1 functionality:
1. Load a city's road network
2. Map coordinates to graph nodes
3. Display basic information

Run: python example_phase1.py
"""

from graph_loader_standalone import load_city_graph, get_graph_stats
from node_mapper_standalone import (
    find_nearest_node,
    get_node_coordinates,
    validate_coordinates,
    batch_find_nearest_nodes
)


def main():
    """Main demonstration function."""
    print("\n" + "=" * 70)
    print("PHASE 1 DEMO - Graph Loading & Node Mapping".center(70))
    print("=" * 70 + "\n")

    # Step 1: Load road network
    print("STEP 1: Load Road Network")
    print("-" * 70)

    city = "Kadıköy, Istanbul, Turkey"
    print(f"Loading: {city}")
    print("(First download takes ~20 seconds...)\n")

    graph = load_city_graph(city)
    stats = get_graph_stats(graph)

    print(f"✓ Loaded successfully!")
    print(f"  Nodes: {stats['num_nodes']:,} intersections")
    print(f"  Edges: {stats['num_edges']:,} road segments")
    print()

    # Step 2: Find nearest nodes to coordinates
    print("STEP 2: Map Coordinates to Graph Nodes")
    print("-" * 70)

    # Test coordinates in Kadıköy
    locations = [
        ("Moda Neighborhood", 40.9856, 29.0298),
        ("Fenerbahçe Park", 40.9638, 29.0408),
        ("Kadıköy Square", 40.9904, 29.0255),
    ]

    print(f"Testing {len(locations)} locations:\n")

    for name, lat, lon in locations:
        # Validate coordinates
        try:
            validate_coordinates(lat, lon)
        except ValueError as e:
            print(f"✗ {name}: Invalid coordinates - {e}")
            continue

        # Find nearest node
        node_id = find_nearest_node(graph, lat, lon)
        node_lat, node_lon = get_node_coordinates(graph, node_id)

        # Calculate distance to node
        import math
        R = 6371000  # Earth radius in meters
        dlat = math.radians(node_lat - lat)
        dlon = math.radians(node_lon - lon)
        a = (math.sin(dlat/2)**2 +
             math.cos(math.radians(lat)) * math.cos(math.radians(node_lat)) *
             math.sin(dlon/2)**2)
        distance = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        print(f"✓ {name}")
        print(f"  Query:      ({lat}, {lon})")
        print(f"  Node ID:    {node_id}")
        print(f"  Node at:    ({node_lat:.6f}, {node_lon:.6f})")
        print(f"  Distance:   {distance:.2f} meters")
        print()

    # Step 3: Batch processing
    print("STEP 3: Batch Node Lookup")
    print("-" * 70)

    coords_batch = [(lat, lon) for _, lat, lon in locations]
    print(f"Finding nearest nodes for {len(coords_batch)} coordinates...")

    node_ids = batch_find_nearest_nodes(graph, coords_batch)

    print(f"✓ Found {len(node_ids)} nodes:")
    for i, (name, _, _) in enumerate(locations):
        print(f"  {i+1}. {name}: Node {node_ids[i]}")
    print()

    # Step 4: Error handling demonstration
    print("STEP 4: Error Handling")
    print("-" * 70)

    invalid_tests = [
        ("Latitude too high", 91.0, 29.0),
        ("Longitude too low", 40.0, -181.0),
        ("NaN latitude", float('nan'), 29.0),
    ]

    print("Testing invalid coordinates:\n")
    for description, lat, lon in invalid_tests:
        try:
            validate_coordinates(lat, lon)
            print(f"  ✗ {description}: Should have failed!")
        except ValueError as e:
            print(f"  ✓ {description}: Caught error")
            print(f"    → {str(e)[:60]}...")

    print("\n" + "=" * 70)
    print("✓ PHASE 1 DEMO COMPLETE".center(70))
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  1. Load city road network from OpenStreetMap")
    print("  2. Map lat/lon coordinates to graph nodes")
    print("  3. Validate coordinate ranges")
    print("  4. Batch process multiple coordinates")
    print("  5. Handle errors with clear exceptions")
    print("\nReady for Phase 2: Routing algorithms!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
