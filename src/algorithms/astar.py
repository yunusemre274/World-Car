import heapq
import time
from math import radians, sin, cos, sqrt, atan2
from typing import Generator, Dict, Set, List, Tuple, Any


class AStarAlgorithm:
    def __init__(self, heuristic_weight=1.0):
        """
        Initialize A* algorithm.

        Args:
            heuristic_weight: Weight for the heuristic (epsilon in Weighted A*).
                             1.0 = standard A* (optimal)
                             >1.0 = weighted A* (faster, near-optimal)
                             Recommended: 1.5 for balanced, 2.0 for aggressive
        """
        if heuristic_weight < 1.0:
            raise ValueError("Heuristic weight must be >= 1.0")
        self.heuristic_weight = heuristic_weight

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
                # MultiDiGraph can have multiple edges - select minimum
                edges = G[current][neighbor]
                if len(edges) == 1:
                    weight = edges[0].get("length", 1.0)
                else:
                    weight = min(edge.get("length", float("inf")) for edge in edges.values())

                tentative_g = g_score[current] + weight

                if tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    previous[neighbor] = current

                    # Weighted A*: f(n) = g(n) + ε × h(n)
                    f_score = tentative_g + (self.heuristic_weight * self.heuristic(
                        neighbor, target, pos
                    ))

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

    # --------------------------------------------------
    # STEP-BY-STEP A* FOR VISUALIZATION
    # --------------------------------------------------
    def run_animated(self, G, source, target) -> Generator[Dict[str, Any], None, Tuple[List[int], float, int, float]]:
        """
        A* algorithm with step-by-step execution for visualization.

        This is a GENERATOR that yields after each node exploration,
        allowing the visualization to update incrementally.

        Each yield provides:
        {
            'type': 'explore' | 'found' | 'complete',
            'current_node': int,           # Node being explored
            'visited': Set[int],           # All visited nodes
            'open_set_nodes': List[int],   # Nodes in frontier (open set)
            'g_scores': Dict[int, float],  # Cost from source to each node
            'f_scores': Dict[int, float],  # f(n) = g(n) + h(n) for open nodes
            'path_so_far': List[int],      # Current path to current_node
            'target': int                  # Target node
        }

        Final return:
            (path, distance, visited_count, time_ms) - same as run()

        Usage:
            >>> algo = AStarAlgorithm(heuristic_weight=1.5)
            >>> generator = algo.run_animated(graph, source, target)
            >>> for step_data in generator:
            >>>     # Render step_data on visualization
            >>>     time.sleep(0.01)  # Add delay for animation
            >>> # Generator returns final result
            >>> path, distance, visited_count, time_ms = generator.value

        Args:
            G: NetworkX graph
            source: Source node ID
            target: Target node ID

        Yields:
            Dict containing current algorithm state for visualization

        Returns:
            Final result tuple (path, distance, visited_count, time_ms)
        """
        start_time = time.perf_counter()

        # Edge case: same node
        if source == target:
            yield {
                'type': 'complete',
                'current_node': source,
                'visited': {source},
                'open_set_nodes': [],
                'g_scores': {source: 0.0},
                'f_scores': {},
                'path_so_far': [source],
                'target': target
            }
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

        # Track f_scores for open set (for visualization)
        f_score_map = {source: 0.0}

        # Main algorithm loop with yields
        while open_set:
            current_f, current = heapq.heappop(open_set)

            if current in visited:
                continue

            visited.add(current)

            # Reconstruct path to current node for visualization
            path_to_current = [current]
            temp = current
            while temp in previous:
                temp = previous[temp]
                path_to_current.append(temp)
            path_to_current.reverse()

            # Get current open set nodes for visualization
            open_set_nodes = [node for _, node in open_set if node not in visited]

            # ⭐ YIELD STEP: Show node being explored
            yield {
                'type': 'explore',
                'current_node': current,
                'visited': visited.copy(),
                'open_set_nodes': open_set_nodes,
                'g_scores': dict(g_score),
                'f_scores': dict(f_score_map),
                'path_so_far': path_to_current,
                'target': target
            }

            # Goal reached
            if current == target:
                # ⭐ YIELD STEP: Target found!
                yield {
                    'type': 'found',
                    'current_node': current,
                    'visited': visited.copy(),
                    'open_set_nodes': [],
                    'g_scores': dict(g_score),
                    'f_scores': dict(f_score_map),
                    'path_so_far': path_to_current,
                    'target': target
                }
                break

            # Explore neighbors
            for neighbor in G.neighbors(current):
                if neighbor in visited:
                    continue

                # MultiDiGraph can have multiple edges - select minimum
                edges = G[current][neighbor]
                if len(edges) == 1:
                    weight = edges[0].get("length", 1.0)
                else:
                    weight = min(edge.get("length", float("inf")) for edge in edges.values())

                tentative_g = g_score[current] + weight

                if tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    previous[neighbor] = current

                    # Weighted A*: f(n) = g(n) + ε × h(n)
                    f_score = tentative_g + (self.heuristic_weight * self.heuristic(
                        neighbor, target, pos
                    ))

                    f_score_map[neighbor] = f_score
                    heapq.heappush(open_set, (f_score, neighbor))

        # Path reconstruction
        if target not in previous and source != target:
            end_time = time.perf_counter()
            # ⭐ YIELD STEP: No path found
            yield {
                'type': 'complete',
                'current_node': None,
                'visited': visited.copy(),
                'open_set_nodes': [],
                'g_scores': dict(g_score),
                'f_scores': dict(f_score_map),
                'path_so_far': [],
                'target': target
            }
            return [], float("inf"), len(visited), (end_time - start_time) * 1000

        # Reconstruct final path
        path = [target]
        while path[-1] != source:
            path.append(previous[path[-1]])
        path.reverse()

        end_time = time.perf_counter()

        # ⭐ YIELD STEP: Algorithm complete
        yield {
            'type': 'complete',
            'current_node': target,
            'visited': visited.copy(),
            'open_set_nodes': [],
            'g_scores': dict(g_score),
            'f_scores': dict(f_score_map),
            'path_so_far': path,
            'target': target
        }

        return (
            path,
            g_score[target],
            len(visited),
            (end_time - start_time) * 1000,
        )
