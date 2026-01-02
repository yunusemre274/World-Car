"""
Node Mapper - Phase 1 Coordinate-to-Node Conversion

Maps geographic coordinates (latitude, longitude) to the nearest node
in a road network graph using OSMnx.

Requirements:
- Python 3.10+
- osmnx>=1.9.0
- networkx>=3.2

Usage:
    from node_mapper import find_nearest_node, get_node_coordinates

    node_id = find_nearest_node(graph, 40.9856, 29.0298)
    lat, lon = get_node_coordinates(graph, node_id)
"""

from typing import Tuple, Union
import logging

import osmnx as ox
import networkx as nx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
        graph: NetworkX MultiDiGraph road network (from graph_loader)
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        validate: If True, validate coordinate ranges (default: True)

    Returns:
        int: Node ID of the nearest intersection in the graph

    Raises:
        ValueError: If coordinates are invalid (out of valid range)
        TypeError: If graph is not a NetworkX graph
        RuntimeError: If graph is empty or nearest node cannot be found

    Example:
        >>> from graph_loader_standalone import load_city_graph
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> node_id = find_nearest_node(graph, 40.9856, 29.0298)
        >>> print(f"Nearest node: {node_id}")
        Nearest node: 298734512
    """
    # Validate graph type
    if not isinstance(graph, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
        raise TypeError(
            f"Expected NetworkX graph, got {type(graph).__name__}"
        )

    # Check graph is not empty
    if graph.number_of_nodes() == 0:
        raise RuntimeError("Cannot find nearest node in empty graph")

    # Validate coordinates if requested
    if validate:
        validate_coordinates(latitude, longitude)

    try:
        # Use OSMnx to find nearest node
        # OSMnx expects (Y, X) = (latitude, longitude)
        nearest_node = ox.nearest_nodes(
            graph,
            X=longitude,  # OSMnx uses X for longitude
            Y=latitude    # OSMnx uses Y for latitude
        )

        logger.debug(
            f"Found nearest node {nearest_node} for coordinates "
            f"({latitude:.6f}, {longitude:.6f})"
        )

        return nearest_node

    except Exception as e:
        error_msg = (
            f"Failed to find nearest node for coordinates "
            f"({latitude:.6f}, {longitude:.6f}). Error: {str(e)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_node_coordinates(
    graph: nx.MultiDiGraph,
    node_id: int
) -> Tuple[float, float]:
    """
    Get latitude and longitude coordinates for a graph node.

    Retrieves the geographic coordinates stored in the node's attributes.
    Road network nodes have 'y' (latitude) and 'x' (longitude) attributes.

    Args:
        graph: NetworkX MultiDiGraph road network
        node_id: Node ID to look up

    Returns:
        Tuple of (latitude, longitude) in decimal degrees

    Raises:
        KeyError: If node_id does not exist in graph
        ValueError: If node is missing coordinate attributes

    Example:
        >>> from graph_loader_standalone import load_city_graph
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> node_id = find_nearest_node(graph, 40.9856, 29.0298)
        >>> lat, lon = get_node_coordinates(graph, node_id)
        >>> print(f"Node at ({lat:.6f}, {lon:.6f})")
        Node at (40.985623, 29.029845)
    """
    # Check if node exists
    if node_id not in graph:
        raise KeyError(
            f"Node {node_id} not found in graph. "
            f"Graph has {graph.number_of_nodes()} nodes."
        )

    # Get node attributes
    node_data = graph.nodes[node_id]

    # Extract coordinates
    if 'y' not in node_data or 'x' not in node_data:
        raise ValueError(
            f"Node {node_id} missing coordinate attributes. "
            f"Expected 'x' (longitude) and 'y' (latitude)."
        )

    latitude = node_data['y']
    longitude = node_data['x']

    return latitude, longitude


def validate_coordinates(latitude: float, longitude: float) -> None:
    """
    Validate that coordinates are within valid ranges.

    Checks that latitude is between -90 and 90, and longitude is between
    -180 and 180. Also validates that values are numeric and not NaN/Inf.

    Args:
        latitude: Latitude to validate
        longitude: Longitude to validate

    Raises:
        ValueError: If coordinates are invalid with descriptive message

    Example:
        >>> validate_coordinates(40.9856, 29.0298)  # Valid - no exception
        >>> validate_coordinates(91.0, 29.0298)  # Invalid latitude
        Traceback (most recent call last):
        ...
        ValueError: Invalid latitude: 91.0. Must be between -90.0 and 90.0
    """
    # Check types
    if not isinstance(latitude, (int, float)):
        raise ValueError(
            f"Latitude must be numeric, got {type(latitude).__name__}"
        )

    if not isinstance(longitude, (int, float)):
        raise ValueError(
            f"Longitude must be numeric, got {type(longitude).__name__}"
        )

    # Check for NaN
    if latitude != latitude:  # NaN check (NaN != NaN)
        raise ValueError("Latitude cannot be NaN")

    if longitude != longitude:  # NaN check
        raise ValueError("Longitude cannot be NaN")

    # Check for infinity
    if abs(latitude) == float('inf'):
        raise ValueError("Latitude cannot be infinite")

    if abs(longitude) == float('inf'):
        raise ValueError("Longitude cannot be infinite")

    # Validate latitude range
    if not (MIN_LATITUDE <= latitude <= MAX_LATITUDE):
        raise ValueError(
            f"Invalid latitude: {latitude}. "
            f"Must be between {MIN_LATITUDE} and {MAX_LATITUDE}"
        )

    # Validate longitude range
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

    Efficiently maps multiple lat/lon pairs to their nearest graph nodes.
    Uses OSMnx's vectorized nearest_nodes function for better performance.

    Args:
        graph: NetworkX MultiDiGraph road network
        coordinates: List of (latitude, longitude) tuples
        validate: If True, validate all coordinates (default: True)

    Returns:
        List of node IDs corresponding to each coordinate pair

    Raises:
        ValueError: If any coordinates are invalid
        RuntimeError: If node lookup fails

    Example:
        >>> graph = load_city_graph("Kadıköy, Istanbul, Turkey")
        >>> coords = [(40.9856, 29.0298), (40.9638, 29.0408)]
        >>> nodes = batch_find_nearest_nodes(graph, coords)
        >>> print(f"Found {len(nodes)} nodes")
        Found 2 nodes
    """
    if not coordinates:
        return []

    # Validate all coordinates first if requested
    if validate:
        for i, (lat, lon) in enumerate(coordinates):
            try:
                validate_coordinates(lat, lon)
            except ValueError as e:
                raise ValueError(
                    f"Invalid coordinates at index {i}: {str(e)}"
                ) from e

    # Extract latitudes and longitudes
    latitudes = [coord[0] for coord in coordinates]
    longitudes = [coord[1] for coord in coordinates]

    try:
        # Use OSMnx vectorized function for batch processing
        nearest_nodes = ox.nearest_nodes(
            graph,
            X=longitudes,  # List of longitudes
            Y=latitudes    # List of latitudes
        )

        # Convert to list if it's a single value or array
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


# ============================================================================
# Main - Demo/Test
# ============================================================================

def main():
    """
    Demo function showing node mapper usage.
    Run: python node_mapper_standalone.py
    """
    print("\n" + "=" * 70)
    print("NODE MAPPER - PHASE 1 DEMO".center(70))
    print("=" * 70 + "\n")

    # First load a graph (reusing from graph_loader demo)
    try:
        from graph_loader_standalone import load_city_graph
    except ImportError:
        print("Error: graph_loader_standalone.py not found.")
        print("Please ensure graph_loader_standalone.py is in the same directory.")
        return

    city = "Kadıköy, Istanbul, Turkey"
    print(f"Loading road network for: {city}")
    print("(This may take 15-30 seconds on first download...)\n")

    try:
        graph = load_city_graph(city)
        print("✓ Graph loaded successfully\n")

        # Test 1: Single coordinate lookup
        print("-" * 70)
        print("TEST 1: Find Nearest Node")
        print("-" * 70)

        test_lat, test_lon = 40.9856, 29.0298  # Moda, Kadıköy
        print(f"Query coordinates: ({test_lat}, {test_lon})")

        node_id = find_nearest_node(graph, test_lat, test_lon)
        print(f"Nearest node ID: {node_id}")

        # Get the actual coordinates of the node
        node_lat, node_lon = get_node_coordinates(graph, node_id)
        print(f"Node coordinates: ({node_lat:.6f}, {node_lon:.6f})")

        # Calculate distance
        import math
        R = 6371000  # Earth radius in meters
        dlat = math.radians(node_lat - test_lat)
        dlon = math.radians(node_lon - test_lon)
        a = (math.sin(dlat/2)**2 +
             math.cos(math.radians(test_lat)) * math.cos(math.radians(node_lat)) *
             math.sin(dlon/2)**2)
        distance = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        print(f"Distance to node: {distance:.2f} meters\n")

        # Test 2: Coordinate validation
        print("-" * 70)
        print("TEST 2: Coordinate Validation")
        print("-" * 70)

        valid_coords = [(40.9856, 29.0298)]
        invalid_coords = [
            (91.0, 29.0),      # Invalid latitude
            (40.0, 181.0),     # Invalid longitude
            (float('nan'), 29.0),  # NaN
        ]

        print("Valid coordinates:")
        for lat, lon in valid_coords:
            try:
                validate_coordinates(lat, lon)
                print(f"  ✓ ({lat}, {lon}) - Valid")
            except ValueError as e:
                print(f"  ✗ ({lat}, {lon}) - {e}")

        print("\nInvalid coordinates:")
        for lat, lon in invalid_coords:
            try:
                validate_coordinates(lat, lon)
                print(f"  ✓ ({lat}, {lon}) - Valid")
            except ValueError as e:
                print(f"  ✗ ({lat}, {lon}) - {str(e)[:50]}...")

        # Test 3: Batch processing
        print("\n" + "-" * 70)
        print("TEST 3: Batch Node Lookup")
        print("-" * 70)

        test_coords = [
            (40.9856, 29.0298),  # Moda
            (40.9638, 29.0408),  # Fenerbahçe
            (40.9904, 29.0255),  # Kadıköy Square
        ]

        print(f"Finding nearest nodes for {len(test_coords)} coordinates...")
        node_ids = batch_find_nearest_nodes(graph, test_coords)

        for i, (coord, node_id) in enumerate(zip(test_coords, node_ids), 1):
            node_lat, node_lon = get_node_coordinates(graph, node_id)
            print(f"  {i}. Query: ({coord[0]:.4f}, {coord[1]:.4f}) "
                  f"→ Node {node_id} at ({node_lat:.6f}, {node_lon:.6f})")

        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED".center(70))
        print("=" * 70 + "\n")

    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ ERROR".center(70))
        print("=" * 70)
        print(f"\n{str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
