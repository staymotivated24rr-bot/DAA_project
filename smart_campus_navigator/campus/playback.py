"""Pure execution/state replay. No Streamlit import and no cross-session cache.

One active execution replaces the old one on a context change. Navigation
replays compact deltas from the beginning, allowing exact backwards seeking
without retaining a matrix per frame (O(V² + t) seek work for Floyd).
"""
from dataclasses import dataclass, field
from math import inf
from .algorithms import bfs, dfs, dijkstra, floyd_warshall, prim, kruskal


@dataclass
class Execution:
    signature: tuple
    algorithm: str
    result: object
    index: int = 0
    base_figure: dict | None = None

    def move(self, delta: int | None = None) -> None:
        last = max(0, len(self.result.steps) - 1)
        self.index = 0 if delta is None else max(0, min(last, self.index + delta))


def execution_for(previous, page, graph, algorithm, source=None, target=None):
    """Bounded session-local reuse; the fingerprint covers the actual graph."""
    signature = (page, algorithm, source, target, graph.nodes, tuple(graph.edges()))
    if previous is not None and previous.signature == signature:
        return previous
    if (previous is not None and algorithm == previous.algorithm == 'Floyd-Warshall'
            and previous.signature[-2:] == signature[-2:]):
        return Execution(signature, algorithm, previous.result, base_figure=previous.base_figure)
    if algorithm == 'BFS': result = bfs(graph, source)
    elif algorithm == 'DFS': result = dfs(graph, source)
    elif algorithm == 'Dijkstra': result = dijkstra(graph, source, target)
    elif algorithm == 'Floyd-Warshall': result = floyd_warshall(graph)
    elif algorithm == 'Prim': result = prim(graph, source)
    elif algorithm == 'Kruskal': result = kruskal(graph)
    else: raise ValueError(f'Unknown algorithm: {algorithm}')
    return Execution(signature, algorithm, result)


@dataclass
class Frame:
    visited: set = field(default_factory=set)
    frontier: set = field(default_factory=set)
    active: list = field(default_factory=list)
    selected: list = field(default_factory=list)
    rejected: list = field(default_factory=list)
    current_edges: list = field(default_factory=list)
    current: str | None = None
    distances: dict = field(default_factory=dict)
    matrix: dict = field(default_factory=dict)
    next_hop: dict = field(default_factory=dict)


def initial_tables(graph):
    distances = {u: {v: 0 if u == v else graph.adj[u].get(v, inf) for v in graph.nodes} for u in graph.nodes}
    next_hop = {u: {v: v if u == v or v in graph.adj[u] else None for v in graph.nodes} for u in graph.nodes}
    return distances, next_hop


def table_path(next_hop, source, target):
    if next_hop[source][target] is None:
        return []
    path = [source]
    while source != target:
        source = next_hop[source][target]
        path.append(source)
    return path


def replay(graph, algorithm, steps, index):
    """Interpret each algorithm's semantics rather than guessing from event names."""
    if not 0 <= index < len(steps):
        raise ValueError('Step index is outside the available history.')
    frame = Frame()
    if algorithm == 'Floyd-Warshall':
        frame.matrix, frame.next_hop = initial_tables(graph)
    if algorithm == 'Dijkstra':
        frame.distances = {n: inf for n in graph.nodes}
    parent = {}
    for event in steps[:index+1]:
        kind = event['kind']
        node = event.get('node')
        if algorithm == 'BFS':
            if kind == 'discover':
                frame.frontier.add(node)
                if 'edge' in event: frame.selected.append(event['edge'])
            elif kind == 'visit':
                frame.visited.add(node)
                frame.frontier.discard(node)
        elif algorithm == 'DFS':
            if kind == 'visit':
                frame.visited.add(node)
                frame.active.append(node)
                if 'edge' in event: frame.selected.append(event['edge'])
            elif kind == 'backtrack':
                frame.active.pop()
        elif algorithm == 'Dijkstra':
            if kind == 'settle':
                frame.visited.add(node)
                frame.frontier.discard(node)
                frame.distances[node] = event['distance']
            elif kind == 'relax':
                frame.frontier.add(node)
                frame.distances[node] = event['distance']
                parent[node] = event['edge'][0]
        elif algorithm == 'Prim':
            if kind in ('root', 'accept'): frame.visited.add(node)
            if kind == 'accept': frame.selected.append(event['edge'])
        elif algorithm == 'Kruskal':
            if kind == 'accept':
                frame.selected.append(event['edge'])
                frame.visited.update(event['edge'])
            elif kind == 'reject': frame.rejected.append(event['edge'])
        elif algorithm == 'Floyd-Warshall':
            if kind == 'compare' and event['improved']:
                i, j = event['i'], event['j']
                frame.matrix[i][j] = event['candidate']
                frame.next_hop[i][j] = event['next_hop']
        else:
            raise ValueError(f'Unknown algorithm: {algorithm}')
    current = steps[index]
    kind = current['kind']
    frame.current = current.get('node')
    if algorithm == 'DFS':
        frame.current_edges = list(zip(frame.active, frame.active[1:]))
    elif algorithm == 'Dijkstra':
        frame.selected = [(u, v) for v, u in parent.items() if v in frame.visited]
        if kind == 'relax': frame.current_edges = [current['edge']]
    elif algorithm == 'Kruskal':
        if kind == 'examine': frame.current_edges = [current['edge']]
    elif algorithm == 'Floyd-Warshall' and kind == 'compare':
        frame.current = current['k']
        left = table_path(frame.next_hop, current['i'], current['k'])
        right = table_path(frame.next_hop, current['k'], current['j'])
        frame.current_edges = list(zip(left, left[1:])) + list(zip(right, right[1:]))
    return frame
