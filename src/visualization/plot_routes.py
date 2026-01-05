import osmnx as ox
import matplotlib.pyplot as plt
import random
import networkx as nx

from src.algorithms.dijkstra import DijkstraAlgorithm
from src.algorithms.astar import AStarAlgorithm


def plot_routes():
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    # En büyük connected component (sürüm bağımsız)
    largest_cc = max(nx.weakly_connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

    nodes = list(G.nodes)
    source, target = random.sample(nodes, 2)

    dijkstra = DijkstraAlgorithm()
    astar = AStarAlgorithm()

    d_path, _, _, _ = dijkstra.run(G, source, target)
    a_path, _, _, _ = astar.run(G, source, target)

    print("Dijkstra path length:", len(d_path))
    print("A* path length:", len(a_path))

    fig, ax = ox.plot_graph(G, show=False, close=False, bgcolor="white")

    if d_path:
        ox.plot_graph_route(
    G,
    d_path,
    ax=ax,
    route_color="red",
    route_linewidth=6,
    node_size=0,
    zorder=1,
    show=False,
    close=False,
)

    if a_path:
        ox.plot_graph_route(
    G,
    a_path,
    ax=ax,
    route_color="green",
    route_linewidth=3,
    node_size=0,
    zorder=2,
    show=False,
    close=False,
)

    plt.title("Dijkstra (Red) vs A* (Green)")
    plt.show()


if __name__ == "__main__":
    plot_routes()
