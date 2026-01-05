import heapq
import math
from typing import Dict, List, Tuple, Set

from src.algorithms.base import ShortestPathAlgorithm
from src.utils.performance import measure_performance


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class AStarAlgorithm(ShortestPathAlgorithm):
    @measure_performance
    def run(self, graph, source: int, target: int):
        if source == target:
            return [source], 0.0, 1

        dist: Dict[int, float] = {source: 0.0}
        prev: Dict[int, int] = {}
        visited: Set[int] = set()

        source_lat = graph.nodes[source]["y"]
        source_lon = graph.nodes[source]["x"]
        target_lat = graph.nodes[target]["y"]
        target_lon = graph.nodes[target]["x"]

        pq: List[Tuple[float, int]] = [(0.0, source)]

        while pq:
            _, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            if current == target:
                break

            current_lat = graph.nodes[current]["y"]
            current_lon = graph.nodes[current]["x"]

            for neighbor in graph.neighbors(current):
                if neighbor in visited:
                    continue

                edge_data = graph[current][neighbor][0]
                weight = edge_data.get("length", float("inf"))

                tentative_g = dist[current] + weight

                if tentative_g < dist.get(neighbor, float("inf")):
                    dist[neighbor] = tentative_g
                    prev[neighbor] = current

                    h = haversine_distance(
                        graph.nodes[neighbor]["y"],
                        graph.nodes[neighbor]["x"],
                        target_lat,
                        target_lon,
                    )

                    f = tentative_g + h
                    heapq.heappush(pq, (f, neighbor))

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
