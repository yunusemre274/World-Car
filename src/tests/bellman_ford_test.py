import osmnx as ox
from src.algorithms.bellman_ford import BellmanFordAlgorithm


def test_bellman_ford_basic():
    print("Testing Bellman-Ford Algorithm")
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[-1]

    algo = BellmanFordAlgorithm()
    path, distance, visited, time_ms = algo.run(G, source, target)

    print("Path length:", len(path))
    print("Distance:", distance)
    print("Visited rounds:", visited)
    print("Time (ms):", time_ms)

    assert path[0] == source
    assert path[-1] == target
    assert distance > 0
    assert visited > 0


if __name__ == "__main__":
    test_bellman_ford_basic()
