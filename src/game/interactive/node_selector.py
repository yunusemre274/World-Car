"""
Node selector for interactive map clicking.

Handles mouse clicks on the map and snaps them to the nearest graph node
using efficient spatial indexing (KD-tree).
"""

from typing import Tuple, Optional, Dict
import networkx as nx
from scipy.spatial import KDTree
import numpy as np


class NodeSelector:
    """
    Selects graph nodes from mouse click positions.

    Uses KD-tree spatial indexing for O(log n) nearest neighbor queries.
    This is critical for real-time interaction on large graphs (10k+ nodes).

    Example:
        >>> selector = NodeSelector(graph, max_distance=100)
        >>> node = selector.select_node(click_lon, click_lat)
        >>> if node is not None:
        >>>     print(f"Selected node {node}")
    """

    def __init__(self, graph: nx.MultiDiGraph, max_distance: float = 100.0):
        """
        Initialize the node selector.

        Args:
            graph: Road network graph
            max_distance: Maximum distance (meters) for snapping to node.
                         If click is farther than this, no node is selected.

        Note:
            The KD-tree is built once during initialization for efficiency.
        """
        self.graph = graph
        self.max_distance = max_distance

        # Build node position mappings
        self.node_positions: Dict[int, Tuple[float, float]] = {}
        self.nodes = []
        self.coordinates = []

        for node in graph.nodes:
            lon = graph.nodes[node]["x"]
            lat = graph.nodes[node]["y"]
            self.node_positions[node] = (lon, lat)
            self.nodes.append(node)
            self.coordinates.append([lon, lat])

        # Build KD-tree for O(log n) nearest neighbor queries
        self.coordinates = np.array(self.coordinates)
        self.kdtree = KDTree(self.coordinates)

        print(f"NodeSelector initialized:")
        print(f"  Nodes indexed: {len(self.nodes)}")
        print(f"  Max snap distance: {max_distance}m")

    def select_node(self, click_lon: float, click_lat: float) -> Optional[int]:
        """
        Select the nearest graph node to a click position.

        Args:
            click_lon: Click longitude (x coordinate)
            click_lat: Click latitude (y coordinate)

        Returns:
            Node ID if found within max_distance, None otherwise
        """
        # Query KD-tree for nearest node
        distance, index = self.kdtree.query([click_lon, click_lat])

        # Convert coordinate distance to approximate meters
        # This is a rough approximation; for more accuracy, use Haversine
        meters_distance = self._approximate_distance_to_meters(
            distance, click_lat
        )

        if meters_distance <= self.max_distance:
            selected_node = self.nodes[index]
            print(f"Node selected: {selected_node} (distance: {meters_distance:.1f}m)")
            return selected_node
        else:
            print(f"Click too far from any node ({meters_distance:.1f}m > {self.max_distance}m)")
            return None

    def get_node_position(self, node: int) -> Tuple[float, float]:
        """
        Get the (lon, lat) position of a node.

        Args:
            node: Node ID

        Returns:
            Tuple of (longitude, latitude)

        Raises:
            KeyError: If node doesn't exist
        """
        return self.node_positions[node]

    def find_nodes_in_radius(self, center_lon: float, center_lat: float,
                             radius: float) -> list:
        """
        Find all nodes within a radius of a point.

        Args:
            center_lon: Center longitude
            center_lat: Center latitude
            radius: Search radius in meters

        Returns:
            List of node IDs within radius
        """
        # Convert meters to approximate coordinate distance
        coord_radius = self._meters_to_coordinate_distance(radius, center_lat)

        # Query KD-tree for all points within radius
        indices = self.kdtree.query_ball_point([center_lon, center_lat], coord_radius)

        return [self.nodes[i] for i in indices]

    def _approximate_distance_to_meters(self, coord_distance: float,
                                       latitude: float) -> float:
        """
        Convert coordinate distance to approximate meters.

        Uses simple equirectangular approximation. Good enough for
        click-to-node snapping within a city.

        Args:
            coord_distance: Distance in coordinate units (degrees)
            latitude: Latitude for correction factor

        Returns:
            Approximate distance in meters
        """
        # At equator, 1 degree ≈ 111km
        # Adjust for latitude (longitude lines converge at poles)
        meters_per_degree_lat = 111000
        meters_per_degree_lon = 111000 * np.cos(np.radians(latitude))

        # Approximate as Euclidean (good enough for small distances)
        meters = coord_distance * np.sqrt(
            meters_per_degree_lat * meters_per_degree_lon
        )
        return meters

    def _meters_to_coordinate_distance(self, meters: float,
                                      latitude: float) -> float:
        """
        Convert meters to approximate coordinate distance.

        Args:
            meters: Distance in meters
            latitude: Latitude for correction factor

        Returns:
            Approximate distance in coordinate units (degrees)
        """
        meters_per_degree_lat = 111000
        meters_per_degree_lon = 111000 * np.cos(np.radians(latitude))

        # Use average of lat and lon conversion
        avg_meters_per_degree = np.sqrt(
            meters_per_degree_lat * meters_per_degree_lon
        )
        return meters / avg_meters_per_degree

    def is_valid_pair(self, start_node: int, target_node: int) -> bool:
        """
        Check if start and target form a valid pair.

        Args:
            start_node: Start node ID
            target_node: Target node ID

        Returns:
            True if valid pair (different nodes, both exist)
        """
        if start_node == target_node:
            print("Warning: Start and target are the same node")
            return False

        if start_node not in self.node_positions:
            print(f"Error: Start node {start_node} not in graph")
            return False

        if target_node not in self.node_positions:
            print(f"Error: Target node {target_node} not in graph")
            return False

        return True

    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the node selector.

        Returns:
            Dictionary with stats (node count, index size, etc.)
        """
        return {
            "nodes_indexed": len(self.nodes),
            "max_snap_distance_m": self.max_distance,
            "kdtree_depth": int(np.log2(len(self.nodes))),
            "memory_kb": self.coordinates.nbytes / 1024
        }
