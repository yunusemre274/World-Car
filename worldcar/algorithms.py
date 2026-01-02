"""
Routing Algorithms Module for WorldCar routing system.

This module implements shortest path routing algorithms on road network graphs.
Currently implements Dijkstra's algorithm via NetworkX for finding optimal routes
between geographic coordinates.
"""

import logging
import time
from typing import Dict, Any, List, Tuple, Optional

import networkx as nx

from worldcar.node_mapper import NodeMapper
from worldcar.config import DEFAULT_WEIGHT, ENABLE_PERFORMANCE_LOGGING
from worldcar.utils import (
    validate_coordinates,
    compute_path_total_length,
    format_distance,
    format_coordinates,
    format_time,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Router:
    """
    Handles routing computations on road network graphs.

    Provides methods to compute shortest paths between geographic coordinates
    using Dijkstra's algorithm. Automatically handles coordinate-to-node mapping
    and path extraction.

    Attributes:
        graph (nx.MultiDiGraph): Road network graph
        node_mapper (NodeMapper): Mapper for converting coordinates to nodes

    Example:
        >>> loader = GraphLoader()
        >>> G = loader.get_or_create_graph()
        >>> mapper = NodeMapper(G)
        >>> router = Router(G, mapper)
        >>> result = router.compute_shortest_path(
        ...     40.9856, 29.0298,  # Moda
        ...     40.9638, 29.0408   # Fenerbahçe
        ... )
        >>> print(f"Distance: {result['distance']:.2f} meters")
        Distance: 2534.50 meters
    """

    def __init__(self, G: nx.MultiDiGraph, node_mapper: NodeMapper):
        """
        Initialize Router with graph and node mapper.

        Args:
            G: NetworkX road network graph
            node_mapper: NodeMapper instance for coordinate-to-node conversion

        Raises:
            ValueError: If graph is empty or node_mapper is invalid
        """
        if G.number_of_nodes() == 0:
            raise ValueError("Cannot create Router with empty graph")

        if not isinstance(node_mapper, NodeMapper):
            raise TypeError("node_mapper must be a NodeMapper instance")

        self.graph = G
        self.node_mapper = node_mapper

        logger.info(
            f"Router initialized with graph: {G.number_of_nodes()} nodes, "
            f"{G.number_of_edges()} edges"
        )

    def compute_shortest_path(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        weight: str = DEFAULT_WEIGHT,
    ) -> Dict[str, Any]:
        """
        Compute shortest path between two geographic coordinates.

        Maps the input coordinates to the nearest graph nodes, then computes
        the shortest path using Dijkstra's algorithm weighted by edge length.

        Args:
            origin_lat: Origin latitude in decimal degrees
            origin_lon: Origin longitude in decimal degrees
            dest_lat: Destination latitude in decimal degrees
            dest_lon: Destination longitude in decimal degrees
            weight: Edge attribute to use for routing (default: 'length')

        Returns:
            Dictionary with routing result:
            {
                'success': bool,
                'path': List[int],              # List of node IDs
                'nodes': List[Tuple[float, float]],  # List of (lat, lon)
                'distance': float,              # Total distance in meters
                'origin_node': int,
                'dest_node': int,
                'origin_coords': Tuple[float, float],
                'dest_coords': Tuple[float, float],
                'computation_time': float,      # Seconds
                'message': str,
            }

        Example:
            >>> router = Router(G, mapper)
            >>> result = router.compute_shortest_path(
            ...     40.9856, 29.0298,  # Moda
            ...     40.9638, 29.0408   # Fenerbahçe
            ... )
            >>> if result['success']:
            ...     print(f"Route distance: {result['distance']:.2f} m")
            Route distance: 2534.50 m
        """
        start_time = time.time()

        # Validate input coordinates
        if not validate_coordinates(origin_lat, origin_lon):
            return self._create_error_result(
                f"Invalid origin coordinates: "
                f"{format_coordinates(origin_lat, origin_lon)}",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )

        if not validate_coordinates(dest_lat, dest_lon):
            return self._create_error_result(
                f"Invalid destination coordinates: "
                f"{format_coordinates(dest_lat, dest_lon)}",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )

        # Check if origin and destination are the same
        if abs(origin_lat - dest_lat) < 1e-6 and abs(origin_lon - dest_lon) < 1e-6:
            return self._create_error_result(
                "Origin and destination are the same location",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )

        # Map coordinates to nodes
        logger.info(
            f"Finding route from {format_coordinates(origin_lat, origin_lon)} "
            f"to {format_coordinates(dest_lat, dest_lon)}"
        )

        origin_node = self.node_mapper.find_nearest_node(origin_lat, origin_lon)
        if origin_node is None:
            return self._create_error_result(
                "Could not map origin coordinates to road network",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )

        dest_node = self.node_mapper.find_nearest_node(dest_lat, dest_lon)
        if dest_node is None:
            return self._create_error_result(
                "Could not map destination coordinates to road network",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )

        logger.info(f"Origin node: {origin_node}, Destination node: {dest_node}")

        # Check if nodes are the same
        if origin_node == dest_node:
            return self._create_error_result(
                "Origin and destination map to the same road intersection",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )

        # Compute shortest path
        try:
            path = nx.shortest_path(
                self.graph,
                source=origin_node,
                target=dest_node,
                weight=weight,
                method='dijkstra',
            )
        except nx.NetworkXNoPath:
            return self._create_error_result(
                "No path exists between origin and destination "
                "(nodes are in disconnected components)",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
                origin_node=origin_node,
                dest_node=dest_node,
            )
        except nx.NodeNotFound as e:
            return self._create_error_result(
                f"Node not found in graph: {str(e)}",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )
        except Exception as e:
            return self._create_error_result(
                f"Routing error: {str(e)}",
                origin_lat,
                origin_lon,
                dest_lat,
                dest_lon,
            )

        # Extract path coordinates
        path_coords = self.get_path_coordinates(path)

        # Calculate total distance
        distance = self.compute_path_length(path, weight)

        # Calculate computation time
        computation_time = time.time() - start_time

        if ENABLE_PERFORMANCE_LOGGING:
            logger.info(
                f"Route computed in {format_time(computation_time)}: "
                f"{len(path)} nodes, {format_distance(distance)}"
            )

        return {
            'success': True,
            'path': path,
            'nodes': path_coords,
            'distance': distance,
            'origin_node': origin_node,
            'dest_node': dest_node,
            'origin_coords': (origin_lat, origin_lon),
            'dest_coords': (dest_lat, dest_lon),
            'computation_time': computation_time,
            'message': f"Route found: {format_distance(distance)}, {len(path)} nodes",
        }

    def compute_path_length(
        self, path: List[int], weight: str = DEFAULT_WEIGHT
    ) -> float:
        """
        Calculate total length of a path.

        Args:
            path: List of node IDs forming the path
            weight: Edge attribute to use for length calculation

        Returns:
            Total path length in the units of the weight attribute

        Example:
            >>> path = [1, 2, 3, 4]
            >>> length = router.compute_path_length(path)
            >>> print(f"Path length: {length:.2f} meters")
            Path length: 2534.50 meters
        """
        if len(path) < 2:
            return 0.0

        return compute_path_total_length(self.graph, path, weight)

    def get_path_coordinates(
        self, path: List[int]
    ) -> List[Tuple[float, float]]:
        """
        Extract latitude/longitude coordinates for a path.

        Args:
            path: List of node IDs forming the path

        Returns:
            List of (latitude, longitude) tuples

        Example:
            >>> path = [1, 2, 3]
            >>> coords = router.get_path_coordinates(path)
            >>> for lat, lon in coords:
            ...     print(f"({lat:.6f}, {lon:.6f})")
        """
        coords = []
        for node_id in path:
            lat, lon = self.node_mapper.get_node_coordinates(node_id)
            coords.append((lat, lon))
        return coords

    def is_path_valid(self, origin_node: int, dest_node: int) -> bool:
        """
        Check if a path exists between two nodes.

        Args:
            origin_node: Origin node ID
            dest_node: Destination node ID

        Returns:
            True if path exists, False otherwise

        Example:
            >>> if router.is_path_valid(origin_node, dest_node):
            ...     print("Path exists!")
        """
        try:
            nx.has_path(self.graph, origin_node, dest_node)
            return True
        except nx.NodeNotFound:
            return False

    def _create_error_result(
        self,
        message: str,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        origin_node: Optional[int] = None,
        dest_node: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a standardized error result dictionary.

        Args:
            message: Error message
            origin_lat: Origin latitude
            origin_lon: Origin longitude
            dest_lat: Destination latitude
            dest_lon: Destination longitude
            origin_node: Origin node ID (if mapped)
            dest_node: Destination node ID (if mapped)

        Returns:
            Error result dictionary
        """
        logger.warning(f"Routing failed: {message}")

        return {
            'success': False,
            'path': [],
            'nodes': [],
            'distance': 0.0,
            'origin_node': origin_node,
            'dest_node': dest_node,
            'origin_coords': (origin_lat, origin_lon),
            'dest_coords': (dest_lat, dest_lon),
            'computation_time': 0.0,
            'message': message,
        }

    def get_route_summary(self, result: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of a routing result.

        Args:
            result: Routing result dictionary from compute_shortest_path()

        Returns:
            Formatted summary string

        Example:
            >>> result = router.compute_shortest_path(40.9856, 29.0298, 40.9638, 29.0408)
            >>> print(router.get_route_summary(result))
            Route: 2.53 km, 45 nodes, computed in 0.05 s
        """
        if not result['success']:
            return f"Routing failed: {result['message']}"

        return (
            f"Route: {format_distance(result['distance'])}, "
            f"{len(result['path'])} nodes, "
            f"computed in {format_time(result['computation_time'])}"
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def compute_route(
    G: nx.MultiDiGraph,
    mapper: NodeMapper,
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    weight: str = DEFAULT_WEIGHT,
) -> Dict[str, Any]:
    """
    Convenience function to compute a route quickly.

    Args:
        G: NetworkX road network graph
        mapper: NodeMapper instance
        origin: Tuple of (latitude, longitude) for origin
        destination: Tuple of (latitude, longitude) for destination
        weight: Edge attribute to use for routing

    Returns:
        Routing result dictionary

    Example:
        >>> origin = (40.9856, 29.0298)
        >>> dest = (40.9638, 29.0408)
        >>> result = compute_route(G, mapper, origin, dest)
        >>> if result['success']:
        ...     print(f"Distance: {result['distance']:.2f} m")
    """
    router = Router(G, mapper)
    return router.compute_shortest_path(
        origin[0], origin[1], destination[0], destination[1], weight=weight
    )
