"""
Interactive renderer with UI overlays and selection markers.

Extends the base game renderer with:
- Start/target node selection markers
- Instruction overlays
- Step-by-step algorithm visualization
- Final summary screen with statistics
"""

from typing import Optional, Tuple, List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import networkx as nx
import osmnx as ox

from src.game.interactive.interactive_state import InteractiveGameState


class InteractiveRenderer:
    """
    Renders the interactive pathfinding game with UI overlays.

    Responsibilities:
    - Show node selection markers
    - Display state-specific instructions
    - Visualize algorithm exploration (optional step-by-step)
    - Show final summary overlay
    """

    # Visual configuration
    NETWORK_COLOR = "#e8e8e8"
    PATH_COLOR = "#4a90e2"
    START_COLOR = "#00ff00"
    START_SIZE = 300
    TARGET_COLOR = "#ff9500"
    TARGET_SIZE = 400
    TARGET_MARKER = "*"
    SELECTION_EDGE = "white"
    SELECTION_EDGE_WIDTH = 3

    # UI colors
    INSTRUCTION_BG = "lightyellow"
    INSTRUCTION_EDGE = "orange"
    SUMMARY_BG = "lightgreen"
    SUMMARY_EDGE = "darkgreen"

    def __init__(self, graph: nx.MultiDiGraph, figsize: Tuple[int, int] = (14, 10)):
        """
        Initialize the interactive renderer.

        Args:
            graph: Road network to render
            figsize: Figure size as (width, height)
        """
        self.graph = graph
        self.figsize = figsize

        # Create figure and axes
        self.fig: Optional[Figure] = None
        self.ax: Optional[Axes] = None

        # Node positions cache
        self.node_positions = {
            node: (self.graph.nodes[node]["x"], self.graph.nodes[node]["y"])
            for node in self.graph.nodes
        }

        # UI elements (artists)
        self._start_marker = None
        self._target_marker = None
        self._instruction_text = None
        self._summary_text = None
        self._path_line = None
        self._explored_nodes = []

        self._initialized = False

    def initialize(self) -> None:
        """
        Initialize the renderer.

        Sets up the figure and draws the base map.
        """
        if self._initialized:
            return

        # Create figure
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.fig.canvas.manager.set_window_title("WorldCar - Interactive Pathfinding")

        # Draw base network
        self._draw_network()

        # Setup UI
        self.ax.set_xlabel("Longitude", fontsize=10)
        self.ax.set_ylabel("Latitude", fontsize=10)
        self.ax.set_title("Interactive Pathfinding - Click to Select Nodes",
                         fontsize=14, fontweight="bold", pad=15)

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
            edge_linewidth=0.5
        )

    def update_node_selection(self, start_node: Optional[int],
                             target_node: Optional[int]) -> None:
        """
        Update the visual markers for selected nodes.

        Args:
            start_node: Start node ID (None if not selected)
            target_node: Target node ID (None if not selected)
        """
        # Remove old markers
        if self._start_marker is not None:
            self._start_marker.remove()
            self._start_marker = None

        if self._target_marker is not None:
            self._target_marker.remove()
            self._target_marker = None

        # Draw start marker
        if start_node is not None:
            pos = self.node_positions[start_node]
            self._start_marker = self.ax.scatter(
                pos[0], pos[1],
                c=self.START_COLOR,
                s=self.START_SIZE,
                marker='o',
                edgecolors=self.SELECTION_EDGE,
                linewidths=self.SELECTION_EDGE_WIDTH,
                zorder=5,
                label="START"
            )

        # Draw target marker
        if target_node is not None:
            pos = self.node_positions[target_node]
            self._target_marker = self.ax.scatter(
                pos[0], pos[1],
                c=self.TARGET_COLOR,
                s=self.TARGET_SIZE,
                marker=self.TARGET_MARKER,
                edgecolors=self.SELECTION_EDGE,
                linewidths=self.SELECTION_EDGE_WIDTH,
                zorder=5,
                label="TARGET"
            )

        # Update legend
        if start_node or target_node:
            self.ax.legend(loc='upper right', fontsize=10, framealpha=0.9)

        plt.draw()

    def update_instruction(self, state: InteractiveGameState) -> None:
        """
        Update the instruction overlay based on current state.

        Args:
            state: Current game state
        """
        # Remove old instruction
        if self._instruction_text is not None:
            self._instruction_text.remove()
            self._instruction_text = None

        # Get instruction text
        instruction = state.get_instruction_text()
        if not instruction:
            return

        # Determine color based on state
        if state == InteractiveGameState.READY:
            bg_color = "lightgreen"
            edge_color = "darkgreen"
        elif state.is_finished:
            return  # Don't show instruction when finished (use summary instead)
        else:
            bg_color = self.INSTRUCTION_BG
            edge_color = self.INSTRUCTION_EDGE

        # Draw instruction box (centered, top)
        self._instruction_text = self.ax.text(
            0.5, 0.97,
            instruction,
            transform=self.ax.transAxes,
            fontsize=12,
            fontweight='bold',
            verticalalignment='top',
            horizontalalignment='center',
            bbox=dict(
                boxstyle='round,pad=0.8',
                facecolor=bg_color,
                alpha=0.95,
                edgecolor=edge_color,
                linewidth=2
            ),
            zorder=10
        )

        plt.draw()

    def draw_path(self, path: List[int]) -> None:
        """
        Draw the computed path on the map.

        Args:
            path: List of node IDs representing the path
        """
        if self._path_line is not None:
            self._path_line[0].remove()
            self._path_line = None

        if len(path) < 2:
            return

        path_coords = [self.node_positions[node] for node in path]
        path_x, path_y = zip(*path_coords)

        self._path_line = self.ax.plot(
            path_x, path_y,
            color=self.PATH_COLOR,
            linewidth=3.0,
            alpha=0.7,
            zorder=3,
            label="Computed Path"
        )

        self.ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        plt.draw()

    def show_summary(self, path_length: float, nodes_visited: int,
                    execution_time: float, algorithm_name: str) -> None:
        """
        Show the final summary overlay.

        Args:
            path_length: Total path distance in meters
            nodes_visited: Number of nodes explored by algorithm
            execution_time: Algorithm execution time in milliseconds
            algorithm_name: Name of the algorithm used
        """
        # Remove instruction
        if self._instruction_text is not None:
            self._instruction_text.remove()
            self._instruction_text = None

        summary = (
            "SIMULATION COMPLETE!\n\n"
            f"Algorithm: {algorithm_name}\n"
            f"Path Distance: {path_length:.0f} meters\n"
            f"Nodes Explored: {nodes_visited}\n"
            f"Computation Time: {execution_time:.2f} ms\n\n"
            "Press R to restart  |  ESC to exit"
        )

        self._summary_text = self.ax.text(
            0.5, 0.5,
            summary,
            transform=self.ax.transAxes,
            fontsize=13,
            fontweight='bold',
            verticalalignment='center',
            horizontalalignment='center',
            bbox=dict(
                boxstyle='round,pad=1.2',
                facecolor=self.SUMMARY_BG,
                alpha=0.95,
                edgecolor=self.SUMMARY_EDGE,
                linewidth=3
            ),
            family='monospace',
            zorder=11
        )

        plt.draw()

    def clear_summary(self) -> None:
        """Clear the summary overlay."""
        if self._summary_text is not None:
            self._summary_text.remove()
            self._summary_text = None
            plt.draw()

    def clear_path(self) -> None:
        """Clear the drawn path."""
        if self._path_line is not None:
            self._path_line[0].remove()
            self._path_line = None
            plt.draw()

    def reset(self) -> None:
        """Reset the renderer to initial state."""
        self.clear_summary()
        self.clear_path()
        self.update_node_selection(None, None)

        if self._instruction_text is not None:
            self._instruction_text.remove()
            self._instruction_text = None

        plt.draw()

    def update(self) -> None:
        """Force a canvas update."""
        if self.fig is not None:
            plt.pause(0.001)

    def show(self) -> None:
        """Display the figure (blocking)."""
        plt.show()

    def close(self) -> None:
        """Close the figure."""
        if self.fig is not None:
            plt.close(self.fig)
