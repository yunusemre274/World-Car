import heapq
from typing import List, Tuple, Dict, Set

from src.algorithms.base import ShortestPathAlgorithm
from src.utils.performance import measure_performance


class DijkstraAlgorithm(ShortestPathAlgorithm):
    @measure_performance
    def run(self, graph, source: int, target: int):
        # Edge case: source == target
        if source == target:
            return [source], 0.0, 1

        # Distance from source to each node
        dist: Dict[int, float] = {source: 0.0}

        # Previous node for path reconstruction
        prev: Dict[int, int] = {}

        # Visited nodes
        visited: Set[int] = set()

        # Priority queue: (distance, node)
        pq: List[Tuple[float, int]] = [(0.0, source)]

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue

            visited.add(current_node)

            # Stop early if target is reached
            if current_node == target:
                break

            # Explore neighbors
            for neighbor in graph.neighbors(current_node):
                if neighbor in visited:
                    continue

                # MultiDiGraph: take first edge
                edge_data = graph[current_node][neighbor][0]
                weight = edge_data.get("length", float("inf"))

                new_dist = current_dist + weight

                if new_dist < dist.get(neighbor, float("inf")):
                    dist[neighbor] = new_dist
                    prev[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))

        # No path found
        if target not in dist:
            return [], float("inf"), len(visited)

        # Path reconstruction
        path = []
        node = target
        while node != source:
            path.append(node)
            node = prev[node]
        path.append(source)
        path.reverse()

        return path, dist[target], len(visited)
