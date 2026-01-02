"""
Configuration settings for WorldCar routing system.

This module contains all configuration constants used throughout the application.
Centralizing configuration makes the system easy to modify and extend.
"""

import os
from pathlib import Path

# ============================================================================
# Project Paths
# ============================================================================

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# ============================================================================
# Location Settings
# ============================================================================

# Default location for road network extraction
DEFAULT_LOCATION = "Kadıköy, Istanbul, Turkey"

# Network type: 'drive', 'walk', 'bike', or 'all'
# 'drive' includes only roads accessible by cars
NETWORK_TYPE = "drive"

# ============================================================================
# Graph Settings
# ============================================================================

# Edge weight attribute for routing (distance in meters)
EDGE_WEIGHT_ATTRIBUTE = "length"

# Whether to simplify the graph (remove nodes that aren't junctions)
# Simplification reduces graph size while maintaining accuracy
SIMPLIFY_GRAPH = True

# Whether to retain all nodes, even isolated ones
RETAIN_ALL_NODES = False

# ============================================================================
# Caching Settings
# ============================================================================

# Directory for caching raw OSM data
CACHE_DIRECTORY = str(RAW_DATA_DIR)

# Whether to save processed graphs to disk
SAVE_PROCESSED_GRAPH = True

# Path for saving/loading processed graph
PROCESSED_GRAPH_FILENAME = "kadiköy_graph.graphml"
PROCESSED_GRAPH_PATH = PROCESSED_DATA_DIR / PROCESSED_GRAPH_FILENAME

# ============================================================================
# Node Mapping Settings
# ============================================================================

# Use KDTree for efficient nearest neighbor search
KDTREE_ENABLED = True

# Maximum search radius for finding nearest node (meters)
# Coordinates further than this from any road will be rejected
MAX_SEARCH_RADIUS_METERS = 500

# ============================================================================
# Coordinate System
# ============================================================================

# Default coordinate reference system (WGS84)
DEFAULT_CRS = "EPSG:4326"

# Projected CRS for accurate distance calculations (UTM)
# Will be determined automatically based on location
PROJECTED_CRS = None  # Auto-detect

# ============================================================================
# Routing Settings
# ============================================================================

# Default routing algorithm
DEFAULT_ALGORITHM = "dijkstra"

# Default weight for routing
DEFAULT_WEIGHT = EDGE_WEIGHT_ATTRIBUTE

# ============================================================================
# Performance Settings
# ============================================================================

# Enable performance logging
ENABLE_PERFORMANCE_LOGGING = False

# Timeout for OSM data download (seconds)
DOWNLOAD_TIMEOUT = 180

# ============================================================================
# Validation Settings
# ============================================================================

# Minimum valid latitude
MIN_LATITUDE = -90.0

# Maximum valid latitude
MAX_LATITUDE = 90.0

# Minimum valid longitude
MIN_LONGITUDE = -180.0

# Maximum valid longitude
MAX_LONGITUDE = 180.0

# ============================================================================
# Display Settings
# ============================================================================

# Number of decimal places for coordinate display
COORDINATE_PRECISION = 6

# Number of decimal places for distance display (meters)
DISTANCE_PRECISION = 2

# ============================================================================
# Utility Functions
# ============================================================================

def ensure_data_directories():
    """
    Ensure that all required data directories exist.

    Creates data/, data/raw/, and data/processed/ directories if they don't exist.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


# Initialize data directories on module import
ensure_data_directories()
