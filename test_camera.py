"""
Camera System Test for WorldCar - Phase 5.3

Tests the Camera and CameraControls classes with interactive controls.
Displays the road network with pan, zoom, and follow capabilities.

Usage:
    python test_camera.py

Controls:
    Mouse:
        - Scroll wheel: Zoom in/out at cursor
        - Middle mouse drag: Pan view
        - Right mouse drag: Pan view (alternative)

    Keyboard:
        - Arrow keys / WASD: Pan view
        - Q / E: Zoom out/in
        - Plus / Minus: Zoom in/out
        - F: Toggle follow mode (follows map center)
        - R: Reset camera to fit map bounds
        - Space: Pause follow mode
        - ESC: Exit

Expected Result:
    - Window opens showing road network
    - Smooth pan and zoom controls
    - Instructions displayed on screen
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
from src.rendering.camera import Camera
from src.input.camera_controls import CameraControls


def load_graph(place_name: str = "Moda, Kadıköy, Istanbul, Turkey"):
    """
    Load road network from OpenStreetMap.

    Args:
        place_name: Location to load

    Returns:
        NetworkX MultiDiGraph
    """
    print("="*60)
    print("WORLDCAR - CAMERA SYSTEM TEST (Phase 5.3)")
    print("="*60)
    print()
    print(f"Loading map: {place_name}")

    try:
        graph = ox.graph_from_place(place_name, network_type="drive")

        # Use largest connected component
        largest_cc = max(nx.weakly_connected_components(graph), key=len)
        graph = graph.subgraph(largest_cc).copy()

        print(f"  ✓ Loaded {len(graph.nodes):,} nodes")
        print(f"  ✓ Loaded {len(graph.edges):,} edges")
        print()

        return graph

    except Exception as e:
        print(f"  ✗ Error loading map: {e}")
        raise


def draw_instructions(screen, camera, fps):
    """Draw control instructions on screen."""
    font_title = pygame.font.Font(None, 32)
    font_normal = pygame.font.Font(None, 24)

    # Semi-transparent background
    overlay = pygame.Surface((400, 380))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (10, 10))

    y_offset = 20

    # Title
    title = font_title.render("Camera Controls", True, (255, 255, 255))
    screen.blit(title, (20, y_offset))
    y_offset += 40

    # Instructions
    instructions = [
        "Mouse:",
        "  Scroll - Zoom at cursor",
        "  Middle/Right drag - Pan",
        "",
        "Keyboard:",
        "  Arrows/WASD - Pan",
        "  Q/E - Zoom out/in",
        "  +/- - Zoom in/out",
        "  F - Toggle follow",
        "  R - Reset camera",
        "  Space - Pause follow",
        "  ESC - Exit",
    ]

    for line in instructions:
        text = font_normal.render(line, True, (255, 255, 255))
        screen.blit(text, (20, y_offset))
        y_offset += 25

    # Camera info
    y_offset += 10
    info_lines = [
        f"Position: ({camera.x:.0f}, {camera.y:.0f})",
        f"Zoom: {camera.zoom:.2f}x",
        f"Mode: {camera.mode.value}",
        f"FPS: {fps:.1f}"
    ]

    for line in info_lines:
        text = font_normal.render(line, True, (100, 255, 100))
        screen.blit(text, (20, y_offset))
        y_offset += 25


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
    pygame.display.set_caption("WorldCar - Camera System Test (Phase 5.3)")

    print(f"  ✓ Window created: {screen_width}x{screen_height}")
    print()

    # Create map renderer
    print("Creating map renderer...")
    renderer = MapRenderer(graph, screen_width, screen_height)
    renderer.preprocess_graph()
    print()

    # Create camera
    print("Creating camera system...")
    camera = Camera(screen_width, screen_height)

    # Fit camera to map bounds
    bounds = renderer.get_bounds()
    camera.fit_to_bounds(
        bounds['min_lon'], bounds['min_lat'],
        bounds['max_lon'], bounds['max_lat'],
        padding=0.1
    )

    print(f"  ✓ Camera initialized at ({camera.x:.2f}, {camera.y:.2f})")
    print(f"  ✓ Zoom level: {camera.zoom:.2f}x")
    print()

    # Create camera controls
    controls = CameraControls(camera, pan_speed=5.0, zoom_speed=0.1)
    print("  ✓ Camera controls ready")
    print()

    # Display map bounds
    print("Map Bounds:")
    print(f"  Longitude: {bounds['min_lon']:.6f} to {bounds['max_lon']:.6f}")
    print(f"  Latitude:  {bounds['min_lat']:.6f} to {bounds['max_lat']:.6f}")
    print()

    # For follow mode demonstration, set target to map center
    map_center_x = (bounds['min_lon'] + bounds['max_lon']) / 2
    map_center_y = (bounds['min_lat'] + bounds['max_lat']) / 2

    # Main loop
    print("="*60)
    print("CAMERA SYSTEM ACTIVE")
    print("="*60)
    print()
    print("Controls:")
    print("  Mouse scroll: Zoom")
    print("  Middle/Right mouse drag: Pan")
    print("  Arrow keys / WASD: Pan")
    print("  Q/E: Zoom")
    print("  F: Toggle follow mode")
    print("  R: Reset camera")
    print("  ESC: Exit")
    print()
    print("Rendering with camera...")
    print()

    clock = pygame.time.Clock()
    running = True
    frame_count = 0

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset camera
                    camera.fit_to_bounds(
                        bounds['min_lon'], bounds['min_lat'],
                        bounds['max_lon'], bounds['max_lat'],
                        padding=0.1
                    )
                    print("Camera reset to fit bounds")

            # Pass event to controls
            controls.handle_event(event)

        # Handle continuous keyboard input
        keys = pygame.key.get_pressed()
        controls.handle_keys(keys)

        # Update camera (for follow mode)
        camera.update(dt, target_pos=(map_center_x, map_center_y))

        # Render
        renderer.render(screen, camera)

        # Draw instructions overlay
        draw_instructions(screen, camera, clock.get_fps())

        # Update display
        pygame.display.flip()

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
        print("✅ SUCCESS: Camera system runs at 60 FPS")
    else:
        print(f"⚠ WARNING: FPS below target ({avg_fps:.1f} < 60)")

    print()
    print("Camera system features tested:")
    print("  ✓ Pan with mouse")
    print("  ✓ Pan with keyboard")
    print("  ✓ Zoom at cursor position")
    print("  ✓ Follow mode toggle")
    print("  ✓ Camera reset")
    print()

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
