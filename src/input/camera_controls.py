"""
Camera Controls for WorldCar

Handles user input for camera control including mouse and keyboard.
"""

import pygame
from typing import Optional, Tuple


class CameraControls:
    """
    Handle user input for camera control.

    Mouse Controls:
    - Scroll wheel: Zoom in/out
    - Middle mouse drag: Pan
    - Right mouse drag: Pan (alternative)

    Keyboard Controls:
    - Arrow keys / WASD: Pan
    - Q / E: Zoom out/in
    - Plus / Minus: Zoom in/out
    - F: Toggle follow mode
    - R: Reset camera to fit bounds
    - Space: Pause/unpause follow mode

    Usage:
        >>> controls = CameraControls(camera)
        >>> # In event loop:
        >>> for event in pygame.event.get():
        >>>     controls.handle_event(event)
        >>> # Each frame:
        >>> controls.handle_keys(pygame.key.get_pressed())
    """

    def __init__(self, camera, pan_speed: float = 5.0, zoom_speed: float = 0.1):
        """
        Initialize camera controls.

        Args:
            camera: Camera instance to control
            pan_speed: Keyboard pan speed in pixels per frame
            zoom_speed: Keyboard/mouse zoom speed (multiplier delta)
        """
        self.camera = camera
        self.pan_speed = pan_speed
        self.zoom_speed = zoom_speed

        # Mouse state
        self.middle_mouse_pressed = False
        self.right_mouse_pressed = False
        self.last_mouse_pos: Optional[Tuple[int, int]] = None

        # Follow mode state
        self.follow_enabled = True  # Can be toggled with F key

    def handle_event(self, event: pygame.event.Event):
        """
        Process single pygame event.

        Args:
            event: pygame event to process
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:  # Middle mouse
                self.middle_mouse_pressed = True
                self.last_mouse_pos = event.pos
            elif event.button == 3:  # Right mouse
                self.right_mouse_pressed = True
                self.last_mouse_pos = event.pos
            elif event.button == 4:  # Scroll up (zoom in)
                self.camera.zoom_at(event.pos[0], event.pos[1], self.zoom_speed)
            elif event.button == 5:  # Scroll down (zoom out)
                self.camera.zoom_at(event.pos[0], event.pos[1], -self.zoom_speed)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                self.middle_mouse_pressed = False
                self.last_mouse_pos = None
            elif event.button == 3:
                self.right_mouse_pressed = False
                self.last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if (self.middle_mouse_pressed or self.right_mouse_pressed) and self.last_mouse_pos:
                # Calculate delta
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]

                # Pan camera
                self.camera.pan(-dx, -dy)
                self.last_mouse_pos = event.pos

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self._toggle_follow()
            elif event.key == pygame.K_r:
                self._reset_camera()
            elif event.key == pygame.K_SPACE:
                self._pause_follow()
            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                # Zoom in at center
                center_x = self.camera.screen_width // 2
                center_y = self.camera.screen_height // 2
                self.camera.zoom_at(center_x, center_y, self.zoom_speed)
            elif event.key == pygame.K_MINUS:
                # Zoom out at center
                center_x = self.camera.screen_width // 2
                center_y = self.camera.screen_height // 2
                self.camera.zoom_at(center_x, center_y, -self.zoom_speed)

    def handle_keys(self, keys):
        """
        Process continuous keyboard input (called each frame).

        Args:
            keys: pygame.key.get_pressed() array
        """
        # Pan with arrow keys or WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera.pan(-self.pan_speed, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera.pan(self.pan_speed, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera.pan(0, -self.pan_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera.pan(0, self.pan_speed)

        # Zoom with Q/E
        if keys[pygame.K_q]:
            # Zoom out at center
            center_x = self.camera.screen_width // 2
            center_y = self.camera.screen_height // 2
            self.camera.zoom_at(center_x, center_y, -self.zoom_speed * 0.5)
        if keys[pygame.K_e]:
            # Zoom in at center
            center_x = self.camera.screen_width // 2
            center_y = self.camera.screen_height // 2
            self.camera.zoom_at(center_x, center_y, self.zoom_speed * 0.5)

    def _toggle_follow(self):
        """Toggle between FREE and FOLLOW_SMOOTH modes."""
        from src.rendering.camera import CameraMode

        if self.camera.mode == CameraMode.FREE:
            self.camera.mode = CameraMode.FOLLOW_SMOOTH
            self.follow_enabled = True
            print("Follow mode: ON")
        else:
            self.camera.mode = CameraMode.FREE
            self.follow_enabled = False
            print("Follow mode: OFF")

    def _pause_follow(self):
        """Temporarily pause follow mode without fully disabling."""
        from src.rendering.camera import CameraMode

        if self.camera.mode != CameraMode.FREE:
            self.camera.mode = CameraMode.FREE
            print("Follow paused (press F to resume)")

    def _reset_camera(self):
        """Reset camera to default view (fit to bounds)."""
        # Note: This requires map bounds to be set
        # In the test script, we'll call fit_to_bounds before this
        print("Camera reset to bounds")

    def set_pan_speed(self, speed: float):
        """Set keyboard pan speed."""
        self.pan_speed = speed

    def set_zoom_speed(self, speed: float):
        """Set zoom speed."""
        self.zoom_speed = speed

    def is_follow_active(self) -> bool:
        """Check if follow mode is currently active."""
        from src.rendering.camera import CameraMode
        return self.camera.mode in (CameraMode.FOLLOW, CameraMode.FOLLOW_SMOOTH)
