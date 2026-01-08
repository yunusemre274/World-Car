"""
Interactive game state machine.

Extends the base game state with user input states:
WAITING_START → WAITING_TARGET → READY → RUNNING → FINISHED

This allows for interactive node selection before running the simulation.
"""

from enum import Enum, auto
from typing import Optional


class InteractiveGameState(Enum):
    """
    State machine for interactive pathfinding game.

    State Flow:
    ┌─────────────────┐
    │  WAITING_START  │  ← User clicks to select start node
    └────────┬────────┘
             │ (start selected)
             ▼
    ┌─────────────────┐
    │ WAITING_TARGET  │  ← User clicks to select target node
    └────────┬────────┘
             │ (target selected)
             ▼
    ┌─────────────────┐
    │      READY      │  ← User presses ENTER to start
    └────────┬────────┘
             │ (ENTER pressed)
             ▼
    ┌─────────────────┐
    │     RUNNING     │  ← Algorithm executing, car moving
    └────────┬────────┘
             │ (destination reached)
             ▼
    ┌─────────────────┐
    │    FINISHED     │  ← Show summary, wait for R/ESC
    └─────────────────┘

    Keyboard Controls:
    - ENTER: Start simulation (when in READY state)
    - R: Restart (reset to WAITING_START)
    - ESC: Exit application
    - SPACE: Pause/resume (when in RUNNING state)
    """

    WAITING_START = auto()   # Waiting for user to click start node
    WAITING_TARGET = auto()  # Waiting for user to click target node
    READY = auto()           # Both nodes selected, waiting for ENTER
    RUNNING = auto()         # Simulation running
    PAUSED = auto()          # Simulation paused
    FINISHED = auto()        # Simulation complete
    ERROR = auto()           # Error state

    def __str__(self) -> str:
        """String representation for display."""
        return self.name.replace('_', ' ')

    @property
    def is_selecting(self) -> bool:
        """Check if currently in node selection phase."""
        return self in (InteractiveGameState.WAITING_START,
                       InteractiveGameState.WAITING_TARGET)

    @property
    def is_ready_to_run(self) -> bool:
        """Check if ready to start simulation."""
        return self == InteractiveGameState.READY

    @property
    def is_running(self) -> bool:
        """Check if simulation is actively running."""
        return self == InteractiveGameState.RUNNING

    @property
    def is_finished(self) -> bool:
        """Check if simulation has completed."""
        return self == InteractiveGameState.FINISHED

    @property
    def is_terminal(self) -> bool:
        """Check if in a terminal state."""
        return self in (InteractiveGameState.FINISHED,
                       InteractiveGameState.ERROR)

    @property
    def allows_mouse_input(self) -> bool:
        """Check if mouse clicks should be processed."""
        return self.is_selecting

    @property
    def allows_keyboard_input(self) -> bool:
        """Check if keyboard input should be processed."""
        return True  # All states can handle keyboard (R, ESC)

    def get_instruction_text(self) -> str:
        """
        Get user instruction text for current state.

        Returns:
            Instruction string to display to user
        """
        instructions = {
            InteractiveGameState.WAITING_START: "Click on the map to select START node",
            InteractiveGameState.WAITING_TARGET: "Click on the map to select TARGET node",
            InteractiveGameState.READY: "Press ENTER to start simulation",
            InteractiveGameState.RUNNING: "Simulation running... (SPACE to pause)",
            InteractiveGameState.PAUSED: "Paused (SPACE to resume, R to restart)",
            InteractiveGameState.FINISHED: "Simulation complete! (R to restart, ESC to exit)",
            InteractiveGameState.ERROR: "Error occurred (R to restart, ESC to exit)"
        }
        return instructions.get(self, "")


class StateTransition:
    """
    Helper class for managing state transitions.

    Validates transitions and provides clear error messages.
    """

    # Valid transitions map
    VALID_TRANSITIONS = {
        InteractiveGameState.WAITING_START: {
            InteractiveGameState.WAITING_TARGET,  # Start node selected
            InteractiveGameState.ERROR            # Error occurred
        },
        InteractiveGameState.WAITING_TARGET: {
            InteractiveGameState.READY,           # Target node selected
            InteractiveGameState.WAITING_START,   # Reset (R pressed)
            InteractiveGameState.ERROR
        },
        InteractiveGameState.READY: {
            InteractiveGameState.RUNNING,         # ENTER pressed
            InteractiveGameState.WAITING_START,   # Reset (R pressed)
            InteractiveGameState.ERROR
        },
        InteractiveGameState.RUNNING: {
            InteractiveGameState.PAUSED,          # SPACE pressed
            InteractiveGameState.FINISHED,        # Simulation complete
            InteractiveGameState.WAITING_START,   # Reset (R pressed)
            InteractiveGameState.ERROR
        },
        InteractiveGameState.PAUSED: {
            InteractiveGameState.RUNNING,         # SPACE pressed
            InteractiveGameState.WAITING_START,   # Reset (R pressed)
            InteractiveGameState.ERROR
        },
        InteractiveGameState.FINISHED: {
            InteractiveGameState.WAITING_START,   # Reset (R pressed)
        },
        InteractiveGameState.ERROR: {
            InteractiveGameState.WAITING_START,   # Reset (R pressed)
        }
    }

    @classmethod
    def is_valid(cls, from_state: InteractiveGameState,
                 to_state: InteractiveGameState) -> bool:
        """
        Check if a state transition is valid.

        Args:
            from_state: Current state
            to_state: Desired next state

        Returns:
            True if transition is valid, False otherwise
        """
        valid_targets = cls.VALID_TRANSITIONS.get(from_state, set())
        return to_state in valid_targets

    @classmethod
    def validate(cls, from_state: InteractiveGameState,
                to_state: InteractiveGameState) -> None:
        """
        Validate a state transition, raising exception if invalid.

        Args:
            from_state: Current state
            to_state: Desired next state

        Raises:
            ValueError: If transition is invalid
        """
        if not cls.is_valid(from_state, to_state):
            raise ValueError(
                f"Invalid state transition: {from_state} → {to_state}. "
                f"Valid transitions from {from_state}: "
                f"{cls.VALID_TRANSITIONS.get(from_state, set())}"
            )
