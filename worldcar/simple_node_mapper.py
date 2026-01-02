"""
Node Mapper for Phase 1 - Coordinate-to-Node Conversion

Simple module to map geographic coordinates to graph nodes using OSMnx.
Part of the WorldCar routing system.
"""

from typing import Tuple
import logging

import osmnx as ox
import networkx as nx

logger = logging.getLogger(__name__)

# Coordinate validation constants
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0


def find_nearest_node(
    graph: nx.MultiDiGraph,
    latitude: float,
    longitude: float,
    validate: bool = True
) -> int:
    """
    Find the nearest graph node to given coordinates.

    Uses OSMnx's nearest_nodes function to find the closest intersection
    in the road network to the specified latitude and longitude.

    Args:
        graph: NetworkX MultiDiGraph road network
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        validate: If True, validate coordinate ranges (default: True)

    Returns:
        Node ID of the nearest intersection

    Raises:
        ValueError: If coordinates are invalid
        TypeError: If graph is not a NetworkX graph
        RuntimeError: If nearest node cannot be found

    Example:
        >>> node_id = find_nearest_node(graph, 40.9856, 29.0298)
        >>> print(f"Nearest node: {node_id}")
    """
    if not isinstance(graph, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
        raise TypeError(f"Expected NetworkX graph, got {type(graph).__name__}")

    if graph.number_of_nodes() == 0:
        raise RuntimeError("Cannot find nearest node in empty graph")

    if validate:
        validate_coordinates(latitude, longitude)

    try:
        nearest_node = ox.nearest_nodes(graph, X=longitude, Y=latitude)
        logger.debug(f"Found node {nearest_node} for ({latitude:.6f}, {longitude:.6f})")
        return nearest_node

    except Exception as e:
        error_msg = (
            f"Failed to find nearest node for ({latitude:.6f}, {longitude:.6f}). "
            f"Error: {str(e)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_node_coordinates(graph: nx.MultiDiGraph, node_id: int) -> Tuple[float, float]:
    """
    Get latitude and longitude coordinates for a graph node.

    Args:
        graph: NetworkX MultiDiGraph road network
        node_id: Node ID to look up

    Returns:
        Tuple of (latitude, longitude) in decimal degrees

    Raises:
        KeyError: If node_id does not exist in graph
        ValueError: If node is missing coordinate attributes

    Example:
        >>> lat, lon = get_node_coordinates(graph, node_id)
        >>> print(f"Node at ({lat:.6f}, {lon:.6f})")
    """
    if node_id not in graph:
        raise KeyError(
            f"Node {node_id} not found in graph. "
            f"Graph has {graph.number_of_nodes()} nodes."
        )

    node_data = graph.nodes[node_id]

    if 'y' not in node_data or 'x' not in node_data:
        raise ValueError(
            f"Node {node_id} missing coordinate attributes (x, y)."
        )

    return node_data['y'], node_data['x']


def validate_coordinates(latitude: float, longitude: float) -> None:
    """
    Validate that coordinates are within valid ranges.

    Args:
        latitude: Latitude to validate
        longitude: Longitude to validate

    Raises:
        ValueError: If coordinates are invalid

    Example:
        >>> validate_coordinates(40.9856, 29.0298)  # Valid
        >>> validate_coordinates(91.0, 29.0)  # Raises ValueError
    """
    if not isinstance(latitude, (int, float)):
        raise ValueError(f"Latitude must be numeric, got {type(latitude).__name__}")

    if not isinstance(longitude, (int, float)):
        raise ValueError(f"Longitude must be numeric, got {type(longitude).__name__}")

    # NaN check
    if latitude != latitude:
        raise ValueError("Latitude cannot be NaN")

    if longitude != longitude:
        raise ValueError("Longitude cannot be NaN")

    # Infinity check
    if abs(latitude) == float('inf'):
        raise ValueError("Latitude cannot be infinite")

    if abs(longitude) == float('inf'):
        raise ValueError("Longitude cannot be infinite")

    # Range validation
    if not (MIN_LATITUDE <= latitude <= MAX_LATITUDE):
        raise ValueError(
            f"Invalid latitude: {latitude}. "
            f"Must be between {MIN_LATITUDE} and {MAX_LATITUDE}"
        )

    if not (MIN_LONGITUDE <= longitude <= MAX_LONGITUDE):
        raise ValueError(
            f"Invalid longitude: {longitude}. "
            f"Must be between {MIN_LONGITUDE} and {MAX_LONGITUDE}"
        )


def batch_find_nearest_nodes(
    graph: nx.MultiDiGraph,
    coordinates: list[Tuple[float, float]],
    validate: bool = True
) -> list[int]:
    """
    Find nearest nodes for multiple coordinate pairs.

    Args:
        graph: NetworkX MultiDiGraph road network
        coordinates: List of (latitude, longitude) tuples
        validate: If True, validate all coordinates

    Returns:
        List of node IDs corresponding to each coordinate pair

    Raises:
        ValueError: If any coordinates are invalid
        RuntimeError: If node lookup fails

    Example:
        >>> coords = [(40.9856, 29.0298), (40.9638, 29.0408)]
        >>> nodes = batch_find_nearest_nodes(graph, coords)
        >>> print(f"Found {len(nodes)} nodes")
    """
    if not coordinates:
        return []

    if validate:
        for i, (lat, lon) in enumerate(coordinates):
            try:
                validate_coordinates(lat, lon)
            except ValueError as e:
                raise ValueError(f"Invalid coordinates at index {i}: {str(e)}") from e

    latitudes = [coord[0] for coord in coordinates]
    longitudes = [coord[1] for coord in coordinates]

    try:
        nearest_nodes = ox.nearest_nodes(graph, X=longitudes, Y=latitudes)

        if isinstance(nearest_nodes, (int, float)):
            nearest_nodes = [int(nearest_nodes)]
        else:
            nearest_nodes = list(nearest_nodes)

        logger.info(f"Found nearest nodes for {len(coordinates)} coordinates")
        return nearest_nodes

    except Exception as e:
        error_msg = (
            f"Failed to find nearest nodes for {len(coordinates)} coordinates. "
            f"Error: {str(e)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
