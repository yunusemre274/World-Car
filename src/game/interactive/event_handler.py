"""
Event handler for matplotlib interactions.

Manages mouse and keyboard events, dispatching them to appropriate handlers
based on current game state.
"""

from typing import Callable, Optional, Dict, Any
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseEvent, KeyEvent


class EventHandler:
    """
    Central event dispatcher for matplotlib figure.

    Connects matplotlib events to game logic callbacks.
    Provides clean separation between UI events and game state changes.

    Example:
        >>> handler = EventHandler(fig)
        >>> handler.on_mouse_click = self.handle_click
        >>> handler.on_key_press = self.handle_key
        >>> handler.connect()
    """

    def __init__(self, figure: Figure):
        """
        Initialize the event handler.

        Args:
            figure: Matplotlib figure to attach events to
        """
        self.figure = figure
        self.enabled = True

        # Callback functions (set by game loop)
        self.on_mouse_click: Optional[Callable[[float, float, MouseEvent], None]] = None
        self.on_key_press: Optional[Callable[[str, KeyEvent], None]] = None

        # Connection IDs for cleanup
        self._mouse_cid = None
        self._key_cid = None

        # Event statistics (for debugging)
        self.stats = {
            "mouse_clicks": 0,
            "key_presses": 0,
            "ignored_events": 0
        }

    def connect(self) -> None:
        """
        Connect event handlers to the matplotlib figure.

        Must be called after setting callback functions.
        """
        if self.on_mouse_click is not None:
            self._mouse_cid = self.figure.canvas.mpl_connect(
                'button_press_event',
                self._handle_mouse_click
            )
            print("Mouse click events connected")

        if self.on_key_press is not None:
            self._key_cid = self.figure.canvas.mpl_connect(
                'key_press_event',
                self._handle_key_press
            )
            print("Keyboard events connected")

    def disconnect(self) -> None:
        """
        Disconnect event handlers.

        Should be called during cleanup.
        """
        if self._mouse_cid is not None:
            self.figure.canvas.mpl_disconnect(self._mouse_cid)
            self._mouse_cid = None

        if self._key_cid is not None:
            self.figure.canvas.mpl_disconnect(self._key_cid)
            self._key_cid = None

        print("Events disconnected")

    def _handle_mouse_click(self, event: MouseEvent) -> None:
        """
        Internal handler for mouse click events.

        Args:
            event: Matplotlib mouse event
        """
        if not self.enabled:
            self.stats["ignored_events"] += 1
            return

        # Only process left clicks within axes
        if event.button != 1:  # Left click
            return

        if event.inaxes is None:
            return

        # Get click coordinates
        click_x = event.xdata
        click_y = event.ydata

        if click_x is None or click_y is None:
            return

        # Dispatch to callback
        if self.on_mouse_click is not None:
            self.stats["mouse_clicks"] += 1
            self.on_mouse_click(click_x, click_y, event)

    def _handle_key_press(self, event: KeyEvent) -> None:
        """
        Internal handler for keyboard events.

        Args:
            event: Matplotlib keyboard event
        """
        if not self.enabled:
            self.stats["ignored_events"] += 1
            return

        key = event.key
        if key is None:
            return

        # Normalize key name
        key = key.lower()

        # Dispatch to callback
        if self.on_key_press is not None:
            self.stats["key_presses"] += 1
            self.on_key_press(key, event)

    def enable(self) -> None:
        """Enable event processing."""
        self.enabled = True

    def disable(self) -> None:
        """Disable event processing (events will be ignored)."""
        self.enabled = False

    def get_stats(self) -> Dict[str, int]:
        """
        Get event statistics.

        Returns:
            Dictionary with event counts
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset event statistics."""
        self.stats = {
            "mouse_clicks": 0,
            "key_presses": 0,
            "ignored_events": 0
        }


class KeyboardShortcuts:
    """
    Defines keyboard shortcuts for the game.

    Centralizes key bindings for easy modification.
    """

    # Primary controls
    ENTER = 'enter'
    RESTART = 'r'
    EXIT = 'escape'
    PAUSE = ' '  # Space

    # Alternative keys
    RESTART_ALT = ['r', 'R']
    EXIT_ALT = ['escape', 'q', 'Q']

    @classmethod
    def is_enter(cls, key: str) -> bool:
        """Check if key is ENTER."""
        return key in ['enter', 'return']

    @classmethod
    def is_restart(cls, key: str) -> bool:
        """Check if key is RESTART."""
        return key in cls.RESTART_ALT

    @classmethod
    def is_exit(cls, key: str) -> bool:
        """Check if key is EXIT."""
        return key in cls.EXIT_ALT

    @classmethod
    def is_pause(cls, key: str) -> bool:
        """Check if key is PAUSE."""
        return key == cls.PAUSE

    @classmethod
    def get_help_text(cls) -> str:
        """
        Get help text for keyboard shortcuts.

        Returns:
            Multi-line string with all shortcuts
        """
        return (
            "Keyboard Shortcuts:\n"
            "  ENTER - Start simulation\n"
            "  SPACE - Pause/Resume\n"
            "  R     - Restart\n"
            "  ESC/Q - Exit"
        )
