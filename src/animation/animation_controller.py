"""
Animation controller - main orchestrator for car animation.

Ties together path interpolation, car animation, and camera control
to create smooth, game-like visualization of pathfinding results.
"""

from typing import Optional, Callable
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
import networkx as nx

from .path_interpolator import PathInterpolator, InterpolationMethod
from .car_animator import CarAnimator
from .camera_controller import CameraController, CameraMode


class AnimationController:
    """
    Main controller for car path animation.

    Orchestrates all components to create smooth, cinematic visualization
    of a car moving along a computed path.

    Example:
        >>> controller = AnimationController(ax, graph, path)
        >>> anim = controller.animate(interval=50)
        >>> plt.show()

    Example with camera follow:
        >>> controller = AnimationController(
        >>>     ax, graph, path,
        >>>     camera_mode='follow_smooth',
        >>>     show_trail=True
        >>> )
        >>> anim = controller.animate()
        >>> plt.show()
    """

    def __init__(self,
                 ax: Axes,
                 graph: nx.MultiDiGraph,
                 path: list,
                 steps_per_edge: int = 30,
                 interpolation_method: InterpolationMethod = InterpolationMethod.LINEAR,
                 car_color: str = '#ff4444',
                 car_size: int = 150,
                 show_trail: bool = False,
                 trail_length: int = 30,
                 camera_mode: str = CameraMode.STATIC,
                 camera_smoothing: float = 0.15):
        """
        Initialize the animation controller.

        Args:
            ax: Matplotlib axes to animate on
            graph: Road network graph
            path: Computed path (list of node IDs)
            steps_per_edge: Number of interpolation points per edge
            interpolation_method: Method for path smoothing
            car_color: Color of car marker
            car_size: Size of car marker
            show_trail: Whether to show trail behind car
            trail_length: Number of trail points
            camera_mode: Camera behavior mode
            camera_smoothing: Smoothing factor for camera follow

        Raises:
            ValueError: If path is invalid
        """
        self.ax = ax
        self.graph = graph
        self.path = path

        # Create path interpolator
        self.interpolator = PathInterpolator(graph, path)
        self.interpolated_coords = self.interpolator.interpolate(
            steps_per_edge=steps_per_edge,
            method=interpolation_method
        )

        # Create car animator
        self.car = CarAnimator(
            ax=ax,
            color=car_color,
            size=car_size,
            trail=show_trail,
            trail_length=trail_length
        )

        # Create camera controller
        self.camera = CameraController(
            ax=ax,
            mode=camera_mode,
            smoothing=camera_smoothing
        )

        # Animation state
        self.current_frame = 0
        self.total_frames = len(self.interpolated_coords)
        self.is_initialized = False

        # Callbacks
        self.on_frame_callback: Optional[Callable[[int, float, float], None]] = None
        self.on_complete_callback: Optional[Callable[[], None]] = None

        print(f"Animation Controller initialized:")
        print(f"  Path nodes: {len(path)}")
        print(f"  Interpolated points: {self.total_frames}")
        print(f"  Total distance: {self.interpolator.total_distance:.0f}m")

    def _init_animation(self):
        """
        Initialize animation (called by FuncAnimation).

        Returns:
            List of artists to animate
        """
        if not self.is_initialized:
            # Initialize car at start position
            start_x, start_y = self.interpolated_coords[0]
            self.car.initialize(start_x, start_y)

            # Initialize camera
            self.camera.initialize(start_x, start_y)

            self.is_initialized = True

        return [self.car._car_marker]

    def _update_frame(self, frame: int):
        """
        Update animation frame (called by FuncAnimation).

        Args:
            frame: Current frame number

        Returns:
            List of artists that were modified
        """
        if frame >= self.total_frames:
            # Animation complete
            if self.on_complete_callback is not None:
                self.on_complete_callback()
            return [self.car._car_marker]

        # Get current position
        x, y = self.interpolated_coords[frame]

        # Update car position
        self.car.update_position(x, y)

        # Update camera
        self.camera.update(x, y)

        # Call frame callback if set
        if self.on_frame_callback is not None:
            self.on_frame_callback(frame, x, y)

        self.current_frame = frame

        # Return modified artists
        artists = [self.car._car_marker]
        if self.car._trail_line is not None:
            artists.append(self.car._trail_line)

        return artists

    def animate(self,
               interval: int = 50,
               repeat: bool = False,
               save_path: Optional[str] = None) -> FuncAnimation:
        """
        Start the animation using matplotlib's FuncAnimation.

        Args:
            interval: Milliseconds between frames (lower = faster)
            repeat: Whether to loop the animation
            save_path: If provided, save animation to file (e.g., 'anim.mp4')

        Returns:
            FuncAnimation object (keep reference to prevent garbage collection)

        Example:
            >>> anim = controller.animate(interval=30)
            >>> plt.show()

        Example (save to file):
            >>> anim = controller.animate(save_path='path_animation.mp4')
            >>> # Animation will be saved automatically
        """
        print(f"\nStarting animation:")
        print(f"  Frames: {self.total_frames}")
        print(f"  Interval: {interval}ms")
        print(f"  Duration: {(self.total_frames * interval) / 1000:.1f}s")

        # Create animation
        anim = FuncAnimation(
            self.ax.figure,
            self._update_frame,
            init_func=self._init_animation,
            frames=self.total_frames,
            interval=interval,
            repeat=repeat,
            blit=True  # Faster rendering
        )

        # Save if requested
        if save_path is not None:
            print(f"Saving animation to: {save_path}")
            anim.save(save_path, writer='pillow', fps=1000//interval)
            print("Animation saved!")

        return anim

    def animate_with_progress(self,
                             interval: int = 50,
                             repeat: bool = False) -> FuncAnimation:
        """
        Animate with progress bar in console.

        Args:
            interval: Milliseconds between frames
            repeat: Whether to loop

        Returns:
            FuncAnimation object
        """
        def progress_callback(frame: int, x: float, y: float):
            """Print progress every 10%."""
            if frame % (self.total_frames // 10) == 0:
                progress = (frame / self.total_frames) * 100
                print(f"Progress: {progress:.0f}% (frame {frame}/{self.total_frames})")

        self.on_frame_callback = progress_callback
        return self.animate(interval=interval, repeat=repeat)

    def set_speed(self, speed_multiplier: float) -> None:
        """
        Adjust animation speed by changing interpolation.

        Args:
            speed_multiplier: Speed multiplier (2.0 = 2x faster, 0.5 = 2x slower)

        Note:
            This requires regenerating interpolated coordinates.
        """
        new_steps = max(1, int(30 / speed_multiplier))
        self.interpolated_coords = self.interpolator.interpolate(
            steps_per_edge=new_steps
        )
        self.total_frames = len(self.interpolated_coords)
        self.current_frame = 0

    def get_stats(self) -> dict:
        """
        Get animation statistics.

        Returns:
            Dictionary with comprehensive stats
        """
        return {
            'path_stats': self.interpolator.get_stats(),
            'car_stats': self.car.get_stats(),
            'camera_stats': self.camera.get_stats(),
            'animation': {
                'current_frame': self.current_frame,
                'total_frames': self.total_frames,
                'progress_pct': (self.current_frame / self.total_frames) * 100
            }
        }


class InteractiveAnimationController(AnimationController):
    """
    Animation controller with interactive controls.

    Adds keyboard controls for pause, speed up, slow down, etc.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with interactive features."""
        super().__init__(*args, **kwargs)

        self.paused = False
        self.speed = 1.0

        # Connect keyboard events
        self.ax.figure.canvas.mpl_connect('key_press_event', self._on_key_press)

    def _on_key_press(self, event):
        """
        Handle keyboard events.

        Controls:
        - SPACE: Pause/Resume
        - +: Speed up
        - -: Slow down
        - R: Reset
        """
        if event.key == ' ':
            # Toggle pause
            self.paused = not self.paused
            print(f"Animation {'paused' if self.paused else 'resumed'}")

        elif event.key == '+' or event.key == '=':
            # Speed up
            self.speed *= 1.5
            print(f"Speed: {self.speed:.1f}x")

        elif event.key == '-' or event.key == '_':
            # Slow down
            self.speed /= 1.5
            print(f"Speed: {self.speed:.1f}x")

        elif event.key == 'r':
            # Reset
            self.current_frame = 0
            print("Animation reset")

    def _update_frame(self, frame: int):
        """Update frame with pause support."""
        if self.paused:
            return [self.car._car_marker]

        # Adjust frame based on speed
        adjusted_frame = int(frame * self.speed)
        adjusted_frame = min(adjusted_frame, self.total_frames - 1)

        return super()._update_frame(adjusted_frame)
