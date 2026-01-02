"""
Graph Loader for Phase 1 - Road Network Loading

This module provides simple functions to load road network graphs from
OpenStreetMap using OSMnx and NetworkX.

Phase 1 Focus:
- Load city road networks
- Extract basic graph statistics
- No traffic simulation
- No routing algorithms (handled in separate module)
"""

from typing import Dict, Any
import logging

import osmnx as ox
import networkx as nx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_city_graph(city_name: str) -> nx.MultiDiGraph:
    """
    Load road network graph for a given city from OpenStreetMap.

    This function downloads the drivable road network for a specified city
    using OSMnx, which queries OpenStreetMap's Overpass API. The resulting
    graph contains nodes (intersections) and edges (road segments) with
    geographic coordinates and road attributes.

    Args:
        city_name: Name of the city or place to download.
                   Examples: "Istanbul, Turkey"
                            "Manhattan, New York, USA"
                            "Kadıköy, Istanbul, Turkey"

    Returns:
        NetworkX MultiDiGraph representing the road network.
        - Nodes have 'x' (longitude) and 'y' (latitude) attributes
        - Edges have 'length' (meters), 'osmid', and other OSM attributes
        - Directed graph supporting one-way streets
        - Multi-graph allowing multiple edges between nodes

    Raises:
        ValueError: If the city name cannot be geocoded or network cannot be downloaded
        ConnectionError: If unable to connect to OSM servers

    Example:
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> print(f"Loaded {graph.number_of_nodes()} intersections")
        Loaded 12453 intersections
    """
    logger.info(f"Loading road network for: {city_name}")

    try:
        # Download road network from OpenStreetMap
        # network_type="drive" gets only roads accessible by car
        # simplify=True removes nodes that aren't intersections
        graph = ox.graph_from_place(
            city_name,
            network_type="drive",
            simplify=True
        )

        logger.info(
            f"Successfully loaded graph with {graph.number_of_nodes()} nodes "
            f"and {graph.number_of_edges()} edges"
        )

        # Ensure all edges have length in meters
        # OSMnx typically adds this, but we verify and add if missing
        graph = _ensure_edge_lengths(graph)

        return graph

    except Exception as e:
        logger.error(f"Failed to load graph for '{city_name}': {str(e)}")
        raise ValueError(
            f"Could not load road network for '{city_name}'. "
            f"Please check the city name and try again. Error: {str(e)}"
        ) from e


def get_graph_stats(graph: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Get basic statistics about a road network graph.

    Computes fundamental graph metrics including node count, edge count,
    and basic network properties.

    Args:
        graph: NetworkX MultiDiGraph representing a road network

    Returns:
        Dictionary containing graph statistics:
        {
            'num_nodes': int,           # Number of intersections
            'num_edges': int,           # Number of road segments
            'graph_type': str,          # 'MultiDiGraph'
            'is_directed': bool,        # True for road networks
            'is_multigraph': bool,      # True (allows multiple edges)
        }

    Example:
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> stats = get_graph_stats(graph)
        >>> print(f"Network has {stats['num_nodes']} intersections")
        Network has 12453 intersections
        >>> print(f"Network has {stats['num_edges']} road segments")
        Network has 28901 road segments
    """
    if not isinstance(graph, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
        raise TypeError(f"Expected NetworkX graph, got {type(graph)}")

    stats = {
        'num_nodes': graph.number_of_nodes(),
        'num_edges': graph.number_of_edges(),
        'graph_type': type(graph).__name__,
        'is_directed': graph.is_directed(),
        'is_multigraph': graph.is_multigraph(),
    }

    logger.debug(f"Graph statistics: {stats}")

    return stats


def _ensure_edge_lengths(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Ensure all edges have a 'length' attribute in meters.

    OSMnx typically adds edge lengths automatically, but this function
    verifies they exist and adds them if missing.

    Args:
        graph: NetworkX MultiDiGraph

    Returns:
        Graph with all edges having 'length' attribute

    Note:
        This is an internal function called by load_city_graph()
    """
    # Check if any edges are missing 'length' attribute
    edges_missing_length = []

    for u, v, key, data in graph.edges(keys=True, data=True):
        if 'length' not in data:
            edges_missing_length.append((u, v, key))

    # If any edges are missing length, use OSMnx to calculate
    if edges_missing_length:
        logger.warning(
            f"Found {len(edges_missing_length)} edges missing 'length' attribute. "
            f"Adding edge lengths..."
        )
        graph = ox.add_edge_lengths(graph)
        logger.info("Edge lengths added successfully")

    return graph


# ============================================================================
# Convenience Functions
# ============================================================================

def print_graph_info(graph: nx.MultiDiGraph, city_name: str = "Unknown") -> None:
    """
    Print formatted information about a graph.

    Convenience function to display graph statistics in a readable format.

    Args:
        graph: NetworkX MultiDiGraph
        city_name: Name of the city (for display purposes)

    Example:
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> print_graph_info(graph, "Kadıköy, Istanbul")
        ========================================
        Road Network: Kadıköy, Istanbul
        ========================================
        Nodes (Intersections): 12,453
        Edges (Road Segments): 28,901
        Graph Type: MultiDiGraph
        Directed: Yes
        ========================================
    """
    stats = get_graph_stats(graph)

    print("\n" + "=" * 60)
    print(f"Road Network: {city_name}".center(60))
    print("=" * 60)
    print(f"Nodes (Intersections): {stats['num_nodes']:,}")
    print(f"Edges (Road Segments): {stats['num_edges']:,}")
    print(f"Graph Type: {stats['graph_type']}")
    print(f"Directed: {'Yes' if stats['is_directed'] else 'No'}")
    print("=" * 60 + "\n")


# ============================================================================
# Module Test/Demo
# ============================================================================

if __name__ == "__main__":
    """
    Simple test/demo of the graph loader functionality.
    Run this file directly to test: python graph_loader.py
    """
    print("Graph Loader - Phase 1 Demo")
    print("=" * 60)

    # Example: Load a small area for testing
    test_city = "Kadıköy, Istanbul, Turkey"

    print(f"\nLoading road network for: {test_city}")
    print("This may take 15-30 seconds on first download...\n")

    try:
        # Load the graph
        graph = load_city_graph(test_city)

        # Display statistics
        print_graph_info(graph, test_city)

        # Get detailed stats
        stats = get_graph_stats(graph)

        print("Additional Information:")
        print(f"  Graph type: {stats['graph_type']}")
        print(f"  Multi-graph (allows parallel edges): {stats['is_multigraph']}")

        # Show a sample node
        sample_node = list(graph.nodes(data=True))[0]
        node_id, node_data = sample_node
        print(f"\nSample Node (Intersection):")
        print(f"  ID: {node_id}")
        print(f"  Latitude: {node_data.get('y', 'N/A'):.6f}")
        print(f"  Longitude: {node_data.get('x', 'N/A'):.6f}")

        # Show a sample edge
        sample_edge = list(graph.edges(data=True))[0]
        u, v, edge_data = sample_edge
        print(f"\nSample Edge (Road Segment):")
        print(f"  From Node: {u}")
        print(f"  To Node: {v}")
        print(f"  Length: {edge_data.get('length', 'N/A'):.2f} meters")

        print("\n✓ Graph loaded successfully!")

    except Exception as e:
        print(f"\n✗ Error loading graph: {str(e)}")
        import traceback
        traceback.print_exc()
