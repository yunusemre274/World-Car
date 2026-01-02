"""
Utility functions for WorldCar routing system.

This module provides common helper functions used throughout the application,
including distance calculations, validation, and formatting.
"""

import math
import os
from typing import Tuple, Optional, Dict, Any
import networkx as nx
import numpy as np

from worldcar.config import (
    MIN_LATITUDE,
    MAX_LATITUDE,
    MIN_LONGITUDE,
    MAX_LONGITUDE,
    COORDINATE_PRECISION,
    DISTANCE_PRECISION,
)


# ============================================================================
# Distance Calculations
# ============================================================================

def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great circle distance between two points on Earth.

    Uses the Haversine formula to compute the distance between two geographic
    coordinates on a sphere. Accurate for small to medium distances.

    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees

    Returns:
        Distance in meters between the two points

    Example:
        >>> # Distance from Moda to Fenerbahçe (Kadıköy, Istanbul)
        >>> dist = haversine_distance(40.9856, 29.0298, 40.9638, 29.0408)
        >>> print(f"{dist:.0f} meters")
        2534 meters
    """
    # Earth's radius in meters
    R = 6371000

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


def euclidean_distance(
    x1: float, y1: float, x2: float, y2: float
) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        x1: X coordinate of first point
        y1: Y coordinate of first point
        x2: X coordinate of second point
        y2: Y coordinate of second point

    Returns:
        Euclidean distance between the two points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# ============================================================================
# Coordinate Validation
# ============================================================================

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate latitude and longitude coordinates.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        True if coordinates are valid, False otherwise

    Example:
        >>> validate_coordinates(40.9856, 29.0298)
        True
        >>> validate_coordinates(91.0, 29.0298)  # Invalid latitude
        False
    """
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False

    if math.isnan(lat) or math.isnan(lon):
        return False

    if math.isinf(lat) or math.isinf(lon):
        return False

    if not (MIN_LATITUDE <= lat <= MAX_LATITUDE):
        return False

    if not (MIN_LONGITUDE <= lon <= MAX_LONGITUDE):
        return False

    return True


def validate_coordinate_pair(
    origin: Tuple[float, float], destination: Tuple[float, float]
) -> Tuple[bool, Optional[str]]:
    """
    Validate a pair of origin and destination coordinates.

    Args:
        origin: Tuple of (latitude, longitude) for origin
        destination: Tuple of (latitude, longitude) for destination

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None

    Example:
        >>> origin = (40.9856, 29.0298)
        >>> dest = (40.9638, 29.0408)
        >>> is_valid, error = validate_coordinate_pair(origin, dest)
        >>> print(is_valid)
        True
    """
    if not isinstance(origin, tuple) or len(origin) != 2:
        return False, "Origin must be a tuple of (latitude, longitude)"

    if not isinstance(destination, tuple) or len(destination) != 2:
        return False, "Destination must be a tuple of (latitude, longitude)"

    origin_lat, origin_lon = origin
    dest_lat, dest_lon = destination

    if not validate_coordinates(origin_lat, origin_lon):
        return False, f"Invalid origin coordinates: ({origin_lat}, {origin_lon})"

    if not validate_coordinates(dest_lat, dest_lon):
        return False, f"Invalid destination coordinates: ({dest_lat}, {dest_lon})"

    # Check if origin and destination are the same
    if (
        abs(origin_lat - dest_lat) < 1e-6
        and abs(origin_lon - dest_lon) < 1e-6
    ):
        return False, "Origin and destination are the same"

    return True, None


# ============================================================================
# Graph Validation
# ============================================================================

def validate_graph(G: nx.MultiDiGraph) -> Tuple[bool, Optional[str]]:
    """
    Validate that a graph is suitable for routing.

    Checks that the graph has the required structure and attributes
    for routing operations.

    Args:
        G: NetworkX MultiDiGraph to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is None

    Example:
        >>> import networkx as nx
        >>> G = nx.MultiDiGraph()
        >>> G.add_node(1, y=40.9856, x=29.0298)
        >>> G.add_node(2, y=40.9638, x=29.0408)
        >>> G.add_edge(1, 2, length=1000)
        >>> is_valid, error = validate_graph(G)
        >>> print(is_valid)
        True
    """
    if not isinstance(G, (nx.MultiDiGraph, nx.DiGraph, nx.Graph)):
        return False, "Graph must be a NetworkX Graph instance"

    if G.number_of_nodes() == 0:
        return False, "Graph has no nodes"

    if G.number_of_edges() == 0:
        return False, "Graph has no edges"

    # Check that nodes have coordinate attributes
    sample_nodes = list(G.nodes(data=True))[:min(10, G.number_of_nodes())]
    for node_id, data in sample_nodes:
        if 'y' not in data or 'x' not in data:
            return False, f"Node {node_id} missing coordinate attributes (x, y)"

    # Check that edges have length attribute
    sample_edges = list(G.edges(data=True))[:min(10, G.number_of_edges())]
    for u, v, data in sample_edges:
        if 'length' not in data:
            return False, f"Edge ({u}, {v}) missing 'length' attribute"

    return True, None


# ============================================================================
# Graph Analysis
# ============================================================================

def get_bounding_box(G: nx.MultiDiGraph) -> Dict[str, float]:
    """
    Get the geographic bounding box of a graph.

    Args:
        G: NetworkX graph with node attributes 'x' (longitude) and 'y' (latitude)

    Returns:
        Dictionary with keys 'north', 'south', 'east', 'west'

    Example:
        >>> bbox = get_bounding_box(G)
        >>> print(f"North: {bbox['north']:.4f}, South: {bbox['south']:.4f}")
        North: 40.9900, South: 40.9500
    """
    lats = [data['y'] for _, data in G.nodes(data=True)]
    lons = [data['x'] for _, data in G.nodes(data=True)]

    return {
        'north': max(lats),
        'south': min(lats),
        'east': max(lons),
        'west': min(lons),
    }


def get_graph_extent(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Get detailed geographic extent information about a graph.

    Args:
        G: NetworkX graph with node attributes

    Returns:
        Dictionary with bounding box and approximate dimensions

    Example:
        >>> extent = get_graph_extent(G)
        >>> print(f"Width: {extent['width_km']:.2f} km")
        Width: 3.45 km
    """
    bbox = get_bounding_box(G)

    # Calculate approximate width and height using Haversine distance
    width_m = haversine_distance(
        (bbox['north'] + bbox['south']) / 2,  # mid latitude
        bbox['west'],
        (bbox['north'] + bbox['south']) / 2,
        bbox['east'],
    )

    height_m = haversine_distance(
        bbox['south'],
        (bbox['east'] + bbox['west']) / 2,  # mid longitude
        bbox['north'],
        (bbox['east'] + bbox['west']) / 2,
    )

    return {
        **bbox,
        'width_m': width_m,
        'height_m': height_m,
        'width_km': width_m / 1000,
        'height_km': height_m / 1000,
    }


# ============================================================================
# File System Utilities
# ============================================================================

def ensure_directory_exists(path: str) -> None:
    """
    Create directory if it doesn't exist.

    Args:
        path: Path to directory to create

    Example:
        >>> ensure_directory_exists("data/processed")
    """
    os.makedirs(path, exist_ok=True)


# ============================================================================
# Formatting Utilities
# ============================================================================

def format_distance(meters: float) -> str:
    """
    Format distance in meters to human-readable string.

    Automatically converts to kilometers if distance is large.

    Args:
        meters: Distance in meters

    Returns:
        Formatted string with appropriate units

    Example:
        >>> print(format_distance(500))
        500.00 m
        >>> print(format_distance(1500))
        1.50 km
        >>> print(format_distance(15234))
        15.23 km
    """
    if meters < 1000:
        return f"{meters:.{DISTANCE_PRECISION}f} m"
    else:
        km = meters / 1000
        return f"{km:.{DISTANCE_PRECISION}f} km"


def format_coordinates(lat: float, lon: float) -> str:
    """
    Format coordinates to human-readable string.

    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees

    Returns:
        Formatted coordinate string

    Example:
        >>> print(format_coordinates(40.9856, 29.0298))
        (40.985600, 29.029800)
    """
    return f"({lat:.{COORDINATE_PRECISION}f}, {lon:.{COORDINATE_PRECISION}f})"


def format_time(seconds: float) -> str:
    """
    Format time duration to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted time string

    Example:
        >>> print(format_time(45))
        45.00 s
        >>> print(format_time(125))
        2.08 min
    """
    if seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} min"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} h"


# ============================================================================
# Path Utilities
# ============================================================================

def compute_path_total_length(
    G: nx.MultiDiGraph, path: list, weight: str = "length"
) -> float:
    """
    Compute total length of a path in the graph.

    Args:
        G: NetworkX graph
        path: List of node IDs forming the path
        weight: Edge attribute to use for length (default: "length")

    Returns:
        Total path length in the units of the weight attribute

    Example:
        >>> path = [1, 2, 3, 4]
        >>> length = compute_path_total_length(G, path)
        >>> print(f"Path length: {length:.2f} meters")
        Path length: 2534.50 meters
    """
    total_length = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]

        # Get edge data (handle MultiDiGraph with multiple edges)
        if G.is_multigraph():
            # Get minimum weight edge if multiple edges exist
            edge_data = min(
                G[u][v].values(),
                key=lambda x: x.get(weight, float('inf'))
            )
        else:
            edge_data = G[u][v]

        edge_length = edge_data.get(weight, 0.0)
        total_length += edge_length

    return total_length


# ============================================================================
# Conversion Utilities
# ============================================================================

def meters_to_km(meters: float) -> float:
    """Convert meters to kilometers."""
    return meters / 1000.0


def km_to_meters(km: float) -> float:
    """Convert kilometers to meters."""
    return km * 1000.0


def meters_to_miles(meters: float) -> float:
    """Convert meters to miles."""
    return meters * 0.000621371


def miles_to_meters(miles: float) -> float:
    """Convert miles to meters."""
    return miles * 1609.34
