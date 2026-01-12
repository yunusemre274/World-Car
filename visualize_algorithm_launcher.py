"""
Launcher for algorithm visualization.
Run this from project root: python visualize_algorithm_launcher.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from examples.visualize_algorithm import main

if __name__ == "__main__":
    exit(main())
