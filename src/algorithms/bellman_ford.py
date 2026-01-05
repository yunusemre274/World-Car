import time


class BellmanFordAlgorithm:
    def run(self, graph, source, target):
        start_time = time.perf_counter()

        distance = {node: float("inf") for node in graph.nodes}
        previous = {node: None for node in graph.nodes}

        distance[source] = 0
        visited_nodes = 0

        nodes = list(graph.nodes)

        for _ in range(len(nodes) - 1):
            updated = False
            for u, v, data in graph.edges(data=True):
                weight = data.get("length", float("inf"))
                if distance[u] + weight < distance[v]:
                    distance[v] = distance[u] + weight
                    previous[v] = u
                    updated = True
            visited_nodes += 1
            if not updated:
                break

        for u, v, data in graph.edges(data=True):
            weight = data.get("length", float("inf"))
            if distance[u] + weight < distance[v]:
                raise ValueError("Graph contains a negative weight cycle")

        if distance[target] == float("inf"):
            return [], float("inf"), visited_nodes, 0

        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        execution_time = (time.perf_counter() - start_time) * 1000

        return path, distance[target], visited_nodes, execution_time
