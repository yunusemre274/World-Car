"""
Algorithm Visualization Renderer

Renders the step-by-step execution of pathfinding algorithms.
Shows explored nodes, frontier (open set), current path, and progress.
"""

from typing import List, Dict, Set, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import networkx as nx
import osmnx as ox


class AlgorithmRenderer:
    """
    Renders step-by-step algorithm execution for educational visualization.

    Shows:
    - Explored/visited nodes (gray)
    - Frontier/open set nodes (yellow)
    - Current node being explored (red)
    - Current path to node (blue)
    - Target node (orange star)
    - Progress statistics
    """

    # Visual configuration
    NETWORK_COLOR = "#f0f0f0"
    NETWORK_WIDTH = 0.4

    VISITED_COLOR = "#cccccc"      # Gray - already explored
    VISITED_SIZE = 20
    VISITED_ALPHA = 0.6

    FRONTIER_COLOR = "#ffeb3b"     # Yellow - in open set
    FRONTIER_SIZE = 40
    FRONTIER_ALPHA = 0.8

    CURRENT_COLOR = "#ff1744"      # Red - currently exploring
    CURRENT_SIZE = 120
    CURRENT_EDGE_COLOR = "white"
    CURRENT_EDGE_WIDTH = 2

    PATH_COLOR = "#2196f3"         # Blue - current path
    PATH_WIDTH = 2.5
    PATH_ALPHA = 0.8

    FINAL_PATH_COLOR = "#00ff00"   # Green - final path
    FINAL_PATH_WIDTH = 4.0
    FINAL_PATH_ALPHA = 0.9

    SOURCE_COLOR = "#00e676"       # Light green
    SOURCE_SIZE = 100

    TARGET_COLOR = "#ff9100"       # Orange
    TARGET_SIZE = 140
    TARGET_MARKER = "*"

    def __init__(self, graph: nx.MultiDiGraph, figsize=(14, 11)):
        """
        Initialize the algorithm renderer.

        Args:
            graph: Road network graph
            figsize: Figure size as (width, height)
        """
        self.graph = graph
        self.figsize = figsize

        # Create figure
        self.fig: Optional[Figure] = None
        self.ax: Optional[Axes] = None

        # Cached positions
        self.node_positions = {
            node: (self.graph.nodes[node]["x"], self.graph.nodes[node]["y"])
            for node in self.graph.nodes
        }

        # Artist objects for updating
        self._visited_artist = None
        self._frontier_artist = None
        self._current_artist = None
        self._path_artist = None
        self._final_path_artist = None
        self._stats_text = None
        self._initialized = False

    def initialize(self, source: int, target: int, algorithm_name: str = "A*") -> None:
        """
        Initialize the visualization.

        Args:
            source: Source node ID
            target: Target node ID
            algorithm_name: Name of algorithm for display
        """
        if self._initialized:
            return

        # Create figure
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.fig.canvas.manager.set_window_title(f"WorldCar - {algorithm_name} Visualization")

        # Draw base network
        self._draw_network()

        # Draw source and target
        self._draw_endpoints(source, target)

        # Setup stats display
        self._setup_stats_display()

        # Configure axes
        self.ax.set_xlabel("Longitude", fontsize=10)
        self.ax.set_ylabel("Latitude", fontsize=10)
        self.ax.set_title(
            f"{algorithm_name} - Step-by-Step Exploration",
            fontsize=14,
            fontweight="bold",
            pad=15
        )

        self._initialized = True
        plt.draw()

    def _draw_network(self) -> None:
        """Draw the base road network."""
        ox.plot_graph(
            self.graph,
            ax=self.ax,
            show=False,
            close=False,
            node_size=0,
            edge_color=self.NETWORK_COLOR,
            edge_linewidth=self.NETWORK_WIDTH
        )

    def _draw_endpoints(self, source: int, target: int) -> None:
        """
        Draw source and target markers.

        Args:
            source: Source node ID
            target: Target node ID
        """
        source_pos = self.node_positions[source]
        target_pos = self.node_positions[target]

        # Source
        self.ax.scatter(
            source_pos[0], source_pos[1],
            c=self.SOURCE_COLOR,
            s=self.SOURCE_SIZE,
            marker='o',
            edgecolors='white',
            linewidths=2,
            zorder=6,
            label="Start"
        )

        # Target
        self.ax.scatter(
            target_pos[0], target_pos[1],
            c=self.TARGET_COLOR,
            s=self.TARGET_SIZE,
            marker=self.TARGET_MARKER,
            edgecolors='white',
            linewidths=2,
            zorder=6,
            label="Target"
        )

        # Legend
        self.ax.legend(loc='upper right', fontsize=9, framealpha=0.95)

    def _setup_stats_display(self) -> None:
        """Setup statistics display box."""
        self._stats_text = self.ax.text(
            0.02, 0.98,
            "",
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.95, edgecolor='gray', linewidth=1.5),
            family='monospace',
            zorder=10
        )

    def update(self, step_data: Dict[str, Any]) -> None:
        """
        Update visualization with current algorithm step.

        Args:
            step_data: Dictionary containing:
                - type: 'explore' | 'found' | 'complete'
                - current_node: Node being explored
                - visited: Set of visited nodes
                - open_set_nodes: List of frontier nodes
                - path_so_far: Current path to node
                - target: Target node
        """
        if not self._initialized:
            raise RuntimeError("Renderer not initialized. Call initialize() first.")

        step_type = step_data['type']
        current_node = step_data['current_node']
        visited = step_data['visited']
        frontier = step_data['open_set_nodes']
        path = step_data['path_so_far']

        # Clear previous dynamic elements
        self._clear_dynamic_artists()

        # Draw visited nodes (gray cloud)
        if len(visited) > 1:  # Don't draw just the source
            self._draw_visited_nodes(visited)

        # Draw frontier nodes (yellow border)
        if frontier:
            self._draw_frontier_nodes(frontier)

        # Draw current path (blue line)
        if len(path) > 1:
            self._draw_current_path(path)

        # Draw current node (red highlight)
        if current_node is not None:
            self._draw_current_node(current_node)

        # Draw final path if found
        if step_type in ['found', 'complete'] and len(path) > 1:
            self._draw_final_path(path)

        # Update stats display
        self._update_stats(step_data)

        # Refresh display
        plt.pause(0.001)  # Small pause to update display

    def _clear_dynamic_artists(self) -> None:
        """Remove previous dynamic visual elements."""
        if self._visited_artist:
            self._visited_artist.remove()
            self._visited_artist = None

        if self._frontier_artist:
            self._frontier_artist.remove()
            self._frontier_artist = None

        if self._current_artist:
            self._current_artist.remove()
            self._current_artist = None

        if self._path_artist:
            self._path_artist.remove()
            self._path_artist = None

        if self._final_path_artist:
            self._final_path_artist.remove()
            self._final_path_artist = None

    def _draw_visited_nodes(self, visited: Set[int]) -> None:
        """Draw explored/visited nodes."""
        coords = [self.node_positions[node] for node in visited if node in self.node_positions]
        if not coords:
            return

        x_coords, y_coords = zip(*coords)
        self._visited_artist = self.ax.scatter(
            x_coords, y_coords,
            c=self.VISITED_COLOR,
            s=self.VISITED_SIZE,
            alpha=self.VISITED_ALPHA,
            zorder=2
        )

    def _draw_frontier_nodes(self, frontier: List[int]) -> None:
        """Draw frontier (open set) nodes."""
        coords = [self.node_positions[node] for node in frontier if node in self.node_positions]
        if not coords:
            return

        x_coords, y_coords = zip(*coords)
        self._frontier_artist = self.ax.scatter(
            x_coords, y_coords,
            c=self.FRONTIER_COLOR,
            s=self.FRONTIER_SIZE,
            alpha=self.FRONTIER_ALPHA,
            edgecolors='orange',
            linewidths=1,
            zorder=3
        )

    def _draw_current_node(self, node: int) -> None:
        """Draw the currently explored node."""
        if node not in self.node_positions:
            return

        pos = self.node_positions[node]
        self._current_artist = self.ax.scatter(
            pos[0], pos[1],
            c=self.CURRENT_COLOR,
            s=self.CURRENT_SIZE,
            marker='o',
            edgecolors=self.CURRENT_EDGE_COLOR,
            linewidths=self.CURRENT_EDGE_WIDTH,
            zorder=5
        )

    def _draw_current_path(self, path: List[int]) -> None:
        """Draw the current path to the node being explored."""
        if len(path) < 2:
            return

        coords = [self.node_positions[node] for node in path if node in self.node_positions]
        if len(coords) < 2:
            return

        x_coords, y_coords = zip(*coords)
        self._path_artist, = self.ax.plot(
            x_coords, y_coords,
            color=self.PATH_COLOR,
            linewidth=self.PATH_WIDTH,
            alpha=self.PATH_ALPHA,
            zorder=4,
            linestyle='--'
        )

    def _draw_final_path(self, path: List[int]) -> None:
        """Draw the final discovered path (when target is reached)."""
        if len(path) < 2:
            return

        coords = [self.node_positions[node] for node in path if node in self.node_positions]
        if len(coords) < 2:
            return

        x_coords, y_coords = zip(*coords)
        self._final_path_artist, = self.ax.plot(
            x_coords, y_coords,
            color=self.FINAL_PATH_COLOR,
            linewidth=self.FINAL_PATH_WIDTH,
            alpha=self.FINAL_PATH_ALPHA,
            zorder=4,
            label="Final Path"
        )

    def _update_stats(self, step_data: Dict[str, Any]) -> None:
        """Update the statistics display."""
        step_type = step_data['type']
        visited_count = len(step_data['visited'])
        frontier_count = len(step_data['open_set_nodes'])
        path_length = len(step_data['path_so_far'])

        status_icon = {
            'explore': '🔍 EXPLORING',
            'found': '✅ TARGET FOUND',
            'complete': '🏁 COMPLETE'
        }.get(step_type, 'RUNNING')

        text = (
            f"{status_icon}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Explored: {visited_count} nodes\n"
            f"Frontier: {frontier_count} nodes\n"
            f"Path Length: {path_length} nodes\n"
            f"Current Node: {step_data['current_node']}"
        )

        self._stats_text.set_text(text)

    def show_final_summary(self, final_result: tuple, algorithm_name: str) -> None:
        """
        Show final summary overlay.

        Args:
            final_result: Tuple of (path, distance, visited_count, time_ms)
            algorithm_name: Name of algorithm
        """
        path, distance, visited_count, time_ms = final_result

        summary = (
            f"🏁 ALGORITHM COMPLETE!\n\n"
            f"Algorithm: {algorithm_name}\n"
            f"Path Length: {len(path)} nodes\n"
            f"Total Distance: {distance:.0f}m\n"
            f"Nodes Explored: {visited_count}\n"
            f"Computation Time: {time_ms:.2f}ms\n\n"
            f"Press any key to exit..."
        )

        self.ax.text(
            0.5, 0.5,
            summary,
            transform=self.ax.transAxes,
            fontsize=13,
            verticalalignment='center',
            horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.95, edgecolor='darkgreen', linewidth=2),
            family='monospace',
            zorder=11
        )

        plt.draw()

    def show(self) -> None:
        """Display the visualization (blocking)."""
        plt.show()

    def close(self) -> None:
        """Close the visualization."""
        if self.fig is not None:
            plt.close(self.fig)
