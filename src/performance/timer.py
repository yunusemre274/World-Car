import time
from functools import wraps


def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        execution_time_ms = (end - start) * 1000

        # Expected result: (path, distance, visited_nodes, time)
        if isinstance(result, tuple) and len(result) == 4:
            path, distance, visited, _ = result
            return path, distance, visited, execution_time_ms

        return result

    return wrapper
