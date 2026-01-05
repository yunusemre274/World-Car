import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import heapq
import random
import math


def heuristic(a, b, pos):
    return math.dist(pos[a], pos[b])


def animate_astar():
    print("Animating A* Algorithm...")
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    largest_cc = max(nx.weakly_connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

    nodes = list(G.nodes)
    source, target = random.sample(nodes, 2)

    pos = {n: (G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes}

    open_set = []
    heapq.heappush(open_set, (0, source))

    g_score = {node: float("inf") for node in G.nodes}
    g_score[source] = 0

    visited = set()

    fig, ax = plt.subplots(figsize=(8, 8))
    ox.plot_graph(G, ax=ax, show=False, close=False, node_size=0, edge_color="#dddddd")

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in visited:
            continue
        visited.add(current)

        ax.scatter(
            pos[current][0],
            pos[current][1],
            c="purple",
            s=10,
            zorder=3,
        )

        plt.pause(0.01)

        if current == target:
            break

        for neighbor in G.successors(current):
            edge_data = G[current][neighbor][0]
            weight = edge_data.get("length", 1)

            tentative_g = g_score[current] + weight

            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, target, pos)
                heapq.heappush(open_set, (f_score, neighbor))

    ax.scatter(*pos[source], c="blue", s=60, label="Source")
    ax.scatter(*pos[target], c="green", s=60, label="Target")
    ax.legend()

    plt.title("A* Step-by-Step Exploration")
    plt.show()


if __name__ == "__main__":
    animate_astar()
