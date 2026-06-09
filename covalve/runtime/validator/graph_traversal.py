from collections import deque, defaultdict
from covalve.runtime.models.schema import CoreSchema

def bfs(graph: dict[str, list], start: str) -> set:
    visited = set()
    queue = deque([start])

    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph[node]:
            queue.append(neighbor)

    return visited


def validate_graph(schema: CoreSchema) -> bool:
    if schema.INITIAL not in schema.states:
        raise ValueError(f"INITIAL state '{schema.INITIAL}' not found in states")

    graph: dict[str, list] = defaultdict(list)
    reverse_graph: dict[str, list] = defaultdict(list)

    for state, config in schema.states.items():
        for transition in config.transitions.values():
            to_state = transition.to
            graph[state].append(to_state)
            reverse_graph[to_state].append(state)

    exist_state = set(schema.states.keys())
    forward = bfs(graph, schema.INITIAL)
    backward = bfs(reverse_graph, schema.FINAL)

    return (
        exist_state.issubset(forward)
        and exist_state.issubset(backward)
    )