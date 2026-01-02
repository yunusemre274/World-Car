import osmnx as ox
import random

from src.algorithms.dijkstra import DijkstraAlgorithm

print("Testing Dijkstra's Algorithm on a real-world graph...")
def test_dijkstra_basic():
    
    place = "Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    # Ensure nodes are connected
    nodes = list(G.nodes)
    source = random.choice(nodes)
    target = random.choice(nodes)

    algo = DijkstraAlgorithm()
    path, distance, visited, time_ms = algo.run(G, source, target)

    if not path:
        print("No path found between selected nodes.")
        return

    print("Path:", path[:5], "...", path[-5:])
    print("Distance (m):", distance)
    print("Visited nodes:", visited)
    print("Time (ms):", time_ms)

    assert path[0] == source
    assert path[-1] == target
    assert distance >= 0
    assert visited > 0
    assert time_ms > 0


if __name__ == "__main__":
    test_dijkstra_basic()
