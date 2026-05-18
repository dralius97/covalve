from collections import deque, defaultdict

def bfs(graph, start):
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

    

def validate_graph(schema) -> bool:
    if "INITIAL" not in schema or "FINAL" not in schema:
        raise ValueError("schema.json missing INITIAL or FINAL key")
    if schema["INITIAL"] not in schema["states"]:
        raise ValueError(f"INITIAL state '{schema['INITIAL']}' not found in states")

    graph = defaultdict(list)
    reverse_graph = defaultdict(list)
    for state, config in schema["states"].items():
        for transition in config["transitions"].values():
            to_state = transition["to"]

            graph[state].append(to_state)
            reverse_graph[to_state].append(state)

    exist_state = set(schema["states"].keys())
    print(reverse_graph)
    forward = bfs(graph, schema['INITIAL'])
    backward = bfs(reverse_graph, schema['FINAL'])

    return (
        exist_state.issubset(forward)
        and exist_state.issubset(backward)
    )