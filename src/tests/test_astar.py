import osmnx as ox
from src.algorithms.astar import AStarAlgorithm


def test_astar_basic():
    print("Running A* Algorithm Test")
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[-1]

    algo = AStarAlgorithm()
    path, distance, visited, time_ms = algo.run(G, source, target)

    print("Path:", path[:5], "...", path[-5:])
    print("Distance (m):", distance)
    print("Visited nodes:", visited)
    print("Time (ms):", time_ms)

    assert path
    assert distance > 0
    assert visited > 0
    assert time_ms > 0


if __name__ == "__main__":
    
    test_astar_basic()
