"""
Car animator for visual marker movement.

Handles the animated car marker on the matplotlib plot, including
visual customization and smooth position updates.
"""

from typing import Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Circle
import numpy as np


class CarAnimator:
    """
    Animated car marker for path visualization.

    Manages the visual representation of the car moving along the path.
    Supports customizable appearance and optional trail effect.

    Example:
        >>> car = CarAnimator(ax, color='red', size=100)
        >>> car.update_position(x, y)  # Move to new position
        >>> car.show_trail(True)       # Enable trail
    """

    def __init__(self,
                 ax: Axes,
                 color: str = '#ff4444',
                 size: int = 150,
                 marker: str = 'o',
                 edge_color: str = 'white',
                 edge_width: int = 2,
                 trail: bool = False,
                 trail_length: int = 20,
                 trail_alpha: float = 0.3):
        """
        Initialize the car animator.

        Args:
            ax: Matplotlib axes to draw on
            color: Car marker color
            size: Car marker size (scatter point size)
            marker: Marker shape ('o', 's', '^', etc.)
            edge_color: Edge color for car marker
            edge_width: Edge width in pixels
            trail: Whether to show trail behind car
            trail_length: Number of trail points to keep
            trail_alpha: Trail transparency (0=invisible, 1=opaque)
        """
        self.ax = ax
        self.color = color
        self.size = size
        self.marker = marker
        self.edge_color = edge_color
        self.edge_width = edge_width

        # Trail settings
        self.trail_enabled = trail
        self.trail_length = trail_length
        self.trail_alpha = trail_alpha
        self.trail_positions = []

        # Current position
        self.x: Optional[float] = None
        self.y: Optional[float] = None

        # Artist objects
        self._car_marker = None
        self._trail_line = None

        # Animation statistics
        self.frames_rendered = 0
        self.distance_traveled = 0.0

    def initialize(self, start_x: float, start_y: float) -> None:
        """
        Initialize car at starting position.

        Args:
            start_x: Starting x coordinate (longitude)
            start_y: Starting y coordinate (latitude)
        """
        self.x = start_x
        self.y = start_y
        self.trail_positions = [(start_x, start_y)]

        # Create car marker
        self._car_marker = self.ax.scatter(
            [self.x], [self.y],
            c=self.color,
            s=self.size,
            marker=self.marker,
            edgecolors=self.edge_color,
            linewidths=self.edge_width,
            zorder=10,  # High z-order to appear on top
            label='Car'
        )

        # Create trail if enabled
        if self.trail_enabled:
            self._trail_line, = self.ax.plot(
                [self.x], [self.y],
                color=self.color,
                linewidth=2,
                alpha=self.trail_alpha,
                zorder=9
            )

    def update_position(self, new_x: float, new_y: float) -> None:
        """
        Update car position to new coordinates.

        Args:
            new_x: New x coordinate (longitude)
            new_y: New y coordinate (latitude)
        """
        if self.x is not None and self.y is not None:
            # Calculate distance moved
            dx = new_x - self.x
            dy = new_y - self.y
            distance = np.sqrt(dx**2 + dy**2)
            self.distance_traveled += distance

        # Update position
        self.x = new_x
        self.y = new_y
        self.frames_rendered += 1

        # Update car marker
        if self._car_marker is not None:
            self._car_marker.set_offsets([[self.x, self.y]])

        # Update trail
        if self.trail_enabled:
            self.trail_positions.append((self.x, self.y))

            # Limit trail length
            if len(self.trail_positions) > self.trail_length:
                self.trail_positions.pop(0)

            # Update trail line
            if self._trail_line is not None and len(self.trail_positions) > 1:
                trail_x = [pos[0] for pos in self.trail_positions]
                trail_y = [pos[1] for pos in self.trail_positions]
                self._trail_line.set_data(trail_x, trail_y)

    def get_position(self) -> Tuple[float, float]:
        """
        Get current car position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)

    def show_trail(self, enabled: bool) -> None:
        """
        Enable or disable trail effect.

        Args:
            enabled: True to show trail, False to hide
        """
        self.trail_enabled = enabled

        if self._trail_line is not None:
            self._trail_line.set_visible(enabled)

    def set_color(self, color: str) -> None:
        """
        Change car color dynamically.

        Args:
            color: New color (matplotlib color string)
        """
        self.color = color
        if self._car_marker is not None:
            self._car_marker.set_facecolors(color)

    def set_size(self, size: int) -> None:
        """
        Change car marker size dynamically.

        Args:
            size: New size
        """
        self.size = size
        if self._car_marker is not None:
            self._car_marker.set_sizes([size])

    def remove(self) -> None:
        """Remove car marker and trail from plot."""
        if self._car_marker is not None:
            self._car_marker.remove()
            self._car_marker = None

        if self._trail_line is not None:
            self._trail_line.remove()
            self._trail_line = None

    def get_stats(self) -> dict:
        """
        Get animation statistics.

        Returns:
            Dictionary with stats
        """
        return {
            'frames_rendered': self.frames_rendered,
            'distance_traveled': self.distance_traveled,
            'current_position': (self.x, self.y),
            'trail_enabled': self.trail_enabled,
            'trail_points': len(self.trail_positions)
        }


class DirectionalCarAnimator(CarAnimator):
    """
    Car animator with directional arrow showing heading.

    Extends CarAnimator to show which direction the car is facing.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with arrow marker by default."""
        kwargs.setdefault('marker', '^')  # Triangle/arrow
        super().__init__(*args, **kwargs)

        self.heading = 0.0  # Angle in degrees

    def update_position(self, new_x: float, new_y: float) -> None:
        """
        Update position and calculate heading direction.

        Args:
            new_x: New x coordinate
            new_y: New y coordinate
        """
        if self.x is not None and self.y is not None:
            # Calculate heading angle
            dx = new_x - self.x
            dy = new_y - self.y

            if dx != 0 or dy != 0:
                # Calculate angle in degrees (0 = East, 90 = North)
                angle = np.degrees(np.arctan2(dy, dx))
                self.heading = angle

        # Update position (parent method)
        super().update_position(new_x, new_y)

        # Rotate marker to face direction
        # Note: This requires recreating the marker
        # Matplotlib scatter doesn't support rotation well
        # For true rotation, use patches instead

    def get_heading(self) -> float:
        """
        Get current heading direction.

        Returns:
            Angle in degrees (0 = East, 90 = North)
        """
        return self.heading
