"""
Game renderer for pathfinding simulation.

Handles all visualization aspects of the game:
- Road network rendering
- Path overlay
- Car position and movement
- UI elements (stats, state indicators)
"""

from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import networkx as nx
import osmnx as ox

from src.game.car import Car
from src.game.game_state import GameState


class GameRenderer:
    """
    Renders the pathfinding game simulation.

    Responsible for all visual aspects of the game including the road network,
    path visualization, car position, and UI overlays.

    The renderer separates visual concerns from game logic, making it easy to
    modify the appearance without touching the game engine.
    """

    # Visual configuration
    NETWORK_COLOR = "#e8e8e8"
    NETWORK_WIDTH = 0.5
    PATH_COLOR = "#4a90e2"
    PATH_WIDTH = 3.0
    PATH_ALPHA = 0.6
    CAR_COLOR = "#ff4444"
    CAR_SIZE = 150
    CAR_EDGE_COLOR = "white"
    CAR_EDGE_WIDTH = 2
    SOURCE_COLOR = "#44ff44"
    SOURCE_SIZE = 120
    TARGET_COLOR = "#ffaa00"
    TARGET_SIZE = 180
    TARGET_MARKER = "*"

    def __init__(self, graph: nx.MultiDiGraph, figsize: Tuple[int, int] = (12, 10)):
        """
        Initialize the game renderer.

        Args:
            graph: Road network to render
            figsize: Figure size as (width, height) in inches
        """
        self.graph = graph
        self.figsize = figsize

        # Create figure and axes
        self.fig: Optional[Figure] = None
        self.ax: Optional[Axes] = None

        # Cached positions for efficient rendering
        self.node_positions = {
            node: (self.graph.nodes[node]["x"], self.graph.nodes[node]["y"])
            for node in self.graph.nodes
        }

        # Render state
        self._car_artist = None
        self._stats_text = None
        self._initialized = False

    def initialize(self, path: List[int]) -> None:
        """
        Initialize the renderer with a path.

        Sets up the figure, draws the base map, and prepares for animation.

        Args:
            path: The computed path to visualize
        """
        if self._initialized:
            return

        # Create figure
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.fig.canvas.manager.set_window_title("WorldCar - Pathfinding Simulation")

        # Draw base road network
        self._draw_network()

        # Draw path
        self._draw_path(path)

        # Draw source and target
        source = path[0]
        target = path[-1]
        self._draw_endpoints(source, target)

        # Setup stats display
        self._setup_stats_display()

        # Configure axes
        self.ax.set_xlabel("Longitude", fontsize=10)
        self.ax.set_ylabel("Latitude", fontsize=10)
        self.ax.set_title("Real-World Pathfinding Simulation", fontsize=14, fontweight="bold", pad=15)

        self._initialized = True

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

    def _draw_path(self, path: List[int]) -> None:
        """
        Draw the computed path on the map.

        Args:
            path: List of node IDs representing the path
        """
        if len(path) < 2:
            return

        path_coords = [self.node_positions[node] for node in path]
        path_x, path_y = zip(*path_coords)

        self.ax.plot(
            path_x, path_y,
            color=self.PATH_COLOR,
            linewidth=self.PATH_WIDTH,
            alpha=self.PATH_ALPHA,
            zorder=2,
            label="Computed Path"
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

        # Draw source
        self.ax.scatter(
            source_pos[0], source_pos[1],
            c=self.SOURCE_COLOR,
            s=self.SOURCE_SIZE,
            marker='o',
            edgecolors='white',
            linewidths=2,
            zorder=4,
            label="Start"
        )

        # Draw target
        self.ax.scatter(
            target_pos[0], target_pos[1],
            c=self.TARGET_COLOR,
            s=self.TARGET_SIZE,
            marker=self.TARGET_MARKER,
            edgecolors='white',
            linewidths=2,
            zorder=4,
            label="Destination"
        )

        # Legend
        self.ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    def _setup_stats_display(self) -> None:
        """Setup the statistics display box."""
        # Create text box for stats in top-left
        self._stats_text = self.ax.text(
            0.02, 0.98,
            "",
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'),
            family='monospace',
            zorder=10
        )

    def update(self, car: Car, state: GameState) -> None:
        """
        Update the visualization with current game state.

        Args:
            car: The car entity to render
            state: Current game state
        """
        if not self._initialized:
            raise RuntimeError("Renderer not initialized. Call initialize() first.")

        # Update car position
        self._update_car_position(car)

        # Update stats display
        self._update_stats_display(car, state)

        # Refresh display
        plt.pause(0.001)

    def _update_car_position(self, car: Car) -> None:
        """
        Update the car's position on the map.

        Args:
            car: The car entity
        """
        # Remove old car marker
        if self._car_artist is not None:
            self._car_artist.remove()

        # Get current position
        pos = car.get_position()

        # Draw new car marker
        self._car_artist = self.ax.scatter(
            pos[0], pos[1],
            c=self.CAR_COLOR,
            s=self.CAR_SIZE,
            marker='o',
            edgecolors=self.CAR_EDGE_COLOR,
            linewidths=self.CAR_EDGE_WIDTH,
            zorder=5
        )

    def _update_stats_display(self, car: Car, state: GameState) -> None:
        """
        Update the statistics display.

        Args:
            car: The car entity
            state: Current game state
        """
        stats = car.get_stats()

        text = (
            f"STATE: {state.name}\n"
            f"Node: {stats['current_node']}\n"
            f"Progress: {stats['progress_pct']:.1f}%\n"
            f"Distance: {stats['distance_traveled']:.0f}m\n"
            f"Visited: {stats['nodes_visited']}/{stats['nodes_visited'] + stats['nodes_remaining']}\n"
            f"Remaining: {stats['nodes_remaining']} nodes"
        )

        self._stats_text.set_text(text)

    def show_final_screen(self, car: Car, total_time: float, algorithm_name: str) -> None:
        """
        Show the final summary screen.

        Args:
            car: The car entity (finished)
            total_time: Total simulation time in seconds
            algorithm_name: Name of the algorithm used
        """
        stats = car.get_stats()

        # Create summary text
        summary = (
            f"SIMULATION COMPLETE!\n\n"
            f"Algorithm: {algorithm_name}\n"
            f"Total Distance: {stats['distance_traveled']:.0f}m\n"
            f"Nodes Traversed: {stats['nodes_visited']}\n"
            f"Simulation Time: {total_time:.2f}s\n\n"
            f"Press any key to exit..."
        )

        # Display centered text
        self.ax.text(
            0.5, 0.5,
            summary,
            transform=self.ax.transAxes,
            fontsize=14,
            verticalalignment='center',
            horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.95, edgecolor='black', linewidth=2),
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
