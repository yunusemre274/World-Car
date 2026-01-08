import networkx as nx
import osmnx as ox
from src.algorithms.astar import AStarAlgorithm
from src.algorithms.dijkstra import DijkstraAlgorithm


def test_weight_validation():
    """Test that weight < 1.0 raises ValueError"""
    print("\n--- Test: Weight Validation ---")

    try:
        AStarAlgorithm(heuristic_weight=0.5)
        assert False, "Should have raised ValueError for weight < 1.0"
    except ValueError as e:
        print(f"✓ Correctly rejected weight 0.5: {e}")

    try:
        AStarAlgorithm(heuristic_weight=0.0)
        assert False, "Should have raised ValueError for weight = 0.0"
    except ValueError as e:
        print(f"✓ Correctly rejected weight 0.0: {e}")

    # Valid weights should not raise
    AStarAlgorithm(heuristic_weight=1.0)
    AStarAlgorithm(heuristic_weight=1.5)
    AStarAlgorithm(heuristic_weight=2.0)
    print("✓ Accepted valid weights: 1.0, 1.5, 2.0")


def test_edge_selection_fix():
    """Test that minimum edge is selected from multiple edges"""
    print("\n--- Test: Edge Selection Fix ---")

    # Create simple MultiDiGraph with multiple edges
    G = nx.MultiDiGraph()
    G.add_node(1, x=0.0, y=0.0)
    G.add_node(2, x=0.01, y=0.0)
    G.add_node(3, x=0.02, y=0.0)

    # Add multiple edges between nodes 1 and 2
    G.add_edge(1, 2, length=1000)  # Longer edge
    G.add_edge(1, 2, length=500)   # Shorter edge (should be selected)
    G.add_edge(2, 3, length=800)

    astar = AStarAlgorithm(heuristic_weight=1.0)
    path, dist, visited, time_ms = astar.run(G, 1, 3)

    # Should select minimum edges: 1->2 (500) + 2->3 (800) = 1300
    assert dist == 1300, f"Expected 1300, got {dist} - minimum edge not selected"
    assert path == [1, 2, 3], f"Expected [1, 2, 3], got {path}"
    print(f"✓ Correctly selected minimum edges: distance = {dist}")


def test_weighted_astar_finds_path():
    """Verify weighted A* finds a valid path"""
    print("\n--- Test: Weighted A* Finds Path ---")

    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[10]

    astar = AStarAlgorithm(heuristic_weight=1.5)
    path, dist, visited, time_ms = astar.run(G, source, target)

    # Verify path exists and is valid
    assert len(path) > 0, "Path should not be empty"
    assert path[0] == source, "Path should start at source"
    assert path[-1] == target, "Path should end at target"
    assert dist > 0, "Distance should be positive"
    assert visited > 0, "Should visit at least one node"
    assert time_ms >= 0, "Time should be non-negative"

    print(f"✓ Found valid path: {len(path)} nodes, {dist:.1f}m, visited {visited} nodes in {time_ms:.2f}ms")


def test_weighted_astar_reduces_nodes():
    """Verify weighted A* visits fewer nodes than Dijkstra"""
    print("\n--- Test: Weighted A* Reduces Node Exploration ---")

    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[20]

    dijkstra = DijkstraAlgorithm()
    astar_standard = AStarAlgorithm(heuristic_weight=1.0)
    astar_weighted = AStarAlgorithm(heuristic_weight=1.5)

    _, _, d_visited, _ = dijkstra.run(G, source, target)
    _, _, a_visited, _ = astar_standard.run(G, source, target)
    _, _, w_visited, _ = astar_weighted.run(G, source, target)

    print(f"  Dijkstra: {d_visited} nodes")
    print(f"  A* (w=1.0): {a_visited} nodes")
    print(f"  A* (w=1.5): {w_visited} nodes")

    # Weighted A* should visit fewer nodes than standard A*
    # Standard A* should visit fewer nodes than Dijkstra
    assert w_visited <= a_visited, f"Weighted A* ({w_visited}) should visit fewer or equal nodes than standard A* ({a_visited})"
    assert a_visited <= d_visited, f"Standard A* ({a_visited}) should visit fewer or equal nodes than Dijkstra ({d_visited})"

    reduction = ((d_visited - w_visited) / d_visited) * 100
    print(f"✓ Weighted A* achieved {reduction:.1f}% node reduction vs Dijkstra")


def test_weighted_astar_path_quality():
    """Verify path is reasonably close to optimal"""
    print("\n--- Test: Weighted A* Path Quality ---")

    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[15]

    dijkstra = DijkstraAlgorithm()
    astar_weighted = AStarAlgorithm(heuristic_weight=1.5)

    _, d_dist, _, _ = dijkstra.run(G, source, target)
    _, w_dist, _, _ = astar_weighted.run(G, source, target)

    # For weight=1.5, path should be within 10% of optimal
    quality_ratio = w_dist / d_dist
    print(f"  Dijkstra (optimal): {d_dist:.1f}m")
    print(f"  Weighted A*: {w_dist:.1f}m")
    print(f"  Quality: {quality_ratio:.2%} of optimal")

    assert quality_ratio <= 1.10, f"Weighted A* path should be within 10% of optimal, got {quality_ratio:.2%}"
    print(f"✓ Path quality acceptable: {quality_ratio:.2%} of optimal")


def test_heuristic_weight_effect():
    """Verify increasing weight reduces exploration"""
    print("\n--- Test: Heuristic Weight Effect ---")

    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[25]

    astar_10 = AStarAlgorithm(heuristic_weight=1.0)
    astar_15 = AStarAlgorithm(heuristic_weight=1.5)
    astar_20 = AStarAlgorithm(heuristic_weight=2.0)

    _, _, v_10, _ = astar_10.run(G, source, target)
    _, _, v_15, _ = astar_15.run(G, source, target)
    _, _, v_20, _ = astar_20.run(G, source, target)

    print(f"  Weight 1.0: {v_10} nodes")
    print(f"  Weight 1.5: {v_15} nodes")
    print(f"  Weight 2.0: {v_20} nodes")

    # Higher weight should generally visit fewer nodes
    assert v_15 <= v_10, f"Weight 1.5 ({v_15}) should visit fewer or equal nodes than 1.0 ({v_10})"
    assert v_20 <= v_15, f"Weight 2.0 ({v_20}) should visit fewer or equal nodes than 1.5 ({v_15})"
    print("✓ Higher weights successfully reduced node exploration")


def test_same_source_target():
    """Test edge case where source equals target"""
    print("\n--- Test: Same Source and Target ---")

    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    node = list(G.nodes)[0]
    astar = AStarAlgorithm(heuristic_weight=1.5)
    path, dist, visited, time_ms = astar.run(G, node, node)

    assert path == [node], "Path should contain only the node itself"
    assert dist == 0.0, "Distance should be zero"
    assert visited == 1, "Should visit only one node"
    print("✓ Correctly handled same source/target case")


def test_backward_compatibility():
    """Test that default weight=1.0 maintains standard A* behavior"""
    print("\n--- Test: Backward Compatibility ---")

    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[10]

    # Default (no parameter) should be same as explicit weight=1.0
    astar_default = AStarAlgorithm()
    astar_explicit = AStarAlgorithm(heuristic_weight=1.0)

    path1, dist1, visited1, _ = astar_default.run(G, source, target)
    path2, dist2, visited2, _ = astar_explicit.run(G, source, target)

    assert path1 == path2, "Default and explicit weight=1.0 should give same path"
    assert dist1 == dist2, "Default and explicit weight=1.0 should give same distance"
    assert visited1 == visited2, "Default and explicit weight=1.0 should visit same nodes"
    print("✓ Default behavior matches weight=1.0 (backward compatible)")


def test_multiple_edges_per_node_pair():
    """Test that algorithm correctly handles MultiDiGraph with multiple edges"""
    print("\n--- Test: Multiple Edges Per Node Pair ---")

    G = nx.MultiDiGraph()

    # Create a simple network
    G.add_node(1, x=0.0, y=0.0)
    G.add_node(2, x=0.01, y=0.0)
    G.add_node(3, x=0.02, y=0.0)
    G.add_node(4, x=0.03, y=0.0)

    # Add multiple parallel edges with different lengths
    G.add_edge(1, 2, length=100)
    G.add_edge(1, 2, length=200)  # Alternative route
    G.add_edge(2, 3, length=150)
    G.add_edge(2, 3, length=100)  # Shorter alternative
    G.add_edge(2, 3, length=300)  # Longer alternative
    G.add_edge(3, 4, length=100)

    astar = AStarAlgorithm(heuristic_weight=1.0)
    path, dist, visited, _ = astar.run(G, 1, 4)

    # Should select minimum edges: 1->2 (100) + 2->3 (100) + 3->4 (100) = 300
    assert dist == 300, f"Expected distance 300, got {dist}"
    assert path == [1, 2, 3, 4], f"Expected path [1, 2, 3, 4], got {path}"
    print(f"✓ Correctly handled multiple edges: selected minimum path distance = {dist}")


def run_all_tests():
    """Run all test functions"""
    print("\n" + "="*60)
    print("WEIGHTED A* COMPREHENSIVE TEST SUITE")
    print("="*60)

    tests = [
        test_weight_validation,
        test_edge_selection_fix,
        test_weighted_astar_finds_path,
        test_weighted_astar_reduces_nodes,
        test_weighted_astar_path_quality,
        test_heuristic_weight_effect,
        test_same_source_target,
        test_backward_compatibility,
        test_multiple_edges_per_node_pair
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("✓ ALL TESTS PASSED!")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
