"""
Game state management for pathfinding simulation.

Defines the state machine that controls the flow of the game:
- INIT: Initial setup, loading resources
- RUNNING: Active simulation, car moving along path
- PAUSED: Simulation paused, waiting for user input
- FINISHED: Car reached destination
- ERROR: Error state (e.g., no path found)
"""

from enum import Enum, auto


class GameState(Enum):
    """
    Enumeration of possible game states.

    The game follows this state machine:
    INIT → RUNNING → FINISHED
           ↓     ↑
         PAUSED
           ↓
         ERROR

    Attributes:
        INIT: Initial state, setting up game world
        RUNNING: Active simulation, car is moving
        PAUSED: Simulation paused by user
        FINISHED: Car reached destination
        ERROR: Error occurred (invalid path, etc.)
    """

    INIT = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    ERROR = auto()

    def __str__(self) -> str:
        """String representation for logging and display."""
        return self.name

    @property
    def is_active(self) -> bool:
        """Check if game is in an active state (not finished or error)."""
        return self in (GameState.INIT, GameState.RUNNING, GameState.PAUSED)

    @property
    def is_terminal(self) -> bool:
        """Check if game is in a terminal state (finished or error)."""
        return self in (GameState.FINISHED, GameState.ERROR)

    @property
    def allows_movement(self) -> bool:
        """Check if car movement is allowed in this state."""
        return self == GameState.RUNNING
