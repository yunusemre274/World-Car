"""
Graph Loader - Phase 1 Road Network Loading (Standalone Version)

A clean, standalone implementation for loading road network graphs from
OpenStreetMap using OSMnx and NetworkX.

Requirements:
- Python 3.10+
- osmnx>=1.9.0
- networkx>=3.2

Usage:
    from graph_loader import load_city_graph, get_graph_stats

    graph = load_city_graph("Kadıköy, Istanbul, Turkey")
    stats = get_graph_stats(graph)
    print(f"Loaded {stats['num_nodes']} nodes and {stats['num_edges']} edges")
"""

from typing import Dict, Any
import logging

import osmnx as ox
import networkx as nx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_city_graph(city_name: str) -> nx.MultiDiGraph:
    """
    Load road network graph for a given city from OpenStreetMap.

    Downloads the drivable road network (network_type="drive") for the specified
    city from OpenStreetMap using OSMnx. The graph is simplified to remove nodes
    that aren't intersections, and all edges have lengths in meters.

    Args:
        city_name: Name of city/place to download. Can be:
                   - City name: "Istanbul, Turkey"
                   - District: "Kadıköy, Istanbul, Turkey"
                   - Full address: "Manhattan, New York, USA"
                   OSMnx uses Nominatim for geocoding.

    Returns:
        nx.MultiDiGraph: Road network graph where:
            - Nodes represent intersections with 'x' (lon) and 'y' (lat) attributes
            - Edges represent road segments with 'length' (meters) attribute
            - Directed graph (supports one-way streets)
            - Multi-graph (allows multiple edges between nodes)

    Raises:
        ValueError: If city name cannot be geocoded or download fails

    Example:
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> print(f"{graph.number_of_nodes()} intersections")
        12453 intersections
        >>> print(f"{graph.number_of_edges()} road segments")
        28901 road segments
    """
    logger.info(f"Downloading road network for: {city_name}")

    try:
        # Download from OpenStreetMap
        # - network_type="drive": only car-accessible roads
        # - simplify=True: remove nodes that aren't intersections
        graph = ox.graph_from_place(
            city_name,
            network_type="drive",
            simplify=True
        )

        # Verify graph was loaded
        if graph.number_of_nodes() == 0:
            raise ValueError(f"No road network found for '{city_name}'")

        logger.info(
            f"✓ Loaded {graph.number_of_nodes():,} nodes, "
            f"{graph.number_of_edges():,} edges"
        )

        # Ensure all edges have length attribute
        graph = _add_edge_lengths_if_missing(graph)

        return graph

    except Exception as e:
        error_msg = (
            f"Failed to load road network for '{city_name}'. "
            f"Check city name spelling and internet connection. "
            f"Error: {str(e)}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e


def get_graph_stats(graph: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Calculate basic statistics for a road network graph.

    Args:
        graph: NetworkX graph (typically from load_city_graph)

    Returns:
        Dictionary with graph statistics:
            - num_nodes (int): Number of nodes (intersections)
            - num_edges (int): Number of edges (road segments)
            - graph_type (str): Type of graph (e.g., "MultiDiGraph")
            - is_directed (bool): Whether graph is directed
            - is_multigraph (bool): Whether graph allows multiple edges

    Raises:
        TypeError: If input is not a NetworkX graph

    Example:
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> stats = get_graph_stats(graph)
        >>> print(f"Nodes: {stats['num_nodes']:,}")
        Nodes: 12,453
        >>> print(f"Edges: {stats['num_edges']:,}")
        Edges: 28,901
    """
    # Validate input
    if not isinstance(graph, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
        raise TypeError(
            f"Expected NetworkX graph, got {type(graph).__name__}"
        )

    # Calculate statistics
    stats = {
        'num_nodes': graph.number_of_nodes(),
        'num_edges': graph.number_of_edges(),
        'graph_type': type(graph).__name__,
        'is_directed': graph.is_directed(),
        'is_multigraph': graph.is_multigraph(),
    }

    return stats


# ============================================================================
# Internal Helper Functions
# ============================================================================

def _add_edge_lengths_if_missing(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Ensure all edges have 'length' attribute in meters.

    OSMnx usually adds this automatically, but we verify and add if needed.
    This is an internal function called by load_city_graph().

    Args:
        graph: NetworkX MultiDiGraph

    Returns:
        Graph with 'length' attribute on all edges
    """
    # Count edges missing 'length'
    missing_count = sum(
        1 for u, v, data in graph.edges(data=True)
        if 'length' not in data
    )

    if missing_count > 0:
        logger.warning(
            f"Found {missing_count} edges without 'length'. Adding lengths..."
        )
        graph = ox.add_edge_lengths(graph)
        logger.info("✓ Edge lengths added")

    return graph


# ============================================================================
# Main - Demo/Test
# ============================================================================

def main():
    """
    Demo function showing how to use the graph loader.
    Run: python graph_loader_standalone.py
    """
    print("\n" + "=" * 70)
    print("GRAPH LOADER - PHASE 1 DEMO".center(70))
    print("=" * 70 + "\n")

    # Test city (use a district for faster download)
    city = "Kadıköy, Istanbul, Turkey"

    print(f"Loading road network for: {city}")
    print("Note: First download may take 15-30 seconds...\n")

    try:
        # Load the graph
        graph = load_city_graph(city)

        # Get and display statistics
        stats = get_graph_stats(graph)

        print("\n" + "-" * 70)
        print("GRAPH STATISTICS".center(70))
        print("-" * 70)
        print(f"Nodes (Intersections):     {stats['num_nodes']:>10,}")
        print(f"Edges (Road Segments):     {stats['num_edges']:>10,}")
        print(f"Graph Type:                {stats['graph_type']:>10}")
        print(f"Directed:                  {str(stats['is_directed']):>10}")
        print(f"Multi-graph:               {str(stats['is_multigraph']):>10}")
        print("-" * 70)

        # Show sample node data
        print("\nSAMPLE NODE (Intersection):")
        node_id, node_data = list(graph.nodes(data=True))[0]
        print(f"  Node ID:    {node_id}")
        print(f"  Latitude:   {node_data['y']:.6f}°")
        print(f"  Longitude:  {node_data['x']:.6f}°")

        # Show sample edge data
        print("\nSAMPLE EDGE (Road Segment):")
        u, v, edge_data = list(graph.edges(data=True))[0]
        print(f"  From Node:  {u}")
        print(f"  To Node:    {v}")
        print(f"  Length:     {edge_data['length']:.2f} meters")

        if 'name' in edge_data:
            print(f"  Street:     {edge_data['name']}")

        print("\n" + "=" * 70)
        print("✓ SUCCESS - Graph loaded and validated".center(70))
        print("=" * 70 + "\n")

        return graph

    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ ERROR".center(70))
        print("=" * 70)
        print(f"\n{str(e)}\n")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
