"""
Path interpolator for smooth car movement.

Converts a discrete node path into a continuous interpolated trajectory.
Supports multiple interpolation methods for different visual effects.
"""

from typing import List, Tuple, Optional
import numpy as np
from scipy.interpolate import interp1d
from enum import Enum
import networkx as nx


class InterpolationMethod(Enum):
    """
    Interpolation methods for path smoothing.

    LINEAR: Straight lines between nodes (fastest, most accurate to road)
    CUBIC: Smooth cubic spline (looks smoother but may cut corners)
    QUADRATIC: Quadratic spline (balance between linear and cubic)
    """
    LINEAR = 'linear'
    CUBIC = 'cubic'
    QUADRATIC = 'quadratic'


class PathInterpolator:
    """
    Interpolates a discrete node path into smooth coordinates.

    Takes a path (list of node IDs) and generates interpolated positions
    for smooth animation. The number of interpolation steps can be adjusted
    to control animation smoothness vs performance.

    Example:
        >>> interpolator = PathInterpolator(graph, path)
        >>> coordinates = interpolator.interpolate(steps_per_edge=20)
        >>> for x, y in coordinates:
        >>>     # Animate car at (x, y)
    """

    def __init__(self, graph: nx.MultiDiGraph, path: List[int]):
        """
        Initialize the path interpolator.

        Args:
            graph: Road network graph with node coordinates
            path: List of node IDs representing the computed path

        Raises:
            ValueError: If path is empty or invalid
        """
        if not path or len(path) == 0:
            raise ValueError("Path cannot be empty")

        self.graph = graph
        self.path = path

        # Extract node coordinates
        self.node_coords = self._extract_coordinates()

        # Calculate path statistics
        self.total_distance = self._calculate_total_distance()
        self.num_edges = len(path) - 1

    def _extract_coordinates(self) -> List[Tuple[float, float]]:
        """
        Extract (x, y) coordinates from node IDs.

        Returns:
            List of (longitude, latitude) tuples
        """
        coords = []
        for node in self.path:
            node_data = self.graph.nodes[node]
            coords.append((node_data['x'], node_data['y']))
        return coords

    def _calculate_total_distance(self) -> float:
        """
        Calculate total path distance in meters.

        Returns:
            Total distance using edge lengths
        """
        total = 0.0
        for i in range(len(self.path) - 1):
            current = self.path[i]
            next_node = self.path[i + 1]

            # Get edge length (handle MultiDiGraph)
            edges = self.graph[current][next_node]
            if len(edges) == 1:
                length = edges[0].get('length', 0.0)
            else:
                length = min(edge.get('length', float('inf'))
                           for edge in edges.values())
            total += length

        return total

    def interpolate(self,
                   steps_per_edge: int = 20,
                   method: InterpolationMethod = InterpolationMethod.LINEAR) -> np.ndarray:
        """
        Interpolate the path into smooth coordinates.

        Args:
            steps_per_edge: Number of interpolation points per edge
                           (higher = smoother but slower)
            method: Interpolation method to use

        Returns:
            Numpy array of shape (N, 2) containing [x, y] coordinates
            where N = (num_edges * steps_per_edge) + 1

        Example:
            >>> coords = interpolator.interpolate(steps_per_edge=30)
            >>> # coords[0] is start, coords[-1] is end
            >>> # coords has (num_edges * 30) + 1 points total
        """
        if len(self.path) == 1:
            # Single node path - no interpolation needed
            return np.array([self.node_coords[0]])

        # Separate x and y coordinates
        x_coords = [coord[0] for coord in self.node_coords]
        y_coords = [coord[1] for coord in self.node_coords]

        # Parameter t goes from 0 to num_edges
        t_original = np.arange(len(self.path))

        # Create interpolation functions
        if method == InterpolationMethod.LINEAR:
            # Linear interpolation - follows road segments exactly
            fx = interp1d(t_original, x_coords, kind='linear')
            fy = interp1d(t_original, y_coords, kind='linear')

        elif method == InterpolationMethod.CUBIC:
            # Cubic spline - smooth but may cut corners
            # Requires at least 4 points
            if len(self.path) >= 4:
                fx = interp1d(t_original, x_coords, kind='cubic')
                fy = interp1d(t_original, y_coords, kind='cubic')
            else:
                # Fall back to quadratic for short paths
                fx = interp1d(t_original, x_coords, kind='quadratic')
                fy = interp1d(t_original, y_coords, kind='quadratic')

        elif method == InterpolationMethod.QUADRATIC:
            # Quadratic spline - balance between linear and cubic
            # Requires at least 3 points
            if len(self.path) >= 3:
                fx = interp1d(t_original, x_coords, kind='quadratic')
                fy = interp1d(t_original, y_coords, kind='quadratic')
            else:
                # Fall back to linear
                fx = interp1d(t_original, x_coords, kind='linear')
                fy = interp1d(t_original, y_coords, kind='linear')

        else:
            raise ValueError(f"Unknown interpolation method: {method}")

        # Generate interpolated points
        total_steps = self.num_edges * steps_per_edge + 1
        t_interp = np.linspace(0, self.num_edges, total_steps)

        x_interp = fx(t_interp)
        y_interp = fy(t_interp)

        # Combine into coordinate array
        coords = np.column_stack([x_interp, y_interp])

        return coords

    def interpolate_by_distance(self,
                                step_distance: float = 10.0,
                                method: InterpolationMethod = InterpolationMethod.LINEAR) -> np.ndarray:
        """
        Interpolate path with fixed distance between points.

        This ensures constant speed animation regardless of node spacing.

        Args:
            step_distance: Distance in meters between interpolated points
            method: Interpolation method to use

        Returns:
            Numpy array of interpolated coordinates

        Example:
            >>> # Generate a point every 10 meters
            >>> coords = interpolator.interpolate_by_distance(step_distance=10.0)
        """
        # Calculate steps per edge based on total distance
        if self.total_distance <= 0:
            return np.array([self.node_coords[0]])

        # Estimate steps needed
        total_steps = int(self.total_distance / step_distance) + 1
        steps_per_edge = max(1, total_steps // max(1, self.num_edges))

        return self.interpolate(steps_per_edge=steps_per_edge, method=method)

    def get_segment_info(self, index: int) -> dict:
        """
        Get information about a specific edge segment.

        Args:
            index: Edge index (0 to num_edges - 1)

        Returns:
            Dictionary with segment information
        """
        if index < 0 or index >= self.num_edges:
            raise ValueError(f"Invalid segment index: {index}")

        current_node = self.path[index]
        next_node = self.path[index + 1]

        # Get edge length
        edges = self.graph[current_node][next_node]
        if len(edges) == 1:
            length = edges[0].get('length', 0.0)
        else:
            length = min(edge.get('length', float('inf'))
                       for edge in edges.values())

        return {
            'index': index,
            'start_node': current_node,
            'end_node': next_node,
            'start_coord': self.node_coords[index],
            'end_coord': self.node_coords[index + 1],
            'length_meters': length
        }

    def get_stats(self) -> dict:
        """
        Get statistics about the path.

        Returns:
            Dictionary with path statistics
        """
        return {
            'num_nodes': len(self.path),
            'num_edges': self.num_edges,
            'total_distance_m': self.total_distance,
            'start_coord': self.node_coords[0],
            'end_coord': self.node_coords[-1]
        }
