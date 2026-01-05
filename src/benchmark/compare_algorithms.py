import osmnx as ox

from src.algorithms.dijkstra import DijkstraAlgorithm
from src.algorithms.astar import AStarAlgorithm


def compare():
    print("Loading graph...")
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    nodes = list(G.nodes)
    source = nodes[0]
    target = nodes[-1]

    dijkstra = DijkstraAlgorithm()
    astar = AStarAlgorithm()

    d_path, d_dist, d_visited, d_time = dijkstra.run(G, source, target)
    a_path, a_dist, a_visited, a_time = astar.run(G, source, target)

    results = {
        "source": source,
        "target": target,
        "results": {
            "dijkstra": {
                "distance": d_dist,
                "visited_nodes": d_visited,
                "execution_time_ms": d_time,
            },
            "astar": {
                "distance": a_dist,
                "visited_nodes": a_visited,
                "execution_time_ms": a_time,
            },
        },
    }

    print(results)


if __name__ == "__main__":
    compare()
