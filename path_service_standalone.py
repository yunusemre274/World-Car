"""
Path Service - Phase 1 Shortest Path Computation

Computes shortest paths on road network graphs using Dijkstra's algorithm
via NetworkX. Uses edge length (meters) as the weight.

Requirements:
- Python 3.10+
- networkx>=3.2

Usage:
    from path_service import compute_shortest_path

    result = compute_shortest_path(graph, start_node, end_node)
    print(f"Path: {result['node_ids']}")
    print(f"Length: {result['path_length_m']} meters")
"""

from typing import Dict, Any, List
import logging

import networkx as nx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_shortest_path(
    graph: nx.MultiDiGraph,
    start_node: int,
    end_node: int,
    weight: str = "length"
) -> Dict[str, Any]:
    """
    Compute shortest path between two nodes using Dijkstra's algorithm.

    Uses NetworkX's shortest_path function with Dijkstra's algorithm to find
    the optimal route between two intersections in a road network. The path
    is weighted by edge length in meters.

    Args:
        graph: NetworkX MultiDiGraph road network
        start_node: Starting node ID
        end_node: Ending node ID
        weight: Edge attribute to use as weight (default: "length")

    Returns:
        Dictionary containing:
        {
            'success': bool,              # True if path found, False otherwise
            'node_ids': List[int],        # List of node IDs in path (empty if no path)
            'path_length_m': float,       # Total path length in meters (0.0 if no path)
            'num_nodes': int,             # Number of nodes in path (0 if no path)
            'start_node': int,            # Starting node ID
            'end_node': int,              # Ending node ID
            'message': str                # Success/error message
        }

    Example:
        >>> result = compute_shortest_path(graph, 298734512, 298734678)
        >>> if result['success']:
        ...     print(f"Path length: {result['path_length_m']:.2f} meters")
        ...     print(f"Path has {result['num_nodes']} nodes")
        Path length: 2534.50 meters
        Path has 45 nodes
    """
    # Validate graph
    if not isinstance(graph, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
        raise TypeError(f"Expected NetworkX graph, got {type(graph).__name__}")

    if graph.number_of_nodes() == 0:
        raise RuntimeError("Cannot compute path on empty graph")

    # Validate nodes exist
    if start_node not in graph:
        raise ValueError(
            f"Start node {start_node} not found in graph. "
            f"Graph has {graph.number_of_nodes()} nodes."
        )

    if end_node not in graph:
        raise ValueError(
            f"End node {end_node} not found in graph. "
            f"Graph has {graph.number_of_nodes()} nodes."
        )

    # Check if start and end are the same
    if start_node == end_node:
        logger.warning(f"Start and end nodes are the same: {start_node}")
        return {
            'success': True,
            'node_ids': [start_node],
            'path_length_m': 0.0,
            'num_nodes': 1,
            'start_node': start_node,
            'end_node': end_node,
            'message': 'Start and end nodes are identical'
        }

    try:
        # Compute shortest path using Dijkstra's algorithm
        # NetworkX uses Dijkstra by default for shortest_path with weights
        path = nx.shortest_path(
            graph,
            source=start_node,
            target=end_node,
            weight=weight,
            method='dijkstra'
        )

        # Calculate total path length
        path_length = calculate_path_length(graph, path, weight)

        logger.info(
            f"Found path from {start_node} to {end_node}: "
            f"{len(path)} nodes, {path_length:.2f}m"
        )

        return {
            'success': True,
            'node_ids': path,
            'path_length_m': path_length,
            'num_nodes': len(path),
            'start_node': start_node,
            'end_node': end_node,
            'message': f'Path found: {len(path)} nodes, {path_length:.2f} meters'
        }

    except nx.NetworkXNoPath:
        # No path exists between the nodes (disconnected components)
        logger.warning(
            f"No path exists from {start_node} to {end_node}. "
            f"Nodes may be in disconnected components."
        )

        return {
            'success': False,
            'node_ids': [],
            'path_length_m': 0.0,
            'num_nodes': 0,
            'start_node': start_node,
            'end_node': end_node,
            'message': (
                f'No path exists between nodes {start_node} and {end_node}. '
                f'They may be in disconnected components of the graph.'
            )
        }

    except nx.NodeNotFound as e:
        # This shouldn't happen due to validation above, but handle it
        error_msg = f"Node not found: {str(e)}"
        logger.error(error_msg)

        return {
            'success': False,
            'node_ids': [],
            'path_length_m': 0.0,
            'num_nodes': 0,
            'start_node': start_node,
            'end_node': end_node,
            'message': error_msg
        }

    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Error computing path: {str(e)}"
        logger.error(error_msg)

        return {
            'success': False,
            'node_ids': [],
            'path_length_m': 0.0,
            'num_nodes': 0,
            'start_node': start_node,
            'end_node': end_node,
            'message': error_msg
        }


def calculate_path_length(
    graph: nx.MultiDiGraph,
    path: List[int],
    weight: str = "length"
) -> float:
    """
    Calculate total length of a path by summing edge weights.

    Iterates through consecutive node pairs in the path and sums their
    edge weights. For MultiDiGraphs with multiple edges between nodes,
    uses the edge with minimum weight.

    Args:
        graph: NetworkX MultiDiGraph road network
        path: List of node IDs forming the path
        weight: Edge attribute to use as weight (default: "length")

    Returns:
        Total path length in the units of the weight attribute (meters)

    Example:
        >>> path = [1, 2, 3, 4]
        >>> length = calculate_path_length(graph, path)
        >>> print(f"Path length: {length:.2f} meters")
        Path length: 2534.50 meters
    """
    if len(path) < 2:
        return 0.0

    total_length = 0.0

    # Iterate through consecutive node pairs
    for i in range(len(path) - 1):
        start = path[i]
        end = path[i + 1]

        # Get edge data
        if graph.is_multigraph():
            # For multigraphs, there may be multiple edges between nodes
            # Use the edge with minimum weight (same as Dijkstra's choice)
            edge_data = graph[start][end]
            min_weight = min(
                data.get(weight, float('inf'))
                for data in edge_data.values()
            )
            total_length += min_weight
        else:
            # For regular graphs, there's only one edge
            edge_data = graph[start][end]
            total_length += edge_data.get(weight, 0.0)

    return total_length


def has_path(graph: nx.MultiDiGraph, start_node: int, end_node: int) -> bool:
    """
    Check if a path exists between two nodes.

    Quick check without computing the actual path. Useful for validating
    whether two nodes are in the same connected component.

    Args:
        graph: NetworkX MultiDiGraph road network
        start_node: Starting node ID
        end_node: Ending node ID

    Returns:
        True if a path exists, False otherwise

    Example:
        >>> if has_path(graph, start_node, end_node):
        ...     result = compute_shortest_path(graph, start_node, end_node)
    """
    try:
        return nx.has_path(graph, start_node, end_node)
    except (nx.NodeNotFound, nx.NetworkXError):
        return False


# ============================================================================
# Main - Demo/Test
# ============================================================================

def main():
    """
    Demo function showing path service usage.
    Run: python path_service_standalone.py
    """
    print("\n" + "=" * 70)
    print("PATH SERVICE - PHASE 1 DEMO".center(70))
    print("=" * 70 + "\n")

    # Load graph and find nodes
    try:
        from graph_loader_standalone import load_city_graph
        from node_mapper_standalone import find_nearest_node
    except ImportError:
        print("Error: Required modules not found.")
        print("Please ensure graph_loader_standalone.py and node_mapper_standalone.py")
        print("are in the same directory.")
        return

    city = "Kadıköy, Istanbul, Turkey"
    print(f"Loading road network for: {city}")
    print("(This may take 15-30 seconds on first download...)\n")

    try:
        graph = load_city_graph(city)
        print("✓ Graph loaded successfully\n")

        # Test locations in Kadıköy
        print("-" * 70)
        print("TEST 1: Compute Shortest Path")
        print("-" * 70)

        # Find nodes for test coordinates
        start_lat, start_lon = 40.9856, 29.0298  # Moda
        end_lat, end_lon = 40.9638, 29.0408      # Fenerbahçe

        print(f"Start: ({start_lat}, {start_lon}) - Moda")
        print(f"End:   ({end_lat}, {end_lon}) - Fenerbahçe\n")

        start_node = find_nearest_node(graph, start_lat, start_lon)
        end_node = find_nearest_node(graph, end_lat, end_lon)

        print(f"Start node ID: {start_node}")
        print(f"End node ID:   {end_node}\n")

        # Compute shortest path
        result = compute_shortest_path(graph, start_node, end_node)

        if result['success']:
            print("✓ PATH FOUND!")
            print(f"  Path length:    {result['path_length_m']:.2f} meters")
            print(f"  Path length:    {result['path_length_m']/1000:.2f} km")
            print(f"  Number of nodes: {result['num_nodes']}")
            print(f"\n  First 5 nodes in path:")
            for i, node_id in enumerate(result['node_ids'][:5], 1):
                print(f"    {i}. Node {node_id}")
            if result['num_nodes'] > 5:
                print(f"    ... and {result['num_nodes'] - 5} more nodes")
        else:
            print(f"✗ NO PATH FOUND")
            print(f"  Message: {result['message']}")

        # Test 2: Multiple routes
        print("\n" + "-" * 70)
        print("TEST 2: Multiple Routes")
        print("-" * 70)

        test_routes = [
            ("Moda to Fenerbahçe", (40.9856, 29.0298), (40.9638, 29.0408)),
            ("Kadıköy Square to Bağdat Ave", (40.9904, 29.0255), (40.9780, 29.0450)),
        ]

        for i, (name, start_coords, end_coords) in enumerate(test_routes, 1):
            print(f"\n{i}. {name}")

            start_node = find_nearest_node(graph, start_coords[0], start_coords[1])
            end_node = find_nearest_node(graph, end_coords[0], end_coords[1])

            result = compute_shortest_path(graph, start_node, end_node)

            if result['success']:
                print(f"   ✓ Path: {result['path_length_m']:.2f}m, "
                      f"{result['num_nodes']} nodes")
            else:
                print(f"   ✗ {result['message']}")

        # Test 3: Same start/end node
        print("\n" + "-" * 70)
        print("TEST 3: Same Start and End Node")
        print("-" * 70)

        same_node = find_nearest_node(graph, 40.9856, 29.0298)
        result = compute_shortest_path(graph, same_node, same_node)

        print(f"Node: {same_node}")
        print(f"Success: {result['success']}")
        print(f"Path length: {result['path_length_m']} meters")
        print(f"Number of nodes: {result['num_nodes']}")
        print(f"Message: {result['message']}")

        # Test 4: Path existence check
        print("\n" + "-" * 70)
        print("TEST 4: Check Path Existence")
        print("-" * 70)

        start_node = find_nearest_node(graph, 40.9856, 29.0298)
        end_node = find_nearest_node(graph, 40.9638, 29.0408)

        if has_path(graph, start_node, end_node):
            print(f"✓ Path exists between nodes {start_node} and {end_node}")
        else:
            print(f"✗ No path exists between nodes {start_node} and {end_node}")

        print("\n" + "=" * 70)
        print("✓ ALL TESTS COMPLETED".center(70))
        print("=" * 70)
        print("\nKey Features Demonstrated:")
        print("  1. Shortest path computation using Dijkstra's algorithm")
        print("  2. Path length calculation in meters")
        print("  3. Handling of no-path scenarios")
        print("  4. Same start/end node handling")
        print("  5. Path existence checking")
        print()

    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ ERROR".center(70))
        print("=" * 70)
        print(f"\n{str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
