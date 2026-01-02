"""
Node Mapper Module for WorldCar routing system.

This module provides efficient mapping from geographic coordinates (latitude, longitude)
to graph nodes using spatial indexing with KDTree for O(log n) nearest neighbor queries.
"""

import logging
from typing import Optional, Tuple, Dict, Any

import networkx as nx
import numpy as np
from scipy.spatial import KDTree

from worldcar.config import MAX_SEARCH_RADIUS_METERS, KDTREE_ENABLED
from worldcar.utils import (
    validate_coordinates,
    haversine_distance,
    format_coordinates,
    format_distance,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeMapper:
    """
    Maps geographic coordinates to graph nodes efficiently.

    Uses KDTree spatial indexing for fast O(log n) nearest neighbor search.
    This allows quick mapping of arbitrary latitude/longitude coordinates to
    the nearest node in the road network graph.

    Attributes:
        graph (nx.MultiDiGraph): The road network graph
        node_coords (np.ndarray): Array of (lat, lon) for each node
        node_ids (list): List of node IDs corresponding to node_coords
        kdtree (KDTree): Spatial index for fast nearest neighbor queries

    Example:
        >>> mapper = NodeMapper(G)
        >>> node_id = mapper.find_nearest_node(40.9856, 29.0298)
        >>> if node_id is not None:
        ...     print(f"Nearest node: {node_id}")
        Nearest node: 123456789
    """

    def __init__(self, G: nx.MultiDiGraph):
        """
        Initialize NodeMapper with a graph.

        Extracts node coordinates and builds a KDTree spatial index
        for efficient nearest neighbor queries.

        Args:
            G: NetworkX graph with node attributes 'x' (longitude) and 'y' (latitude)

        Raises:
            ValueError: If graph has no nodes or missing coordinate attributes
        """
        self.graph = G
        self.node_coords: Optional[np.ndarray] = None
        self.node_ids: Optional[list] = None
        self.kdtree: Optional[KDTree] = None

        if G.number_of_nodes() == 0:
            raise ValueError("Cannot create NodeMapper from empty graph")

        logger.info(
            f"Initializing NodeMapper for graph with {G.number_of_nodes()} nodes"
        )

        # Build spatial index
        self._build_spatial_index()

        logger.info("NodeMapper initialized successfully")

    def _build_spatial_index(self) -> None:
        """
        Build KDTree spatial index for fast nearest neighbor search.

        Extracts coordinates from all nodes and constructs a KDTree
        for efficient O(log n) nearest neighbor queries.

        Raises:
            ValueError: If nodes are missing coordinate attributes
        """
        logger.info("Building spatial index...")

        # Extract node IDs and coordinates
        node_ids = []
        node_coords = []

        for node_id, data in self.graph.nodes(data=True):
            if 'y' not in data or 'x' not in data:
                raise ValueError(
                    f"Node {node_id} missing coordinate attributes (x, y)"
                )

            lat = data['y']
            lon = data['x']

            node_ids.append(node_id)
            node_coords.append([lat, lon])

        # Convert to numpy arrays
        self.node_ids = node_ids
        self.node_coords = np.array(node_coords)

        # Build KDTree for fast nearest neighbor search
        if KDTREE_ENABLED:
            self.kdtree = KDTree(self.node_coords)
            logger.info(
                f"KDTree built successfully with {len(self.node_ids)} nodes"
            )
        else:
            logger.info(
                "KDTree disabled in config. Using brute-force search (slower)."
            )

    def find_nearest_node(
        self,
        lat: float,
        lon: float,
        max_distance: float = MAX_SEARCH_RADIUS_METERS,
    ) -> Optional[int]:
        """
        Find the nearest graph node to given coordinates.

        Uses KDTree for fast O(log n) nearest neighbor search. Returns None
        if the nearest node is further than max_distance.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            max_distance: Maximum search radius in meters (default from config)

        Returns:
            Node ID of nearest node, or None if no node within max_distance

        Example:
            >>> mapper = NodeMapper(G)
            >>> node = mapper.find_nearest_node(40.9856, 29.0298)
            >>> if node is not None:
            ...     print(f"Found node: {node}")
            Found node: 123456789
        """
        # Validate coordinates
        if not validate_coordinates(lat, lon):
            logger.warning(f"Invalid coordinates: {format_coordinates(lat, lon)}")
            return None

        query_point = np.array([lat, lon])

        if KDTREE_ENABLED and self.kdtree is not None:
            # Use KDTree for fast search
            distance, index = self.kdtree.query(query_point)

            # KDTree returns distance in coordinate units (degrees)
            # Convert to meters using Haversine
            nearest_lat, nearest_lon = self.node_coords[index]
            distance_meters = haversine_distance(lat, lon, nearest_lat, nearest_lon)

        else:
            # Brute force search (slower, but works without KDTree)
            distances = np.array([
                haversine_distance(lat, lon, node_lat, node_lon)
                for node_lat, node_lon in self.node_coords
            ])
            index = np.argmin(distances)
            distance_meters = distances[index]

        # Check if within max distance
        if distance_meters > max_distance:
            logger.warning(
                f"No node found within {format_distance(max_distance)} "
                f"of {format_coordinates(lat, lon)}. "
                f"Nearest node is {format_distance(distance_meters)} away."
            )
            return None

        node_id = self.node_ids[index]
        logger.debug(
            f"Found nearest node {node_id} at {format_distance(distance_meters)}"
        )

        return node_id

    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        """
        Get latitude and longitude coordinates for a node.

        Args:
            node_id: Node ID in the graph

        Returns:
            Tuple of (latitude, longitude)

        Raises:
            ValueError: If node_id doesn't exist in graph

        Example:
            >>> mapper = NodeMapper(G)
            >>> lat, lon = mapper.get_node_coordinates(123456789)
            >>> print(f"Node coordinates: {lat:.6f}, {lon:.6f}")
            Node coordinates: 40.985600, 29.029800
        """
        if node_id not in self.graph:
            raise ValueError(f"Node {node_id} not found in graph")

        data = self.graph.nodes[node_id]
        lat = data['y']
        lon = data['x']

        return lat, lon

    def snap_to_network(
        self,
        lat: float,
        lon: float,
        max_distance: float = MAX_SEARCH_RADIUS_METERS,
    ) -> Dict[str, Any]:
        """
        Snap coordinates to the road network and return detailed information.

        Finds the nearest node and returns comprehensive information about
        the snapping operation, including the node ID, its coordinates,
        and the distance from the query point.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            max_distance: Maximum search radius in meters

        Returns:
            Dictionary with snapping information:
            {
                'success': bool,
                'node_id': int or None,
                'node_lat': float or None,
                'node_lon': float or None,
                'distance': float or None (meters),
                'query_lat': float,
                'query_lon': float,
                'message': str
            }

        Example:
            >>> mapper = NodeMapper(G)
            >>> result = mapper.snap_to_network(40.9856, 29.0298)
            >>> if result['success']:
            ...     print(f"Snapped to node {result['node_id']}")
            Snapped to node 123456789
        """
        # Validate input coordinates
        if not validate_coordinates(lat, lon):
            return {
                'success': False,
                'node_id': None,
                'node_lat': None,
                'node_lon': None,
                'distance': None,
                'query_lat': lat,
                'query_lon': lon,
                'message': f"Invalid coordinates: {format_coordinates(lat, lon)}",
            }

        # Find nearest node
        node_id = self.find_nearest_node(lat, lon, max_distance)

        if node_id is None:
            return {
                'success': False,
                'node_id': None,
                'node_lat': None,
                'node_lon': None,
                'distance': None,
                'query_lat': lat,
                'query_lon': lon,
                'message': (
                    f"No node found within {format_distance(max_distance)} "
                    f"of {format_coordinates(lat, lon)}"
                ),
            }

        # Get node coordinates
        node_lat, node_lon = self.get_node_coordinates(node_id)

        # Calculate distance
        distance = haversine_distance(lat, lon, node_lat, node_lon)

        return {
            'success': True,
            'node_id': node_id,
            'node_lat': node_lat,
            'node_lon': node_lon,
            'distance': distance,
            'query_lat': lat,
            'query_lon': lon,
            'message': (
                f"Snapped to node {node_id} at {format_distance(distance)}"
            ),
        }

    def batch_find_nearest_nodes(
        self,
        coordinates: list[Tuple[float, float]],
        max_distance: float = MAX_SEARCH_RADIUS_METERS,
    ) -> list[Optional[int]]:
        """
        Find nearest nodes for multiple coordinates efficiently.

        Args:
            coordinates: List of (latitude, longitude) tuples
            max_distance: Maximum search radius in meters

        Returns:
            List of node IDs (or None if no node within max_distance)

        Example:
            >>> mapper = NodeMapper(G)
            >>> coords = [(40.9856, 29.0298), (40.9638, 29.0408)]
            >>> nodes = mapper.batch_find_nearest_nodes(coords)
            >>> print(f"Found {len([n for n in nodes if n is not None])} nodes")
            Found 2 nodes
        """
        logger.info(f"Batch finding nearest nodes for {len(coordinates)} coordinates")

        results = []
        for lat, lon in coordinates:
            node_id = self.find_nearest_node(lat, lon, max_distance)
            results.append(node_id)

        found = len([n for n in results if n is not None])
        logger.info(f"Found nearest nodes for {found}/{len(coordinates)} coordinates")

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the NodeMapper.

        Returns:
            Dictionary with mapper statistics

        Example:
            >>> mapper = NodeMapper(G)
            >>> stats = mapper.get_stats()
            >>> print(f"Indexed {stats['num_nodes']} nodes")
            Indexed 12453 nodes
        """
        return {
            'num_nodes': len(self.node_ids) if self.node_ids else 0,
            'kdtree_enabled': KDTREE_ENABLED and self.kdtree is not None,
            'max_search_radius_m': MAX_SEARCH_RADIUS_METERS,
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def create_node_mapper(G: nx.MultiDiGraph) -> NodeMapper:
    """
    Convenience function to create a NodeMapper.

    Args:
        G: NetworkX graph with road network

    Returns:
        Initialized NodeMapper instance

    Example:
        >>> mapper = create_node_mapper(G)
        >>> node = mapper.find_nearest_node(40.9856, 29.0298)
    """
    return NodeMapper(G)
