"""
Camera controller for following car movement.

Provides cinematic camera effects like following the car, smooth panning,
and dynamic zoom for enhanced visualization.
"""

from typing import Tuple, Optional
from matplotlib.axes import Axes
import numpy as np


class CameraMode:
    """Camera behavior modes."""
    STATIC = 'static'        # Camera doesn't move
    FOLLOW = 'follow'        # Camera follows car
    FOLLOW_SMOOTH = 'follow_smooth'  # Smoothed following
    LOOKAHEAD = 'lookahead'  # Camera looks ahead of car


class CameraController:
    """
    Controls camera position and zoom for car animation.

    Provides various camera modes for different visual effects:
    - Static: Traditional fixed view
    - Follow: Camera centers on car (can be jarring)
    - Follow Smooth: Smoothed camera movement (recommended)
    - Lookahead: Camera leads the car slightly

    Example:
        >>> camera = CameraController(ax, mode='follow_smooth')
        >>> camera.update(car_x, car_y)  # Update camera each frame
    """

    def __init__(self,
                 ax: Axes,
                 mode: str = CameraMode.STATIC,
                 padding: float = 0.001,
                 smoothing: float = 0.15,
                 lookahead_distance: float = 0.0005):
        """
        Initialize the camera controller.

        Args:
            ax: Matplotlib axes to control
            mode: Camera mode (see CameraMode)
            padding: Padding around car as fraction of view
            smoothing: Smoothing factor for smooth follow (0=instant, 1=no follow)
            lookahead_distance: Distance to look ahead (in coordinate units)
        """
        self.ax = ax
        self.mode = mode
        self.padding = padding
        self.smoothing = smoothing
        self.lookahead_distance = lookahead_distance

        # Camera state
        self.target_x: Optional[float] = None
        self.target_y: Optional[float] = None
        self.current_x: Optional[float] = None
        self.current_y: Optional[float] = None

        # View bounds
        self.view_width: Optional[float] = None
        self.view_height: Optional[float] = None

        # Statistics
        self.updates = 0

    def initialize(self, initial_x: float, initial_y: float,
                  view_width: Optional[float] = None,
                  view_height: Optional[float] = None) -> None:
        """
        Initialize camera at starting position.

        Args:
            initial_x: Initial x coordinate
            initial_y: Initial y coordinate
            view_width: Initial view width (None = use current)
            view_height: Initial view height (None = use current)
        """
        self.target_x = initial_x
        self.target_y = initial_y
        self.current_x = initial_x
        self.current_y = initial_y

        if view_width is not None:
            self.view_width = view_width
        else:
            xlim = self.ax.get_xlim()
            self.view_width = xlim[1] - xlim[0]

        if view_height is not None:
            self.view_height = view_height
        else:
            ylim = self.ax.get_ylim()
            self.view_height = ylim[1] - ylim[0]

    def update(self, car_x: float, car_y: float,
              heading: Optional[float] = None) -> None:
        """
        Update camera position based on car position.

        Args:
            car_x: Car x coordinate
            car_y: Car y coordinate
            heading: Car heading angle in degrees (for lookahead)
        """
        if self.mode == CameraMode.STATIC:
            # No camera movement
            return

        # Calculate target position based on mode
        if self.mode == CameraMode.FOLLOW:
            # Instant follow - camera locked to car
            self.target_x = car_x
            self.target_y = car_y

        elif self.mode == CameraMode.FOLLOW_SMOOTH:
            # Smooth follow with interpolation
            if self.current_x is None:
                self.current_x = car_x
            if self.current_y is None:
                self.current_y = car_y

            # Smooth interpolation
            self.current_x += (car_x - self.current_x) * (1 - self.smoothing)
            self.current_y += (car_y - self.current_y) * (1 - self.smoothing)

            self.target_x = self.current_x
            self.target_y = self.current_y

        elif self.mode == CameraMode.LOOKAHEAD:
            # Camera looks ahead of car in movement direction
            if heading is not None:
                # Calculate lookahead point
                angle_rad = np.radians(heading)
                lookahead_x = car_x + self.lookahead_distance * np.cos(angle_rad)
                lookahead_y = car_y + self.lookahead_distance * np.sin(angle_rad)

                self.target_x = lookahead_x
                self.target_y = lookahead_y
            else:
                # No heading info - fall back to follow
                self.target_x = car_x
                self.target_y = car_y

        # Apply camera position
        if self.target_x is not None and self.target_y is not None:
            self._apply_camera_position()

        self.updates += 1

    def _apply_camera_position(self) -> None:
        """Apply the calculated camera position to axes."""
        if self.view_width is None or self.view_height is None:
            return

        # Calculate new axis limits centered on target
        half_width = self.view_width / 2
        half_height = self.view_height / 2

        new_xlim = (
            self.target_x - half_width,
            self.target_x + half_width
        )
        new_ylim = (
            self.target_y - half_height,
            self.target_y + half_height
        )

        # Apply limits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

    def zoom(self, factor: float) -> None:
        """
        Zoom camera in or out.

        Args:
            factor: Zoom factor (>1 = zoom in, <1 = zoom out)
        """
        if self.view_width is not None:
            self.view_width /= factor
        if self.view_height is not None:
            self.view_height /= factor

        # Reapply camera position with new zoom
        if self.target_x is not None and self.target_y is not None:
            self._apply_camera_position()

    def set_mode(self, mode: str) -> None:
        """
        Change camera mode dynamically.

        Args:
            mode: New camera mode
        """
        self.mode = mode

        # Reset interpolation state
        if mode == CameraMode.FOLLOW_SMOOTH:
            if self.target_x is not None:
                self.current_x = self.target_x
            if self.target_y is not None:
                self.current_y = self.target_y

    def get_stats(self) -> dict:
        """
        Get camera statistics.

        Returns:
            Dictionary with camera stats
        """
        return {
            'mode': self.mode,
            'updates': self.updates,
            'current_position': (self.current_x, self.current_y),
            'target_position': (self.target_x, self.target_y),
            'view_size': (self.view_width, self.view_height)
        }


class DynamicCameraController(CameraController):
    """
    Camera controller with dynamic zoom based on speed.

    Automatically adjusts zoom level based on car speed - zooms out
    when moving fast, zooms in when moving slow.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with dynamic zoom settings."""
        self.min_zoom = kwargs.pop('min_zoom', 0.5)
        self.max_zoom = kwargs.pop('max_zoom', 2.0)
        super().__init__(*args, **kwargs)

        self.prev_x: Optional[float] = None
        self.prev_y: Optional[float] = None
        self.speed = 0.0

    def update(self, car_x: float, car_y: float,
              heading: Optional[float] = None) -> None:
        """
        Update camera with dynamic zoom based on speed.

        Args:
            car_x: Car x coordinate
            car_y: Car y coordinate
            heading: Car heading angle
        """
        # Calculate speed
        if self.prev_x is not None and self.prev_y is not None:
            dx = car_x - self.prev_x
            dy = car_y - self.prev_y
            self.speed = np.sqrt(dx**2 + dy**2)

            # Adjust zoom based on speed
            # Higher speed = zoom out more
            # This is a simple linear mapping
            speed_factor = 1.0 + (self.speed * 1000)  # Scale factor
            zoom_factor = np.clip(speed_factor, self.min_zoom, self.max_zoom)

            # Apply zoom gradually
            target_width = self.view_width * zoom_factor
            self.view_width += (target_width - self.view_width) * 0.1

        self.prev_x = car_x
        self.prev_y = car_y

        # Update camera position
        super().update(car_x, car_y, heading)
