"""
Map Renderer for WorldCar

Renders OpenStreetMap road networks in pygame with coordinate conversion
and performance optimization.
"""

import pygame
from typing import Dict, List, Tuple


class MapRenderer:
    """
    Renders OSM road network in pygame.

    Responsibilities:
    - Load graph data (nodes, edges)
    - Convert geo-coordinates (lat/lon) → screen pixels
    - Draw road network efficiently
    - Cache rendering for performance

    Coordinate System:
    Geographic (lat/lon) → Screen (pixels)
    """

    def __init__(self, graph, screen_width: int = 1280, screen_height: int = 720):
        """
        Initialize map renderer.

        Args:
            graph: NetworkX graph from OSMnx with node["x"], node["y"]
            screen_width: Window width in pixels
            screen_height: Window height in pixels
        """
        self.graph = graph
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Cached data
        self.nodes_xy: Dict[int, Tuple[int, int]] = {}  # node_id → (screen_x, screen_y)
        self.edges: List[Tuple[int, int, int, int]] = []  # (x1, y1, x2, y2) tuples

        # Map geographic bounds
        self.min_lon = 0
        self.max_lon = 0
        self.min_lat = 0
        self.max_lat = 0
        self.lon_range = 0
        self.lat_range = 0

        # Pre-rendered surface (performance optimization)
        self.cached_surface: pygame.Surface = None
        self.cache_enabled = True

        # Calculate map bounds
        self._calculate_bounds()

    def _calculate_bounds(self):
        """Calculate min/max lat/lon from graph for coordinate conversion."""
        if len(self.graph.nodes) == 0:
            raise ValueError("Graph has no nodes")

        lons = [self.graph.nodes[n]["x"] for n in self.graph.nodes]
        lats = [self.graph.nodes[n]["y"] for n in self.graph.nodes]

        self.min_lon = min(lons)
        self.max_lon = max(lons)
        self.min_lat = min(lats)
        self.max_lat = max(lats)

        # Calculate ranges for normalization
        self.lon_range = self.max_lon - self.min_lon
        self.lat_range = self.max_lat - self.min_lat

        if self.lon_range == 0:
            self.lon_range = 1.0  # Prevent division by zero
        if self.lat_range == 0:
            self.lat_range = 1.0

    def geo_to_screen(self, lon: float, lat: float) -> Tuple[int, int]:
        """
        Convert geographic coordinates to screen pixels.

        Args:
            lon: Longitude (degrees)
            lat: Latitude (degrees)

        Returns:
            (screen_x, screen_y) tuple in pixels
        """
        # Normalize to [0, 1]
        norm_x = (lon - self.min_lon) / self.lon_range
        norm_y = (lat - self.min_lat) / self.lat_range

        # Scale to screen with padding
        padding = 50
        screen_x = padding + norm_x * (self.screen_width - 2 * padding)
        screen_y = padding + (1 - norm_y) * (self.screen_height - 2 * padding)  # Invert Y axis

        return (int(screen_x), int(screen_y))

    def preprocess_graph(self):
        """
        Pre-calculate all node positions and edges.

        Should be called once during initialization for performance.
        Converts all geographic coordinates to screen coordinates and
        builds edge list for fast rendering.
        """
        print(f"Preprocessing graph with {len(self.graph.nodes)} nodes...")

        # Convert all nodes to screen coordinates
        for node_id in self.graph.nodes:
            lon = self.graph.nodes[node_id]["x"]
            lat = self.graph.nodes[node_id]["y"]
            self.nodes_xy[node_id] = self.geo_to_screen(lon, lat)

        # Build edge list
        edge_count = 0
        for u, v in self.graph.edges():
            if u in self.nodes_xy and v in self.nodes_xy:
                x1, y1 = self.nodes_xy[u]
                x2, y2 = self.nodes_xy[v]
                self.edges.append((x1, y1, x2, y2))
                edge_count += 1

        print(f"Preprocessed {len(self.nodes_xy)} nodes and {edge_count} edges")

        # Pre-render to surface if caching enabled
        if self.cache_enabled:
            self._pre_render_to_surface()

    def _pre_render_to_surface(self):
        """
        Pre-render entire map to a surface (1-time cost).

        This dramatically improves performance for large graphs
        by avoiding redrawing thousands of lines each frame.
        """
        print("Pre-rendering map to cached surface...")

        # Create surface
        self.cached_surface = pygame.Surface((self.screen_width, self.screen_height))
        self.cached_surface.fill((255, 255, 255))  # White background

        # Draw all roads
        for x1, y1, x2, y2 in self.edges:
            pygame.draw.line(
                self.cached_surface,
                (200, 200, 200),  # Gray roads
                (x1, y1),
                (x2, y2),
                width=2
            )

        print("Map pre-rendering complete")

    def render(self, screen: pygame.Surface, camera=None):
        """
        Draw the road network on pygame screen.

        Args:
            screen: pygame.Surface to draw on
            camera: Optional Camera instance for pan/zoom transforms
        """
        if camera is None:
            # Legacy mode: No camera transform
            if self.cache_enabled and self.cached_surface is not None:
                # Fast path: blit pre-rendered surface
                screen.blit(self.cached_surface, (0, 0))
            else:
                # Slow path: draw each edge individually
                screen.fill((255, 255, 255))  # White background

                for x1, y1, x2, y2 in self.edges:
                    pygame.draw.line(
                        screen,
                        (200, 200, 200),  # Gray
                        (x1, y1),
                        (x2, y2),
                        width=2
                    )
        else:
            # Camera mode: Apply camera transform
            self._render_with_camera(screen, camera)

    def _render_with_camera(self, screen: pygame.Surface, camera):
        """
        Render map with camera transform applied.

        Args:
            screen: pygame.Surface to draw on
            camera: Camera instance
        """
        screen.fill((255, 255, 255))  # White background

        # Get visible bounds for culling
        min_x, min_y, max_x, max_y = camera.get_visible_bounds()

        # Draw edges with camera transform
        edges_drawn = 0
        for x1, y1, x2, y2 in self.edges:
            # Simple culling: check if either endpoint is visible
            # (More sophisticated culling could check line-rect intersection)
            if not self._is_edge_visible(x1, y1, x2, y2, min_x, min_y, max_x, max_y):
                continue

            # Transform world coords through camera
            screen_x1, screen_y1 = camera.world_to_screen(x1, y1)
            screen_x2, screen_y2 = camera.world_to_screen(x2, y2)

            # Adjust line width based on zoom
            line_width = max(1, int(2 * camera.zoom))

            # Draw line
            pygame.draw.line(
                screen,
                (200, 200, 200),  # Gray
                (screen_x1, screen_y1),
                (screen_x2, screen_y2),
                width=line_width
            )
            edges_drawn += 1

    def _is_edge_visible(self, x1: float, y1: float, x2: float, y2: float,
                         min_x: float, min_y: float, max_x: float, max_y: float) -> bool:
        """
        Check if edge is within visible bounds (simple culling).

        Args:
            x1, y1: First endpoint in world coordinates
            x2, y2: Second endpoint in world coordinates
            min_x, min_y, max_x, max_y: Visible bounds in world coordinates

        Returns:
            True if edge should be drawn
        """
        # Check if either endpoint is visible
        point1_visible = min_x <= x1 <= max_x and min_y <= y1 <= max_y
        point2_visible = min_x <= x2 <= max_x and min_y <= y2 <= max_y

        # Also check if line crosses the bounds (basic check)
        # This prevents missing edges that cross through the view but have both endpoints outside
        if point1_visible or point2_visible:
            return True

        # Check if line intersects bounding box (simplified)
        # A more complete implementation would use line-rect intersection
        # For now, we'll draw any edge where the bounding box overlaps visible area
        edge_min_x = min(x1, x2)
        edge_max_x = max(x1, x2)
        edge_min_y = min(y1, y2)
        edge_max_y = max(y1, y2)

        return not (edge_max_x < min_x or edge_min_x > max_x or
                   edge_max_y < min_y or edge_min_y > max_y)

    def get_bounds(self) -> Dict[str, float]:
        """
        Get geographic bounds of the map.

        Returns:
            Dict with keys: min_lon, max_lon, min_lat, max_lat
        """
        return {
            "min_lon": self.min_lon,
            "max_lon": self.max_lon,
            "min_lat": self.min_lat,
            "max_lat": self.max_lat
        }
