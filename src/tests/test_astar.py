import osmnx as ox
from src.algorithms.astar import AStarAlgorithm


def test_astar():
    place = "Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[-1]

    algo = AStarAlgorithm()
    path, dist, visited, time_ms = algo.run(G, source, target)

    print("A* distance:", dist)
    print("Visited nodes:", visited)
    print("Time (ms):", time_ms)

    assert path[0] == source
    assert path[-1] == target
    assert dist > 0
    assert visited > 0


if __name__ == "__main__":
    test_astar()
