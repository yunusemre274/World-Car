import heapq
import time
from math import radians, sin, cos, sqrt, atan2


class AStarAlgorithm:
    def __init__(self):
        pass

    # --------------------------------------------------
    # Heuristic: Haversine distance (meters)
    # --------------------------------------------------
    def heuristic(self, a, b, pos):
        lon1, lat1 = pos[a]
        lon2, lat2 = pos[b]

        R = 6371000  # Earth radius in meters

        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlambda = radians(lon2 - lon1)

        h = (
            sin(dphi / 2) ** 2
            + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
        )

        return 2 * R * atan2(sqrt(h), sqrt(1 - h))

    # --------------------------------------------------
    # A* algorithm
    # --------------------------------------------------
    def run(self, G, source, target):
        start_time = time.perf_counter()

        # Edge case: same node
        if source == target:
            return [source], 0.0, 1, 0.0

        # Node positions (lon, lat)
        pos = {
            node: (G.nodes[node]["x"], G.nodes[node]["y"])
            for node in G.nodes
        }

        # Priority queue: (f_score, node)
        open_set = []
        heapq.heappush(open_set, (0, source))

        # Cost from source
        g_score = {node: float("inf") for node in G.nodes}
        g_score[source] = 0.0

        # Path reconstruction
        previous = {}

        visited = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current in visited:
                continue

            visited.add(current)

            # Goal reached
            if current == target:
                break

            for neighbor in G.neighbors(current):
                edge_data = G[current][neighbor][0]
                weight = edge_data.get("length", 1.0)

                tentative_g = g_score[current] + weight

                if tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    previous[neighbor] = current

                    f_score = tentative_g + self.heuristic(
                        neighbor, target, pos
                    )

                    heapq.heappush(open_set, (f_score, neighbor))

        # No path found
        if target not in previous and source != target:
            end_time = time.perf_counter()
            return [], float("inf"), len(visited), (end_time - start_time) * 1000

        # Path reconstruction
        path = [target]
        while path[-1] != source:
            path.append(previous[path[-1]])
        path.reverse()

        end_time = time.perf_counter()

        return (
            path,
            g_score[target],
            len(visited),
            (end_time - start_time) * 1000,
        )
