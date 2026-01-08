"""
Launcher for interactive game.
Run this from project root: python run_interactive.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from examples.play_interactive import main

if __name__ == "__main__":
    exit(main())
