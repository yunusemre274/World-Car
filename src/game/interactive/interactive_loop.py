"""
Interactive game loop for user-driven pathfinding simulation.

Manages the complete interactive flow:
1. User clicks to select start node
2. User clicks to select target node
3. User presses ENTER to compute path
4. Algorithm runs and visualizes exploration
5. Car animates along path
6. Summary displayed with restart option
"""

from typing import Optional
import time
import networkx as nx
from matplotlib.backend_bases import MouseEvent, KeyEvent

from .interactive_state import InteractiveGameState, StateTransition
from .node_selector import NodeSelector
from .event_handler import EventHandler, KeyboardShortcuts
from src.visualization.interactive_renderer import InteractiveRenderer
from src.game.car import Car


class InteractiveGameLoop:
    """
    Main interactive game loop.

    State Machine:
    WAITING_START → WAITING_TARGET → READY → RUNNING → FINISHED
                                       ↑____________↓
                                       (R pressed - restart)

    Event Flow:
    1. Mouse click in WAITING_START → select start node → transition to WAITING_TARGET
    2. Mouse click in WAITING_TARGET → select target node → transition to READY
    3. ENTER key in READY → compute path → transition to RUNNING
    4. Car moves → reaches destination → transition to FINISHED
    5. R key → reset to WAITING_START
    6. ESC key → exit
    """

    def __init__(self,
                 graph: nx.MultiDiGraph,
                 algorithm,
                 algorithm_name: str = "Unknown",
                 snap_distance: float = 100.0,
                 car_speed: int = 10):
        """
        Initialize the interactive game loop.

        Args:
            graph: Road network graph
            algorithm: Pathfinding algorithm instance (must have .run() method)
            algorithm_name: Display name for the algorithm
            snap_distance: Max distance (meters) for click-to-node snapping
            car_speed: Ticks between car movements
        """
        self.graph = graph
        self.algorithm = algorithm
        self.algorithm_name = algorithm_name
        self.car_speed = car_speed

        # Game state
        self.state = InteractiveGameState.WAITING_START

        # Selected nodes
        self.start_node: Optional[int] = None
        self.target_node: Optional[int] = None

        # Computed path and metrics
        self.path: Optional[list] = None
        self.path_distance: float = 0.0
        self.nodes_visited: int = 0
        self.computation_time: float = 0.0

        # Game components
        self.node_selector = NodeSelector(graph, max_distance=snap_distance)
        self.renderer = InteractiveRenderer(graph)
        self.event_handler = EventHandler(None)  # Figure set after initialization
        self.car: Optional[Car] = None

        # Game timing
        self._tick_count = 0
        self._running = True

        print("\n" + "="*60)
        print("INTERACTIVE PATHFINDING GAME")
        print("="*60)
        print(f"Algorithm: {algorithm_name}")
        print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        print(f"Snap distance: {snap_distance}m")
        print("="*60)

    def run(self) -> None:
        """
        Start the interactive game loop.

        Blocks until user exits (ESC key).
        """
        try:
            # Initialize
            self._initialize()

            # Main loop
            while self._running:
                self._update()
                self.renderer.update()
                time.sleep(0.033)  # ~30 FPS

        except KeyboardInterrupt:
            print("\nGame interrupted by user")

        finally:
            self._cleanup()

    def _initialize(self) -> None:
        """Initialize game systems."""
        print("\nInitializing game...")

        # Initialize renderer
        self.renderer.initialize()

        # Connect event handler
        self.event_handler.figure = self.renderer.fig
        self.event_handler.on_mouse_click = self._handle_mouse_click
        self.event_handler.on_key_press = self._handle_key_press
        self.event_handler.connect()

        # Show initial instruction
        self.renderer.update_instruction(self.state)

        print("Game ready! Click on the map to select START node.")

    def _update(self) -> None:
        """Update game state (called each frame)."""
        if self.state == InteractiveGameState.RUNNING:
            # Move car
            if self._tick_count % self.car_speed == 0:
                if self.car and not self.car.is_finished:
                    self.car.advance()

                    # Update visualization
                    pos = self.car.get_position()
                    # TODO: Update car marker position

                    # Check if finished
                    if self.car.is_finished:
                        self._transition_to_finished()

            self._tick_count += 1

    def _handle_mouse_click(self, x: float, y: float, event: MouseEvent) -> None:
        """
        Handle mouse click events.

        Args:
            x: Click x coordinate (longitude)
            y: Click y coordinate (latitude)
            event: Matplotlib mouse event
        """
        if not self.state.allows_mouse_input:
            return

        # Select nearest node
        selected_node = self.node_selector.select_node(x, y)

        if selected_node is None:
            print("No node found near click position")
            return

        # Handle based on state
        if self.state == InteractiveGameState.WAITING_START:
            self._select_start_node(selected_node)

        elif self.state == InteractiveGameState.WAITING_TARGET:
            self._select_target_node(selected_node)

    def _handle_key_press(self, key: str, event: KeyEvent) -> None:
        """
        Handle keyboard events.

        Args:
            key: Key pressed (lowercase)
            event: Matplotlib key event
        """
        # ENTER - Start simulation (when READY)
        if KeyboardShortcuts.is_enter(key):
            if self.state == InteractiveGameState.READY:
                self._start_simulation()
            return

        # R - Restart
        if KeyboardShortcuts.is_restart(key):
            self._restart()
            return

        # ESC - Exit
        if KeyboardShortcuts.is_exit(key):
            self._exit()
            return

        # SPACE - Pause/Resume (when RUNNING)
        if KeyboardShortcuts.is_pause(key):
            if self.state == InteractiveGameState.RUNNING:
                self._transition(InteractiveGameState.PAUSED)
            elif self.state == InteractiveGameState.PAUSED:
                self._transition(InteractiveGameState.RUNNING)
            return

    def _select_start_node(self, node: int) -> None:
        """Select the start node."""
        self.start_node = node
        print(f"\nSTART node selected: {node}")

        # Update visualization
        self.renderer.update_node_selection(self.start_node, None)

        # Transition to waiting for target
        self._transition(InteractiveGameState.WAITING_TARGET)

    def _select_target_node(self, node: int) -> None:
        """Select the target node."""
        # Check if same as start
        if node == self.start_node:
            print("Target cannot be the same as start! Click a different node.")
            return

        self.target_node = node
        print(f"TARGET node selected: {node}")

        # Update visualization
        self.renderer.update_node_selection(self.start_node, self.target_node)

        # Transition to ready
        self._transition(InteractiveGameState.READY)

    def _start_simulation(self) -> None:
        """Compute path and start the simulation."""
        print("\n" + "="*60)
        print("COMPUTING PATH...")
        print("="*60)

        # Compute path using algorithm
        start_time = time.perf_counter()
        self.path, self.path_distance, self.nodes_visited, algo_time = \
            self.algorithm.run(self.graph, self.start_node, self.target_node)
        end_time = time.perf_counter()

        self.computation_time = (end_time - start_time) * 1000  # ms

        print(f"Path computed:")
        print(f"  Length: {len(self.path)} nodes")
        print(f"  Distance: {self.path_distance:.0f} meters")
        print(f"  Nodes explored: {self.nodes_visited}")
        print(f"  Time: {self.computation_time:.2f}ms")

        # Draw path
        self.renderer.draw_path(self.path)

        # Create car
        self.car = Car(self.path, self.graph)

        # Transition to running
        self._transition(InteractiveGameState.RUNNING)

        print("\nSimulation started! Watch the car move...")

    def _transition_to_finished(self) -> None:
        """Transition to finished state and show summary."""
        self._transition(InteractiveGameState.FINISHED)

        print("\n" + "="*60)
        print("SIMULATION COMPLETE")
        print("="*60)
        print(f"Algorithm: {self.algorithm_name}")
        print(f"Path Distance: {self.path_distance:.0f}m")
        print(f"Nodes Explored: {self.nodes_visited}")
        print(f"Computation Time: {self.computation_time:.2f}ms")
        print("="*60)
        print("Press R to restart or ESC to exit")

        # Show summary overlay
        self.renderer.show_summary(
            self.path_distance,
            self.nodes_visited,
            self.computation_time,
            self.algorithm_name
        )

    def _restart(self) -> None:
        """Restart the game."""
        print("\n" + "="*60)
        print("RESTARTING...")
        print("="*60)

        # Reset state
        self.start_node = None
        self.target_node = None
        self.path = None
        self.car = None
        self._tick_count = 0

        # Reset visualization
        self.renderer.reset()

        # Transition to initial state
        self._transition(InteractiveGameState.WAITING_START)

        print("Click on the map to select START node.")

    def _exit(self) -> None:
        """Exit the game."""
        print("\nExiting game...")
        self._running = False

    def _transition(self, new_state: InteractiveGameState) -> None:
        """
        Transition to a new state.

        Args:
            new_state: Target state

        Raises:
            ValueError: If transition is invalid
        """
        # Validate transition
        StateTransition.validate(self.state, new_state)

        old_state = self.state
        self.state = new_state

        print(f"State transition: {old_state} → {new_state}")

        # Update instruction overlay
        self.renderer.update_instruction(new_state)

    def _cleanup(self) -> None:
        """Cleanup resources."""
        print("\nCleaning up...")
        self.event_handler.disconnect()
        # Don't close renderer - let user close window manually
