"""
Camera System for WorldCar

Provides 2D camera with pan, zoom, and follow modes for navigating large maps.
"""

from enum import Enum
from typing import Tuple, Optional


class CameraMode(Enum):
    """Camera operating modes."""
    FREE = "free"                    # User-controlled pan/zoom
    FOLLOW = "follow"                # Hard lock to target
    FOLLOW_SMOOTH = "follow_smooth"  # Smooth interpolation to target


class Camera:
    """
    2D camera for panning and zooming the map view.

    Coordinate System:
    - Camera has position (x, y) in world space
    - world_to_screen() transforms world coords to screen coords
    - Supports zoom (1.0 = base, 2.0 = 2x zoomed in)

    Modes:
    - FREE: User-controlled pan/zoom
    - FOLLOW: Camera locked to target position
    - FOLLOW_SMOOTH: Camera smoothly follows target

    Example:
        >>> camera = Camera(1280, 720)
        >>> camera.zoom = 2.0  # 2x zoom
        >>> screen_x, screen_y = camera.world_to_screen(world_x, world_y)
    """

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize camera.

        Args:
            screen_width: Window width in pixels
            screen_height: Window height in pixels
        """
        # Screen dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Camera position (center point in world coordinates)
        self.x = 0.0
        self.y = 0.0

        # Zoom level (scale factor)
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 5.0

        # Follow mode
        self.mode = CameraMode.FOLLOW_SMOOTH
        self.target_x = 0.0
        self.target_y = 0.0
        self.smoothing = 0.1  # Lerp factor (0 = no movement, 1 = instant)

        # Bounds (set by fit_to_bounds)
        self.world_min_x = 0.0
        self.world_min_y = 0.0
        self.world_max_x = 1000.0
        self.world_max_y = 1000.0

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        Transform world coordinates to screen coordinates.

        Args:
            world_x: X position in world space
            world_y: Y position in world space

        Returns:
            (screen_x, screen_y) tuple in pixels
        """
        # Apply camera transform
        cam_x = (world_x - self.x) * self.zoom
        cam_y = (world_y - self.y) * self.zoom

        # Center on screen
        screen_x = cam_x + self.screen_width / 2
        screen_y = cam_y + self.screen_height / 2

        return (int(screen_x), int(screen_y))

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """
        Transform screen coordinates to world coordinates.

        Useful for mouse picking and interaction.

        Args:
            screen_x: X position in screen space (pixels)
            screen_y: Y position in screen space (pixels)

        Returns:
            (world_x, world_y) tuple
        """
        # Reverse the world_to_screen transform
        cam_x = screen_x - self.screen_width / 2
        cam_y = screen_y - self.screen_height / 2

        world_x = cam_x / self.zoom + self.x
        world_y = cam_y / self.zoom + self.y

        return (world_x, world_y)

    def pan(self, dx: float, dy: float):
        """
        Move camera by screen pixels.

        Args:
            dx: Horizontal movement in screen pixels
            dy: Vertical movement in screen pixels
        """
        # Convert screen movement to world movement
        self.x -= dx / self.zoom
        self.y -= dy / self.zoom

        # Clamp to bounds
        self._clamp_to_bounds()

    def zoom_at(self, screen_x: int, screen_y: int, zoom_delta: float):
        """
        Zoom camera at a specific screen point (e.g., mouse cursor).

        Keeps the world point under the screen point stationary.

        Args:
            screen_x: Screen X position to zoom at
            screen_y: Screen Y position to zoom at
            zoom_delta: Zoom change (+0.1 = zoom in, -0.1 = zoom out)
        """
        # Calculate world position at screen point before zoom
        world_x_before = (screen_x - self.screen_width / 2) / self.zoom + self.x
        world_y_before = (screen_y - self.screen_height / 2) / self.zoom + self.y

        # Apply zoom
        new_zoom = self.zoom * (1.0 + zoom_delta)
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        # Calculate new camera position so world point stays at same screen position
        self.x = world_x_before - (screen_x - self.screen_width / 2) / new_zoom
        self.y = world_y_before - (screen_y - self.screen_height / 2) / new_zoom
        self.zoom = new_zoom

        # Clamp to bounds
        self._clamp_to_bounds()

    def set_zoom(self, zoom: float):
        """
        Set zoom level (centered on current camera position).

        Args:
            zoom: New zoom level (1.0 = base, 2.0 = 2x)
        """
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))

    def update(self, dt: float, target_pos: Optional[Tuple[float, float]] = None):
        """
        Update camera each frame.

        Handles smooth following in FOLLOW_SMOOTH mode.

        Args:
            dt: Delta time in seconds
            target_pos: (world_x, world_y) to follow if in follow mode
        """
        if self.mode == CameraMode.FOLLOW_SMOOTH and target_pos:
            target_x, target_y = target_pos

            # Smooth interpolation (lerp)
            self.x += (target_x - self.x) * self.smoothing
            self.y += (target_y - self.y) * self.smoothing

            # Clamp to bounds
            self._clamp_to_bounds()

        elif self.mode == CameraMode.FOLLOW and target_pos:
            # Hard lock to target
            self.x, self.y = target_pos

            # Clamp to bounds
            self._clamp_to_bounds()

    def fit_to_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float, padding: float = 0.1):
        """
        Fit camera to show entire world bounds.

        Args:
            min_x: Minimum world X
            min_y: Minimum world Y
            max_x: Maximum world X
            max_y: Maximum world Y
            padding: Padding factor (0.1 = 10% padding)
        """
        # Store bounds
        self.world_min_x = min_x
        self.world_min_y = min_y
        self.world_max_x = max_x
        self.world_max_y = max_y

        # Calculate world size
        world_width = max_x - min_x
        world_height = max_y - min_y

        if world_width <= 0 or world_height <= 0:
            return  # Invalid bounds

        # Calculate zoom to fit (with padding)
        zoom_x = (self.screen_width * (1 - padding)) / world_width
        zoom_y = (self.screen_height * (1 - padding)) / world_height
        self.zoom = min(zoom_x, zoom_y)

        # Clamp zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

        # Center camera on world center
        self.x = (min_x + max_x) / 2
        self.y = (min_y + max_y) / 2

    def _clamp_to_bounds(self):
        """Prevent camera from going outside world bounds."""
        # Calculate visible world area
        visible_width = self.screen_width / self.zoom
        visible_height = self.screen_height / self.zoom

        # Calculate max camera position (so world bounds stay on screen)
        max_offset_x = self.world_max_x - visible_width / 2
        min_offset_x = self.world_min_x + visible_width / 2

        max_offset_y = self.world_max_y - visible_height / 2
        min_offset_y = self.world_min_y + visible_height / 2

        # Clamp camera position
        self.x = max(min_offset_x, min(self.x, max_offset_x))
        self.y = max(min_offset_y, min(self.y, max_offset_y))

    def set_mode(self, mode: CameraMode):
        """
        Change camera mode.

        Args:
            mode: New camera mode
        """
        self.mode = mode

    def toggle_follow_mode(self):
        """Toggle between FREE and FOLLOW_SMOOTH modes."""
        if self.mode == CameraMode.FREE:
            self.mode = CameraMode.FOLLOW_SMOOTH
        else:
            self.mode = CameraMode.FREE

    def get_visible_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get world bounds of visible area.

        Returns:
            (min_x, min_y, max_x, max_y) in world coordinates
        """
        # Calculate visible world area
        visible_width = self.screen_width / self.zoom
        visible_height = self.screen_height / self.zoom

        min_x = self.x - visible_width / 2
        max_x = self.x + visible_width / 2
        min_y = self.y - visible_height / 2
        max_y = self.y + visible_height / 2

        return (min_x, min_y, max_x, max_y)

    def is_on_screen(self, world_x: float, world_y: float) -> bool:
        """
        Check if a world point is visible on screen.

        Useful for culling objects outside view.

        Args:
            world_x: World X coordinate
            world_y: World Y coordinate

        Returns:
            True if point is visible
        """
        min_x, min_y, max_x, max_y = self.get_visible_bounds()
        return min_x <= world_x <= max_x and min_y <= world_y <= max_y

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"Camera(pos=({self.x:.1f}, {self.y:.1f}), "
                f"zoom={self.zoom:.2f}, mode={self.mode.value})")
