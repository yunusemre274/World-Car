"""
Algorithm Visualization Game Loop

Runs pathfinding algorithms step-by-step with visual feedback.
Each algorithm iteration is rendered before proceeding to the next.
"""

from typing import Optional
import time
import networkx as nx

from src.visualization.algorithm_renderer import AlgorithmRenderer


class AlgorithmVisualizationConfig:
    """
    Configuration for algorithm visualization.

    Attributes:
        step_delay: Delay between algorithm steps in seconds
        show_final_screen: Whether to show summary at end
        auto_close: Whether to close window automatically
    """
    def __init__(
        self,
        step_delay: float = 0.05,  # 50ms per step - ADJUST THIS FOR SPEED
        show_final_screen: bool = True,
        auto_close: bool = False
    ):
        self.step_delay = step_delay
        self.show_final_screen = show_final_screen
        self.auto_close = auto_close


class AlgorithmGameLoop:
    """
    Game loop for visualizing pathfinding algorithm execution.

    This loop drives the algorithm step-by-step, rendering each
    iteration to show how the algorithm explores the graph.

    The key difference from the regular game loop:
    - Regular loop: Algorithm runs instantly, then car animates along path
    - THIS loop: Algorithm runs step-by-step with visualization

    Example:
        >>> algo = AStarAlgorithm(heuristic_weight=1.5)
        >>> loop = AlgorithmGameLoop(graph, algo, source, target)
        >>> loop.run()
    """

    def __init__(
        self,
        graph: nx.MultiDiGraph,
        algorithm,  # Should have run_animated() method
        source: int,
        target: int,
        algorithm_name: str = "A*",
        config: Optional[AlgorithmVisualizationConfig] = None
    ):
        """
        Initialize the algorithm visualization loop.

        Args:
            graph: Road network graph
            algorithm: Algorithm instance with run_animated() method
            source: Source node ID
            target: Target node ID
            algorithm_name: Display name for algorithm
            config: Visualization configuration

        Raises:
            ValueError: If algorithm doesn't have run_animated() method
        """
        if not hasattr(algorithm, 'run_animated'):
            raise ValueError(
                f"Algorithm {type(algorithm).__name__} must have run_animated() method for visualization"
            )

        self.graph = graph
        self.algorithm = algorithm
        self.source = source
        self.target = target
        self.algorithm_name = algorithm_name
        self.config = config or AlgorithmVisualizationConfig()

        # Renderer
        self.renderer = AlgorithmRenderer(graph)

        # State
        self._step_count = 0
        self._running = True

    def run(self) -> tuple:
        """
        Run the algorithm visualization.

        Executes the algorithm step-by-step, rendering each iteration.

        Returns:
            Final result tuple: (path, distance, visited_count, time_ms)
        """
        try:
            print("="*60)
            print(f"ALGORITHM VISUALIZATION: {self.algorithm_name}")
            print("="*60)
            print(f"Source: {self.source}")
            print(f"Target: {self.target}")
            print(f"Step delay: {self.config.step_delay*1000:.1f}ms")
            print("="*60)
            print()

            # Initialize renderer
            self.renderer.initialize(self.source, self.target, self.algorithm_name)

            # Create algorithm generator
            print("▶ Starting step-by-step execution...")
            print()
            algo_generator = self.algorithm.run_animated(self.graph, self.source, self.target)

            # ⭐ MAIN VISUALIZATION LOOP ⭐
            # This is where the magic happens:
            # 1. Get next algorithm step
            # 2. Render it
            # 3. Delay for animation
            # 4. Repeat until complete

            final_result = None

            # We need to manually iterate to catch StopIteration and get return value
            while True:
                try:
                    step_data = next(algo_generator)

                    # Update visualization with current step
                    self.renderer.update(step_data)

                    # Print progress
                    step_type = step_data['type']
                    if step_type == 'explore':
                        self._step_count += 1
                        if self._step_count % 10 == 0:  # Print every 10 steps
                            print(f"  Step {self._step_count}: Explored {len(step_data['visited'])} nodes, "
                                  f"Frontier: {len(step_data['open_set_nodes'])} nodes")

                    elif step_type == 'found':
                        print(f"\n✅ Target found after {self._step_count} steps!")

                    elif step_type == 'complete':
                        print(f"\n🏁 Algorithm complete!")

                    # ⏱️ TIMING CONTROL - ADJUST config.step_delay TO CHANGE SPEED
                    time.sleep(self.config.step_delay)

                except StopIteration as e:
                    # Generator finished - extract return value
                    final_result = e.value
                    break

            if final_result is None:
                raise RuntimeError("Algorithm generator did not return a result")

            path, distance, visited_count, time_ms = final_result

            print()
            print("="*60)
            print("ALGORITHM STATISTICS")
            print("="*60)
            print(f"Algorithm: {self.algorithm_name}")
            print(f"Path Length: {len(path)} nodes")
            print(f"Total Distance: {distance:.0f} meters")
            print(f"Nodes Explored: {visited_count}")
            print(f"Computation Time: {time_ms:.2f}ms")
            print(f"Visualization Steps: {self._step_count}")
            print("="*60)

            # Show final summary overlay
            if self.config.show_final_screen:
                self.renderer.show_final_summary(final_result, self.algorithm_name)

            # Display window
            if not self.config.auto_close:
                print("\n👀 Close the window to exit...")
                self.renderer.show()

            return final_result

        except KeyboardInterrupt:
            print("\n\n⚠ Visualization interrupted by user")
            return None

        finally:
            if self.config.auto_close:
                self.renderer.close()


# ============================================================================
# SPEED PRESETS
# ============================================================================

def create_slow_config() -> AlgorithmVisualizationConfig:
    """Slow visualization - good for presentations and debugging."""
    return AlgorithmVisualizationConfig(step_delay=0.1)  # 100ms per step


def create_normal_config() -> AlgorithmVisualizationConfig:
    """Normal speed - balanced visualization."""
    return AlgorithmVisualizationConfig(step_delay=0.05)  # 50ms per step


def create_fast_config() -> AlgorithmVisualizationConfig:
    """Fast visualization - quick overview."""
    return AlgorithmVisualizationConfig(step_delay=0.01)  # 10ms per step


def create_turbo_config() -> AlgorithmVisualizationConfig:
    """Turbo speed - as fast as possible."""
    return AlgorithmVisualizationConfig(step_delay=0.001)  # 1ms per step
