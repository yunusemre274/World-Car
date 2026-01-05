import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import heapq
import random


def animate_dijkstra():
    print("Animating Dijkstra's Algorithm...")
    place = "Moda, Kadıköy, Istanbul, Turkey"
    G = ox.graph_from_place(place, network_type="drive")

    # Largest connected component
    largest_cc = max(nx.weakly_connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

    nodes = list(G.nodes)
    source, target = random.sample(nodes, 2)

    pos = {n: (G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes}

    visited = set()
    distances = {node: float("inf") for node in G.nodes}
    distances[source] = 0

    pq = [(0, source)]

    fig, ax = plt.subplots(figsize=(8, 8))
    ox.plot_graph(G, ax=ax, show=False, close=False, node_size=0, edge_color="#dddddd")

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue

        visited.add(current)

        # Draw visited node
        ax.scatter(
            pos[current][0],
            pos[current][1],
            c="red",
            s=10,
            zorder=3,
        )

        plt.pause(0.01)

        if current == target:
            break

        for neighbor in G.successors(current):
            edge_data = G[current][neighbor][0]
            weight = edge_data.get("length", 1)

            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))

    # Highlight source & target
    ax.scatter(*pos[source], c="blue", s=50, label="Source")
    ax.scatter(*pos[target], c="green", s=50, label="Target")
    ax.legend()

    plt.title("Dijkstra Step-by-Step Exploration")
    plt.show()


if __name__ == "__main__":
    animate_dijkstra()
