"""
Main game loop for pathfinding simulation.

Implements a fixed-timestep game loop with state machine control.
Manages the flow between initialization, running, paused, and finished states.
"""

from typing import List, Optional
import time
import networkx as nx

from .game_state import GameState
from .car import Car
from .input_handler import InputHandler
from src.visualization.game_renderer import GameRenderer


class GameConfig:
    """
    Configuration parameters for the game loop.

    Attributes:
        tick_rate: Number of updates per second
        move_interval: Number of ticks between car movements
        auto_close: Whether to close automatically when finished
        show_final_screen: Whether to show summary at end
    """
    def __init__(
        self,
        tick_rate: int = 30,
        move_interval: int = 10,
        auto_close: bool = False,
        show_final_screen: bool = True
    ):
        self.tick_rate = tick_rate
        self.move_interval = move_interval
        self.auto_close = auto_close
        self.show_final_screen = show_final_screen

    @property
    def tick_duration(self) -> float:
        """Duration of one tick in seconds."""
        return 1.0 / self.tick_rate


class GameLoop:
    """
    Main game loop for the pathfinding simulation.

    Implements a professional game engine architecture:
    - Fixed timestep updates
    - State machine control
    - Decoupled game logic and rendering
    - Input handling structure

    The loop runs at a fixed tick rate and moves the car at a configurable interval,
    creating a smooth animation of the pathfinding result.

    Example:
        >>> game = GameLoop(graph, path, algorithm_name="A*")
        >>> game.run()
    """

    def __init__(
        self,
        graph: nx.MultiDiGraph,
        path: List[int],
        algorithm_name: str = "Unknown",
        config: Optional[GameConfig] = None
    ):
        """
        Initialize the game loop.

        Args:
            graph: Road network graph
            path: Computed path for the car to follow
            algorithm_name: Name of the algorithm used (for display)
            config: Game configuration parameters

        Raises:
            ValueError: If path is empty or invalid
        """
        if not path or len(path) == 0:
            raise ValueError("Path cannot be empty")

        self.graph = graph
        self.path = path
        self.algorithm_name = algorithm_name
        self.config = config or GameConfig()

        # Initialize game components
        self.state = GameState.INIT
        self.car = Car(path, graph)
        self.renderer = GameRenderer(graph)
        self.input_handler = InputHandler()

        # Game timing
        self._tick_count = 0
        self._start_time = 0.0
        self._elapsed_time = 0.0

        # Control flags
        self._running = True

    def initialize(self) -> None:
        """
        Initialize the game systems.

        Sets up the renderer, prepares the car, and transitions to RUNNING state.
        """
        print(f"Initializing simulation...")
        print(f"  Algorithm: {self.algorithm_name}")
        print(f"  Path length: {len(self.path)} nodes")
        print(f"  Tick rate: {self.config.tick_rate} Hz")
        print(f"  Move interval: {self.config.move_interval} ticks")

        # Initialize renderer
        self.renderer.initialize(self.path)

        # Setup car
        self.car.reset()

        # Transition to RUNNING
        self.state = GameState.RUNNING
        self._start_time = time.time()

        print("Simulation started!")

    def run(self) -> None:
        """
        Main game loop.

        Runs the simulation with fixed timestep until the car reaches
        the destination or the user closes the window.

        State flow:
            INIT -> RUNNING -> FINISHED
        """
        try:
            # Initialize
            self.initialize()

            # Main loop
            while self._running and not self.state.is_terminal:
                frame_start = time.time()

                # Update game state
                self.update()

                # Render
                self.render()

                # Maintain fixed timestep
                frame_time = time.time() - frame_start
                sleep_time = max(0, self.config.tick_duration - frame_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

                self._tick_count += 1

            # Finalize
            self.finalize()

        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
            self.state = GameState.ERROR

        finally:
            self.cleanup()

    def update(self) -> None:
        """
        Update game state (fixed timestep).

        Called once per tick. Handles:
        - Car movement (at configured interval)
        - State transitions
        - Win condition checking
        """
        if self.state != GameState.RUNNING:
            return

        # Move car at specified interval
        if self._tick_count % self.config.move_interval == 0:
            advanced = self.car.advance()

            # Check if car finished
            if self.car.is_finished:
                self.state = GameState.FINISHED
                self._elapsed_time = time.time() - self._start_time

    def render(self) -> None:
        """
        Render the current frame.

        Updates the visual representation of the game state.
        """
        self.renderer.update(self.car, self.state)

    def finalize(self) -> None:
        """
        Finalize the simulation.

        Called when the car reaches the destination.
        Shows summary statistics if configured.
        """
        if self.state == GameState.FINISHED:
            print("\n" + "="*50)
            print("SIMULATION COMPLETE")
            print("="*50)

            stats = self.car.get_stats()
            print(f"Algorithm: {self.algorithm_name}")
            print(f"Total Distance: {stats['distance_traveled']:.0f}m")
            print(f"Nodes Traversed: {stats['nodes_visited']}")
            print(f"Simulation Time: {self._elapsed_time:.2f}s")
            print(f"Total Ticks: {self._tick_count}")
            print("="*50)

            # Show final screen
            if self.config.show_final_screen:
                self.renderer.show_final_screen(
                    self.car,
                    self._elapsed_time,
                    self.algorithm_name
                )

            # Display window
            if not self.config.auto_close:
                self.renderer.show()

    def cleanup(self) -> None:
        """
        Cleanup resources.

        Called when the game loop exits.
        """
        if self.config.auto_close:
            self.renderer.close()

    def pause(self) -> None:
        """Pause the simulation."""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
            print("Simulation paused")

    def resume(self) -> None:
        """Resume the simulation."""
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
            print("Simulation resumed")

    def stop(self) -> None:
        """Stop the simulation."""
        self._running = False
        print("Simulation stopped")
