"""
Game module for interactive pathfinding simulation.

This module provides a game-like architecture for visualizing shortest path
algorithms on real-world road networks. It includes:
- State machine for game flow
- Car entity for path traversal
- Game loop with fixed timestep
- Rendering system for visualization
"""

from .game_state import GameState
from .car import Car
from .game_loop import GameLoop

__all__ = ["GameState", "Car", "GameLoop"]
