"""
Statistics Module for WorldCar routing system.

This module provides comprehensive graph statistics and analysis functions
for road network graphs, including node/edge counts, connectivity analysis,
and geographic extent calculations.
"""

import logging
from typing import Dict, Any

import networkx as nx

from worldcar.utils import get_bounding_box, format_distance, meters_to_km

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_graph_statistics(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Compute comprehensive statistics for a road network graph.

    Calculates various metrics including node/edge counts, total road length,
    connectivity information, and geographic extent.

    Args:
        G: NetworkX road network graph

    Returns:
        Dictionary with graph statistics:
        {
            'num_nodes': int,
            'num_edges': int,
            'total_length_m': float,
            'total_length_km': float,
            'avg_edge_length_m': float,
            'min_edge_length_m': float,
            'max_edge_length_m': float,
            'num_connected_components': int,
            'largest_component_size': int,
            'largest_component_pct': float,
            'avg_degree': float,
            'network_density': float,
            'is_directed': bool,
            'is_multigraph': bool,
            'bounding_box': Dict[str, float]
        }

    Example:
        >>> stats = compute_graph_statistics(G)
        >>> print(f"Network has {stats['num_nodes']} nodes")
        >>> print(f"Total road length: {stats['total_length_km']:.2f} km")
    """
    logger.info("Computing graph statistics...")

    # Basic counts
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    # Edge length statistics
    edge_lengths = [data.get('length', 0.0) for u, v, data in G.edges(data=True)]

    if edge_lengths:
        total_length_m = sum(edge_lengths)
        avg_edge_length_m = total_length_m / len(edge_lengths)
        min_edge_length_m = min(edge_lengths)
        max_edge_length_m = max(edge_lengths)
    else:
        total_length_m = 0.0
        avg_edge_length_m = 0.0
        min_edge_length_m = 0.0
        max_edge_length_m = 0.0

    total_length_km = meters_to_km(total_length_m)

    # Connectivity analysis
    if G.is_directed():
        num_components = nx.number_weakly_connected_components(G)
        components = list(nx.weakly_connected_components(G))
    else:
        num_components = nx.number_connected_components(G)
        components = list(nx.connected_components(G))

    if components:
        largest_component_size = len(max(components, key=len))
        largest_component_pct = (largest_component_size / num_nodes) * 100
    else:
        largest_component_size = 0
        largest_component_pct = 0.0

    # Degree statistics
    if num_nodes > 0:
        degrees = [degree for node, degree in G.degree()]
        avg_degree = sum(degrees) / len(degrees)
    else:
        avg_degree = 0.0

    # Network density
    if G.is_directed():
        max_edges = num_nodes * (num_nodes - 1)
    else:
        max_edges = num_nodes * (num_nodes - 1) / 2

    if max_edges > 0:
        network_density = num_edges / max_edges
    else:
        network_density = 0.0

    # Geographic extent
    try:
        bounding_box = get_bounding_box(G)
    except Exception as e:
        logger.warning(f"Could not compute bounding box: {e}")
        bounding_box = {'north': 0, 'south': 0, 'east': 0, 'west': 0}

    stats = {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'total_length_m': total_length_m,
        'total_length_km': total_length_km,
        'avg_edge_length_m': avg_edge_length_m,
        'min_edge_length_m': min_edge_length_m,
        'max_edge_length_m': max_edge_length_m,
        'num_connected_components': num_components,
        'largest_component_size': largest_component_size,
        'largest_component_pct': largest_component_pct,
        'avg_degree': avg_degree,
        'network_density': network_density,
        'is_directed': G.is_directed(),
        'is_multigraph': G.is_multigraph(),
        'bounding_box': bounding_box,
    }

    logger.info(f"Statistics computed: {num_nodes} nodes, {num_edges} edges")

    return stats


def print_statistics(stats: Dict[str, Any]) -> None:
    """
    Print graph statistics in a human-readable format.

    Args:
        stats: Statistics dictionary from compute_graph_statistics()

    Example:
        >>> stats = compute_graph_statistics(G)
        >>> print_statistics(stats)
        ========================================
        Graph Statistics
        ========================================
        Nodes: 12,453
        Edges: 28,901
        Total Road Length: 456.78 km
        ...
    """
    print("\n" + "=" * 60)
    print("GRAPH STATISTICS".center(60))
    print("=" * 60)

    # Basic Structure
    print("\n--- Basic Structure ---")
    print(f"Nodes (Intersections): {stats['num_nodes']:,}")
    print(f"Edges (Road Segments): {stats['num_edges']:,}")
    print(f"Graph Type: {'Directed' if stats['is_directed'] else 'Undirected'}")
    print(f"Multigraph: {'Yes' if stats['is_multigraph'] else 'No'}")

    # Road Length
    print("\n--- Road Network Length ---")
    print(f"Total Length: {format_distance(stats['total_length_m'])} "
          f"({stats['total_length_km']:.2f} km)")
    print(f"Average Edge Length: {format_distance(stats['avg_edge_length_m'])}")
    print(f"Min Edge Length: {format_distance(stats['min_edge_length_m'])}")
    print(f"Max Edge Length: {format_distance(stats['max_edge_length_m'])}")

    # Connectivity
    print("\n--- Connectivity ---")
    print(f"Connected Components: {stats['num_connected_components']}")
    print(f"Largest Component Size: {stats['largest_component_size']:,} nodes "
          f"({stats['largest_component_pct']:.1f}%)")

    # Network Properties
    print("\n--- Network Properties ---")
    print(f"Average Node Degree: {stats['avg_degree']:.2f}")
    print(f"Network Density: {stats['network_density']:.6f}")

    # Geographic Extent
    bbox = stats['bounding_box']
    print("\n--- Geographic Extent ---")
    print(f"North: {bbox['north']:.6f}°")
    print(f"South: {bbox['south']:.6f}°")
    print(f"East: {bbox['east']:.6f}°")
    print(f"West: {bbox['west']:.6f}°")

    print("\n" + "=" * 60 + "\n")


def get_network_extent(G: nx.MultiDiGraph) -> Dict[str, float]:
    """
    Get geographic extent of the road network.

    Args:
        G: NetworkX road network graph

    Returns:
        Dictionary with bounding box coordinates

    Example:
        >>> extent = get_network_extent(G)
        >>> print(f"Network spans from {extent['south']:.4f}° to {extent['north']:.4f}° latitude")
    """
    return get_bounding_box(G)


def analyze_connectivity(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Analyze graph connectivity properties in detail.

    Args:
        G: NetworkX road network graph

    Returns:
        Dictionary with connectivity analysis:
        {
            'is_connected': bool,
            'num_components': int,
            'component_sizes': List[int],
            'largest_component_size': int,
            'isolated_nodes': int,
        }

    Example:
        >>> conn = analyze_connectivity(G)
        >>> if not conn['is_connected']:
        ...     print(f"Warning: Graph has {conn['num_components']} components")
    """
    logger.info("Analyzing graph connectivity...")

    # Determine connectivity based on graph type
    if G.is_directed():
        num_components = nx.number_weakly_connected_components(G)
        components = list(nx.weakly_connected_components(G))
        is_connected = nx.is_weakly_connected(G)
    else:
        num_components = nx.number_connected_components(G)
        components = list(nx.connected_components(G))
        is_connected = nx.is_connected(G)

    # Get component sizes
    component_sizes = sorted([len(comp) for comp in components], reverse=True)

    # Count isolated nodes (nodes with degree 0)
    isolated_nodes = len([node for node, degree in G.degree() if degree == 0])

    analysis = {
        'is_connected': is_connected,
        'num_components': num_components,
        'component_sizes': component_sizes,
        'largest_component_size': component_sizes[0] if component_sizes else 0,
        'isolated_nodes': isolated_nodes,
    }

    logger.info(
        f"Connectivity analysis: {num_components} components, "
        f"{isolated_nodes} isolated nodes"
    )

    return analysis


def get_degree_statistics(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Compute detailed degree statistics for the graph.

    Args:
        G: NetworkX road network graph

    Returns:
        Dictionary with degree statistics:
        {
            'avg_degree': float,
            'min_degree': int,
            'max_degree': int,
            'median_degree': float,
            'degree_distribution': Dict[int, int]  # degree -> count
        }

    Example:
        >>> deg_stats = get_degree_statistics(G)
        >>> print(f"Average degree: {deg_stats['avg_degree']:.2f}")
        >>> print(f"Max degree (busiest intersection): {deg_stats['max_degree']}")
    """
    degrees = [degree for node, degree in G.degree()]

    if not degrees:
        return {
            'avg_degree': 0.0,
            'min_degree': 0,
            'max_degree': 0,
            'median_degree': 0.0,
            'degree_distribution': {},
        }

    # Basic statistics
    avg_degree = sum(degrees) / len(degrees)
    min_degree = min(degrees)
    max_degree = max(degrees)

    # Median degree
    sorted_degrees = sorted(degrees)
    n = len(sorted_degrees)
    if n % 2 == 0:
        median_degree = (sorted_degrees[n // 2 - 1] + sorted_degrees[n // 2]) / 2
    else:
        median_degree = sorted_degrees[n // 2]

    # Degree distribution
    degree_distribution = {}
    for degree in degrees:
        degree_distribution[degree] = degree_distribution.get(degree, 0) + 1

    return {
        'avg_degree': avg_degree,
        'min_degree': min_degree,
        'max_degree': max_degree,
        'median_degree': median_degree,
        'degree_distribution': degree_distribution,
    }


def summarize_graph(G: nx.MultiDiGraph) -> str:
    """
    Get a brief one-line summary of the graph.

    Args:
        G: NetworkX road network graph

    Returns:
        Summary string

    Example:
        >>> print(summarize_graph(G))
        Road network: 12,453 nodes, 28,901 edges, 456.78 km
    """
    stats = compute_graph_statistics(G)
    return (
        f"Road network: {stats['num_nodes']:,} nodes, "
        f"{stats['num_edges']:,} edges, "
        f"{stats['total_length_km']:.2f} km"
    )


# ============================================================================
# Convenience Functions
# ============================================================================

def print_graph_summary(G: nx.MultiDiGraph) -> None:
    """
    Compute and print complete graph statistics.

    Convenience function that combines compute_graph_statistics() and
    print_statistics().

    Args:
        G: NetworkX road network graph

    Example:
        >>> print_graph_summary(G)
        ========================================
        Graph Statistics
        ========================================
        ...
    """
    stats = compute_graph_statistics(G)
    print_statistics(stats)
