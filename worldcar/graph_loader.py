"""
Graph Loader Module for WorldCar routing system.

This module handles downloading road network data from OpenStreetMap using OSMnx,
creating NetworkX graphs, and managing graph caching for efficient repeated use.
"""

import os
import logging
from typing import Optional
from pathlib import Path

import osmnx as ox
import networkx as nx

from worldcar.config import (
    DEFAULT_LOCATION,
    NETWORK_TYPE,
    SIMPLIFY_GRAPH,
    RETAIN_ALL_NODES,
    CACHE_DIRECTORY,
    SAVE_PROCESSED_GRAPH,
    PROCESSED_GRAPH_PATH,
    DOWNLOAD_TIMEOUT,
)
from worldcar.utils import validate_graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OSMnx
ox.settings.log_console = True
ox.settings.use_cache = True
ox.settings.cache_folder = CACHE_DIRECTORY


class GraphLoader:
    """
    Handles OSM data extraction and graph creation.

    This class provides methods to download road network data from OpenStreetMap,
    create NetworkX graphs, and manage caching for efficient repeated use.

    Attributes:
        location (str): Geographic location to extract (e.g., "Kadıköy, Istanbul, Turkey")
        network_type (str): Type of road network ('drive', 'walk', 'bike', 'all')
        simplify (bool): Whether to simplify the graph by removing non-junction nodes
        graph (nx.MultiDiGraph): The loaded or downloaded graph

    Example:
        >>> loader = GraphLoader("Kadıköy, Istanbul, Turkey")
        >>> G = loader.get_or_create_graph()
        >>> print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
        Nodes: 12453, Edges: 28901
    """

    def __init__(
        self,
        location: str = DEFAULT_LOCATION,
        network_type: str = NETWORK_TYPE,
        simplify: bool = SIMPLIFY_GRAPH,
    ):
        """
        Initialize the GraphLoader.

        Args:
            location: Geographic location (place name, address, or coordinates)
            network_type: Type of network to download ('drive', 'walk', 'bike', 'all')
            simplify: Whether to simplify the graph
        """
        self.location = location
        self.network_type = network_type
        self.simplify = simplify
        self.graph: Optional[nx.MultiDiGraph] = None

        logger.info(
            f"GraphLoader initialized for location: {location}, "
            f"network_type: {network_type}, simplify: {simplify}"
        )

    def download_network(self) -> nx.MultiDiGraph:
        """
        Download road network from OpenStreetMap.

        Uses OSMnx to download the road network for the specified location.
        The graph is automatically cached by OSMnx for faster subsequent loads.

        Returns:
            NetworkX MultiDiGraph with road network data

        Raises:
            ValueError: If the location cannot be found or network download fails
            ConnectionError: If unable to connect to OSM servers

        Example:
            >>> loader = GraphLoader("Kadıköy, Istanbul, Turkey")
            >>> G = loader.download_network()
            >>> print(f"Downloaded graph with {G.number_of_nodes()} nodes")
            Downloaded graph with 12453 nodes
        """
        logger.info(f"Downloading road network for: {self.location}")

        try:
            # Download network from OSM
            G = ox.graph_from_place(
                self.location,
                network_type=self.network_type,
                simplify=self.simplify,
                retain_all=RETAIN_ALL_NODES,
                truncate_by_edge=True,
            )

            logger.info(
                f"Successfully downloaded graph: {G.number_of_nodes()} nodes, "
                f"{G.number_of_edges()} edges"
            )

            # Prepare graph for routing
            G = self.prepare_graph(G)

            return G

        except Exception as e:
            logger.error(f"Failed to download network: {str(e)}")
            raise ValueError(
                f"Could not download road network for '{self.location}'. "
                f"Error: {str(e)}"
            ) from e

    def prepare_graph(self, G: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Prepare graph for routing operations.

        Ensures the graph has all required attributes and structure for routing:
        - Verifies edge weights (length) exist
        - Validates graph structure
        - Adds any missing attributes

        Args:
            G: NetworkX graph to prepare

        Returns:
            Prepared NetworkX graph

        Raises:
            ValueError: If graph validation fails
        """
        logger.info("Preparing graph for routing...")

        # Validate graph structure
        is_valid, error_msg = validate_graph(G)
        if not is_valid:
            raise ValueError(f"Graph validation failed: {error_msg}")

        # Ensure all edges have 'length' attribute
        # OSMnx should already add this, but we verify
        missing_length = []
        for u, v, key, data in G.edges(keys=True, data=True):
            if 'length' not in data:
                missing_length.append((u, v, key))

        if missing_length:
            logger.warning(
                f"Found {len(missing_length)} edges missing 'length' attribute. "
                "Adding edge geometries..."
            )
            G = ox.add_edge_lengths(G)

        # Verify connectivity
        if not nx.is_weakly_connected(G):
            num_components = nx.number_weakly_connected_components(G)
            logger.warning(
                f"Graph is not fully connected. "
                f"It has {num_components} weakly connected components."
            )

            # Get largest connected component
            largest_cc = max(nx.weakly_connected_components(G), key=len)
            logger.info(
                f"Largest component has {len(largest_cc)} nodes "
                f"({len(largest_cc) / G.number_of_nodes() * 100:.1f}% of total)"
            )

        logger.info("Graph preparation complete.")
        return G

    def save_graph(
        self, G: nx.MultiDiGraph, filepath: Optional[str] = None
    ) -> None:
        """
        Save graph to disk in GraphML format.

        GraphML format preserves all node and edge attributes, making it
        suitable for caching processed graphs.

        Args:
            G: NetworkX graph to save
            filepath: Path to save file (default: config.PROCESSED_GRAPH_PATH)

        Example:
            >>> loader = GraphLoader()
            >>> G = loader.download_network()
            >>> loader.save_graph(G, "data/processed/my_graph.graphml")
        """
        if filepath is None:
            filepath = str(PROCESSED_GRAPH_PATH)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        logger.info(f"Saving graph to: {filepath}")

        try:
            ox.save_graphml(G, filepath=filepath)
            logger.info(
                f"Graph saved successfully. File size: "
                f"{os.path.getsize(filepath) / (1024 * 1024):.2f} MB"
            )
        except Exception as e:
            logger.error(f"Failed to save graph: {str(e)}")
            raise

    def load_from_cache(
        self, filepath: Optional[str] = None
    ) -> Optional[nx.MultiDiGraph]:
        """
        Load previously saved graph from disk.

        Args:
            filepath: Path to GraphML file (default: config.PROCESSED_GRAPH_PATH)

        Returns:
            NetworkX graph if file exists, None otherwise

        Example:
            >>> loader = GraphLoader()
            >>> G = loader.load_from_cache()
            >>> if G is not None:
            ...     print(f"Loaded cached graph with {G.number_of_nodes()} nodes")
        """
        if filepath is None:
            filepath = str(PROCESSED_GRAPH_PATH)

        if not os.path.exists(filepath):
            logger.info(f"No cached graph found at: {filepath}")
            return None

        logger.info(f"Loading cached graph from: {filepath}")

        try:
            G = ox.load_graphml(filepath)
            logger.info(
                f"Successfully loaded graph: {G.number_of_nodes()} nodes, "
                f"{G.number_of_edges()} edges"
            )
            return G
        except Exception as e:
            logger.error(f"Failed to load cached graph: {str(e)}")
            logger.info("Will download fresh graph instead.")
            return None

    def get_or_create_graph(self) -> nx.MultiDiGraph:
        """
        Get graph from cache or download if not available.

        This is the main method to use for getting a graph. It automatically
        handles caching and downloading as needed.

        Returns:
            NetworkX MultiDiGraph with road network

        Example:
            >>> loader = GraphLoader("Kadıköy, Istanbul, Turkey")
            >>> G = loader.get_or_create_graph()  # Loads from cache or downloads
            >>> print(f"Graph ready: {G.number_of_nodes()} nodes")
            Graph ready: 12453 nodes
        """
        # Try to load from cache first
        G = self.load_from_cache()

        if G is not None:
            self.graph = G
            return G

        # Download if not cached
        logger.info("Cached graph not found. Downloading from OSM...")
        G = self.download_network()

        # Save for future use
        if SAVE_PROCESSED_GRAPH:
            self.save_graph(G)

        self.graph = G
        return G

    def reload(self, force_download: bool = False) -> nx.MultiDiGraph:
        """
        Reload the graph, optionally forcing a fresh download.

        Args:
            force_download: If True, download fresh data even if cache exists

        Returns:
            NetworkX MultiDiGraph with road network

        Example:
            >>> loader = GraphLoader()
            >>> G = loader.reload(force_download=True)  # Force fresh download
        """
        if force_download:
            logger.info("Forcing fresh download from OSM...")
            G = self.download_network()
            if SAVE_PROCESSED_GRAPH:
                self.save_graph(G)
        else:
            G = self.get_or_create_graph()

        self.graph = G
        return G

    def get_graph_info(self) -> dict:
        """
        Get basic information about the loaded graph.

        Returns:
            Dictionary with graph statistics

        Raises:
            ValueError: If no graph is loaded

        Example:
            >>> loader = GraphLoader()
            >>> G = loader.get_or_create_graph()
            >>> info = loader.get_graph_info()
            >>> print(f"Network type: {info['network_type']}")
            Network type: drive
        """
        if self.graph is None:
            raise ValueError("No graph loaded. Call get_or_create_graph() first.")

        return {
            'location': self.location,
            'network_type': self.network_type,
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'is_directed': self.graph.is_directed(),
            'is_multigraph': self.graph.is_multigraph(),
            'num_connected_components': nx.number_weakly_connected_components(
                self.graph
            ),
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def load_graph(
    location: str = DEFAULT_LOCATION,
    network_type: str = NETWORK_TYPE,
    force_download: bool = False,
) -> nx.MultiDiGraph:
    """
    Convenience function to load a graph quickly.

    Args:
        location: Geographic location to load
        network_type: Type of network ('drive', 'walk', 'bike', 'all')
        force_download: Force fresh download even if cache exists

    Returns:
        NetworkX MultiDiGraph with road network

    Example:
        >>> G = load_graph("Kadıköy, Istanbul, Turkey")
        >>> print(f"Loaded {G.number_of_nodes()} nodes")
        Loaded 12453 nodes
    """
    loader = GraphLoader(location=location, network_type=network_type)

    if force_download:
        return loader.reload(force_download=True)
    else:
        return loader.get_or_create_graph()
