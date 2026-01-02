"""
Path Service for Phase 1 - Shortest Path Computation

Computes shortest paths using Dijkstra's algorithm via NetworkX.
Part of the WorldCar routing system.
"""

from typing import Dict, Any, List
import logging

import networkx as nx

logger = logging.getLogger(__name__)


def compute_shortest_path(
    graph: nx.MultiDiGraph,
    start_node: int,
    end_node: int,
    weight: str = "length"
) -> Dict[str, Any]:
    """
    Compute shortest path between two nodes using Dijkstra's algorithm.

    Args:
        graph: NetworkX MultiDiGraph road network
        start_node: Starting node ID
        end_node: Ending node ID
        weight: Edge attribute to use as weight (default: "length")

    Returns:
        Dictionary containing:
            - success (bool): True if path found
            - node_ids (List[int]): List of node IDs in path
            - path_length_m (float): Total path length in meters
            - num_nodes (int): Number of nodes in path
            - start_node (int): Starting node ID
            - end_node (int): Ending node ID
            - message (str): Success/error message

    Example:
        >>> result = compute_shortest_path(graph, start_node, end_node)
        >>> if result['success']:
        ...     print(f"Length: {result['path_length_m']:.2f}m")
    """
    if not isinstance(graph, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
        raise TypeError(f"Expected NetworkX graph, got {type(graph).__name__}")

    if graph.number_of_nodes() == 0:
        raise RuntimeError("Cannot compute path on empty graph")

    if start_node not in graph:
        raise ValueError(f"Start node {start_node} not found in graph")

    if end_node not in graph:
        raise ValueError(f"End node {end_node} not found in graph")

    if start_node == end_node:
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
        path = nx.shortest_path(
            graph,
            source=start_node,
            target=end_node,
            weight=weight,
            method='dijkstra'
        )

        path_length = calculate_path_length(graph, path, weight)

        logger.info(f"Found path: {len(path)} nodes, {path_length:.2f}m")

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
        logger.warning(f"No path from {start_node} to {end_node}")

        return {
            'success': False,
            'node_ids': [],
            'path_length_m': 0.0,
            'num_nodes': 0,
            'start_node': start_node,
            'end_node': end_node,
            'message': f'No path exists between nodes {start_node} and {end_node}'
        }

    except Exception as e:
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

    Args:
        graph: NetworkX MultiDiGraph road network
        path: List of node IDs forming the path
        weight: Edge attribute to use as weight (default: "length")

    Returns:
        Total path length in meters

    Example:
        >>> length = calculate_path_length(graph, [1, 2, 3, 4])
    """
    if len(path) < 2:
        return 0.0

    total_length = 0.0

    for i in range(len(path) - 1):
        start = path[i]
        end = path[i + 1]

        if graph.is_multigraph():
            edge_data = graph[start][end]
            min_weight = min(
                data.get(weight, float('inf'))
                for data in edge_data.values()
            )
            total_length += min_weight
        else:
            edge_data = graph[start][end]
            total_length += edge_data.get(weight, 0.0)

    return total_length


def has_path(graph: nx.MultiDiGraph, start_node: int, end_node: int) -> bool:
    """
    Check if a path exists between two nodes.

    Args:
        graph: NetworkX MultiDiGraph road network
        start_node: Starting node ID
        end_node: Ending node ID

    Returns:
        True if a path exists, False otherwise
    """
    try:
        return nx.has_path(graph, start_node, end_node)
    except (nx.NodeNotFound, nx.NetworkXError):
        return False
