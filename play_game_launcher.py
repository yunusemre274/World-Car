"""
Launcher script for the WorldCar pathfinding game.
Run this from the project root directory.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the game
from examples.play_game import main

if __name__ == "__main__":
    exit(main())
