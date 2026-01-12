"""
Map Rendering Test for WorldCar - Phase 5.2

Tests the MapRenderer class with a real OSM graph.
Displays the road network in a pygame window.

Usage:
    python test_map_render.py

Controls:
    ESC: Exit
    Close window: Exit

Expected Result:
    - Window opens showing road network
    - Map fits screen automatically
    - All roads visible (gray lines)
    - 60 FPS stable
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import osmnx as ox
import networkx as nx
from src.rendering.map_renderer import MapRenderer


def load_graph(place_name: str = "Moda, Kadıköy, Istanbul, Turkey"):
    """
    Load road network from OpenStreetMap.

    Args:
        place_name: Location to load

    Returns:
        NetworkX MultiDiGraph
    """
    print("="*60)
    print("WORLDCAR - MAP RENDERING TEST")
    print("="*60)
    print()
    print(f"Loading map: {place_name}")

    try:
        graph = ox.graph_from_place(place_name, network_type="drive")

        # Use largest connected component for reliability
        largest_cc = max(nx.weakly_connected_components(graph), key=len)
        graph = graph.subgraph(largest_cc).copy()

        print(f"  ✓ Loaded {len(graph.nodes):,} nodes")
        print(f"  ✓ Loaded {len(graph.edges):,} edges")
        print()

        return graph

    except Exception as e:
        print(f"  ✗ Error loading map: {e}")
        raise


def main():
    """Main test function."""
    # Load graph
    graph = load_graph()

    # Initialize pygame
    print("Initializing pygame...")
    pygame.init()

    # Create window
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("WorldCar - Map Rendering Test (Phase 5.2)")

    print(f"  ✓ Window created: {screen_width}x{screen_height}")
    print()

    # Create map renderer
    print("Creating map renderer...")
    renderer = MapRenderer(graph, screen_width, screen_height)

    # Preprocess graph (coordinate conversion)
    renderer.preprocess_graph()
    print()

    # Display map bounds
    bounds = renderer.get_bounds()
    print("Map Bounds:")
    print(f"  Longitude: {bounds['min_lon']:.6f} to {bounds['max_lon']:.6f}")
    print(f"  Latitude:  {bounds['min_lat']:.6f} to {bounds['max_lat']:.6f}")
    print()

    # Main loop
    print("="*60)
    print("RENDERING ACTIVE")
    print("="*60)
    print()
    print("Controls:")
    print("  ESC: Exit")
    print("  Close window: Exit")
    print()
    print("Rendering map...")
    print()

    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    fps_update_interval = 30  # Update FPS display every 30 frames

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Render
        renderer.render(screen)

        # Display FPS overlay
        if frame_count % fps_update_interval == 0:
            current_fps = clock.get_fps()
            # Draw FPS text
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f"FPS: {current_fps:.1f}", True, (0, 0, 0))
            fps_bg = pygame.Surface((150, 40))
            fps_bg.fill((255, 255, 200))  # Light yellow
            fps_bg.set_alpha(200)
            screen.blit(fps_bg, (screen_width - 160, 10))
            screen.blit(fps_text, (screen_width - 150, 15))

        # Update display
        pygame.display.flip()

        # Maintain 60 FPS
        clock.tick(60)
        frame_count += 1

    # Cleanup
    pygame.quit()

    print()
    print("="*60)
    print("TEST COMPLETE")
    print("="*60)
    print()
    print(f"Total frames rendered: {frame_count}")
    print(f"Average FPS: {clock.get_fps():.1f}")
    print()

    # Verify success criteria
    avg_fps = clock.get_fps()
    if avg_fps >= 55:
        print("✅ SUCCESS: Map renders at 60 FPS")
    else:
        print(f"⚠ WARNING: FPS below target ({avg_fps:.1f} < 60)")

    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
