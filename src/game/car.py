"""
Car entity for pathfinding simulation.

The car represents a vehicle traversing a computed path on a road network.
It moves node-by-node at a fixed rate, independent of the pathfinding algorithm.
"""

from typing import List, Optional, Tuple
import networkx as nx


class Car:
    """
    A car entity that traverses a precomputed path on a road network.

    The car maintains its current position and advances one node per tick.
    It is decoupled from the pathfinding algorithm - it simply follows
    the provided path.

    Attributes:
        path: List of node IDs representing the route
        current_index: Current position in the path (0-based)
        total_distance_traveled: Cumulative distance traveled in meters
        is_finished: Whether the car has reached the destination
    """

    def __init__(self, path: List[int], graph: nx.MultiDiGraph):
        """
        Initialize a car with a path to follow.

        Args:
            path: Ordered list of node IDs to traverse
            graph: Road network graph for distance calculations

        Raises:
            ValueError: If path is empty or invalid
        """
        if not path or len(path) == 0:
            raise ValueError("Path cannot be empty")

        self.path = path
        self.graph = graph
        self.current_index = 0
        self.total_distance_traveled = 0.0
        self._finished = False

    @property
    def current_node(self) -> int:
        """Get the current node ID."""
        return self.path[self.current_index]

    @property
    def is_finished(self) -> bool:
        """Check if the car has reached the destination."""
        return self._finished

    @property
    def progress(self) -> float:
        """Get progress as a percentage (0.0 to 1.0)."""
        if len(self.path) <= 1:
            return 1.0
        return self.current_index / (len(self.path) - 1)

    @property
    def nodes_remaining(self) -> int:
        """Get number of nodes remaining to destination."""
        return len(self.path) - self.current_index - 1

    def get_position(self) -> Tuple[float, float]:
        """
        Get current position as (longitude, latitude).

        Returns:
            Tuple of (lon, lat) coordinates
        """
        node_data = self.graph.nodes[self.current_node]
        return (node_data["x"], node_data["y"])

    def advance(self) -> bool:
        """
        Advance the car to the next node in the path.

        Returns:
            True if successfully advanced, False if already at destination

        Updates:
            - current_index
            - total_distance_traveled
            - is_finished flag
        """
        if self._finished:
            return False

        # Check if we're at the last node
        if self.current_index >= len(self.path) - 1:
            self._finished = True
            return False

        # Calculate distance of this segment
        current = self.path[self.current_index]
        next_node = self.path[self.current_index + 1]
        segment_distance = self._get_edge_length(current, next_node)

        # Update state
        self.current_index += 1
        self.total_distance_traveled += segment_distance

        # Check if we've reached the destination
        if self.current_index >= len(self.path) - 1:
            self._finished = True

        return True

    def reset(self) -> None:
        """Reset the car to the start of the path."""
        self.current_index = 0
        self.total_distance_traveled = 0.0
        self._finished = False

    def _get_edge_length(self, u: int, v: int) -> float:
        """
        Get the length of the edge between two nodes.

        For MultiDiGraph, selects the minimum length edge.

        Args:
            u: Source node ID
            v: Target node ID

        Returns:
            Edge length in meters
        """
        try:
            edges = self.graph[u][v]
            if len(edges) == 1:
                return edges[0].get("length", 0.0)
            else:
                return min(edge.get("length", float("inf")) for edge in edges.values())
        except KeyError:
            # Edge doesn't exist - should not happen with valid path
            return 0.0

    def get_stats(self) -> dict:
        """
        Get current statistics about the car's journey.

        Returns:
            Dictionary containing:
                - current_node: Current node ID
                - progress_pct: Progress percentage
                - distance_traveled: Distance traveled in meters
                - nodes_visited: Number of nodes visited
                - nodes_remaining: Number of nodes to destination
                - is_finished: Whether journey is complete
        """
        return {
            "current_node": self.current_node,
            "progress_pct": self.progress * 100,
            "distance_traveled": self.total_distance_traveled,
            "nodes_visited": self.current_index + 1,
            "nodes_remaining": self.nodes_remaining,
            "is_finished": self.is_finished
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"Car(node={self.current_node}, "
                f"progress={self.progress:.1%}, "
                f"distance={self.total_distance_traveled:.1f}m, "
                f"finished={self.is_finished})")
