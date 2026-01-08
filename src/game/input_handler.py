"""
Input handler for game controls.

Placeholder for future interactive features:
- Mouse clicks for selecting start/end points
- Keyboard controls for pause/resume
- UI button clicks

Currently provides a basic structure for event handling.
"""

from typing import Optional, Callable
from enum import Enum, auto


class InputEvent(Enum):
    """Types of input events."""
    MOUSE_CLICK = auto()
    KEY_PRESS = auto()
    PAUSE_TOGGLE = auto()
    RESET = auto()
    QUIT = auto()


class InputHandler:
    """
    Handles user input events for the game.

    This is a placeholder structure for future interactive features.
    Can be extended to support:
    - Mouse-based node selection
    - Keyboard shortcuts
    - UI controls

    Attributes:
        enabled: Whether input handling is active
    """

    def __init__(self):
        """Initialize the input handler."""
        self.enabled = True
        self._event_callbacks = {}

    def register_callback(self, event_type: InputEvent, callback: Callable) -> None:
        """
        Register a callback for a specific event type.

        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        self._event_callbacks[event_type] = callback

    def handle_keypress(self, key: str) -> Optional[InputEvent]:
        """
        Handle a keyboard input.

        Args:
            key: Key that was pressed

        Returns:
            InputEvent if recognized, None otherwise
        """
        if not self.enabled:
            return None

        # Map keys to events (can be expanded)
        key_map = {
            ' ': InputEvent.PAUSE_TOGGLE,  # Spacebar
            'p': InputEvent.PAUSE_TOGGLE,
            'r': InputEvent.RESET,
            'q': InputEvent.QUIT,
            'escape': InputEvent.QUIT
        }

        return key_map.get(key.lower())

    def handle_mouse_click(self, x: float, y: float) -> Optional[InputEvent]:
        """
        Handle a mouse click event.

        Args:
            x: X coordinate of click
            y: Y coordinate of click

        Returns:
            InputEvent if action should be taken, None otherwise

        Note:
            This is a placeholder for future node selection features.
        """
        if not self.enabled:
            return None

        # Future: Convert (x, y) to nearest node
        # Future: Trigger path recalculation
        return InputEvent.MOUSE_CLICK

    def process_event(self, event: InputEvent) -> None:
        """
        Process an input event by calling registered callback.

        Args:
            event: The event to process
        """
        callback = self._event_callbacks.get(event)
        if callback is not None:
            callback()

    def enable(self) -> None:
        """Enable input handling."""
        self.enabled = True

    def disable(self) -> None:
        """Disable input handling."""
        self.enabled = False
