"""Six manual syllabus algorithms. trace=False disables explanatory history.

Events are compact deltas, not copies of algorithm state. All traversal tie
breaking is alphabetical; equal heap distances use the vertex name.
"""
from collections import deque
from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import inf


@dataclass
class Result:
    order: list = field(default_factory=list)
    path: list = field(default_factory=list)
    distance: float = inf
    distances: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)
    total: float = 0
    connected: bool = False
    steps: list = field(default_factory=list)


def event(steps, trace, kind, message, **details):
    if trace:
        steps.append(dict(kind=kind, message=message, **details))


def bfs(graph, source, trace=True):
    graph.require_node(source)
    result = Result()
    queue, seen = deque([source]), {source}
    event(result.steps, trace, 'discover', f'Enqueue {source}.', node=source)
    while queue:
        u = queue.popleft()
        result.order.append(u)
        event(result.steps, trace, 'visit', f'Dequeue and visit {u}.', node=u)
        for v in graph.adj[u]:
            if v not in seen:
                seen.add(v)  # Mark on enqueue: no vertex enters twice.
                queue.append(v)
                event(result.steps, trace, 'discover', f'Discover {v} from {u}; enqueue it.', node=v, edge=(u, v))
    result.connected = len(seen) == len(graph.nodes)
    return result


def dfs(graph, source, trace=True):
    graph.require_node(source)
    result = Result(order=[source])
    seen = {source}
    # Iterator frames simulate recursive DFS without Python's recursion limit.
    stack = [(source, iter(graph.adj[source]))]
    event(result.steps, trace, 'visit', f'Enter {source}; push an iterator frame.', node=source)
    while stack:
        u, neighbors = stack[-1]
        v = next(neighbors, None)
        if v is None:
            stack.pop()
            event(result.steps, trace, 'backtrack', f'Backtrack from {u}.', node=u)
        elif v not in seen:
            seen.add(v)
            result.order.append(v)
            stack.append((v, iter(graph.adj[v])))
            event(result.steps, trace, 'visit', f'Follow {u} to {v}; explore deeply.', node=v, edge=(u, v))
    result.connected = len(seen) == len(graph.nodes)
    return result


def dijkstra(graph, source, target=None, trace=True):
    graph.require_node(source)
    if target is not None:
        graph.require_node(target)
    result = Result(distances={n: inf for n in graph.nodes})
    result.distances[source] = 0
    parent, settled, heap = {}, set(), [(0, source)]
    while heap:
        distance, u = heappop(heap)
        if u in settled:
            continue  # Ignore obsolete lazy-heap entries.
        settled.add(u)
        result.order.append(u)
        event(result.steps, trace, 'settle', f'Settle {u} at {distance:g} m.', node=u, distance=distance)
        # Complete the source distance table, even when a target is requested.
        for v, weight in graph.adj[u].items():
            candidate = distance + weight
            if candidate < result.distances[v]:
                result.distances[v] = candidate
                parent[v] = u
                heappush(heap, (candidate, v))
                event(result.steps, trace, 'relax', f'Improve {v} via {u} to {candidate:g} m.', node=v, edge=(u, v), distance=candidate)
    if target is not None:
        result.distance = result.distances[target]
        if result.distance != inf:
            result.path = [target]
            while result.path[-1] != source:
                result.path.append(parent[result.path[-1]])
            result.path.reverse()
    result.connected = len(settled) == len(graph.nodes)
    return result


@dataclass
class AllPairs:
    nodes: tuple
    distances: dict
    next_hop: dict
    steps: list

    def path(self, source, target):
        if source not in self.distances or target not in self.distances:
            raise ValueError('Unknown location.')
        if self.next_hop[source][target] is None:
            return []
        path = [source]
        while source != target:
            source = self.next_hop[source][target]
            path.append(source)
        return path


def floyd_warshall(graph, trace=True):
    nodes = graph.nodes
    distances = {u: {v: (0 if u == v else inf) for v in nodes} for u in nodes}
    next_hop = {u: {v: (u if u == v else None) for v in nodes} for u in nodes}
    steps = []
    for u in nodes:
        for v, weight in graph.adj[u].items():
            distances[u][v], next_hop[u][v] = weight, v
    event(steps, trace, 'initialize', 'Start with direct paths, zero diagonal and infinity for missing paths.')
    for k in nodes:
        for u in nodes:
            for v in nodes:
                before = distances[u][v]
                left, right = distances[u][k], distances[k][v]
                candidate = left + right
                improved = candidate < before
                if improved:
                    distances[u][v] = candidate
                    next_hop[u][v] = next_hop[u][k]
                # One compact event per actual comparison; never copy the matrix.
                if trace:
                    event(steps, True, 'compare',
                          (f'Going from {u} to {v} through {k} gives a shorter distance; update the table.'
                           if improved else f'Going from {u} to {v} through {k} does not improve the distance.'),
                          k=k, i=u, j=v, before=before, left=left, right=right,
                          candidate=candidate, improved=improved,
                          next_hop=next_hop[u][v] if improved else None)
    event(steps, trace, 'complete', 'All intermediate vertices processed. The distance matrix is final.')
    return AllPairs(nodes, distances, next_hop, steps)


def prim(graph, source=None, trace=True):
    if source is not None:
        graph.require_node(source)
    result = Result()
    seen = set()
    roots = ([source] if source is not None else []) + [n for n in graph.nodes if n != source]
    # Restart on each component, producing a minimum spanning forest.
    for root in roots:
        if root in seen:
            continue
        heap = [(0, root, None)]
        while heap:
            weight, u, parent = heappop(heap)
            if u in seen:
                continue
            seen.add(u)
            result.order.append(u)
            if parent is None:
                event(result.steps, trace, 'root', f'Start component at {u}.', node=u)
            else:
                result.edges.append((parent, u, weight))
                result.total += weight
                event(result.steps, trace, 'accept', f'Choose {parent} - {u}: {weight:g} m.', node=u, edge=(parent, u), weight=weight)
            for v, cost in graph.adj[u].items():
                if v not in seen:
                    heappush(heap, (cost, v, u))
    result.connected = bool(graph.nodes) and len(result.edges) == len(graph.nodes) - 1
    return result


class DisjointSet:
    """Path compression and union by rank; nearly constant amortized operations."""
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank = {n: 0 for n in nodes}

    def find(self, node):
        root = node
        while root != self.parent[root]:
            root = self.parent[root]
        while node != root:
            previous = self.parent[node]
            self.parent[node] = root
            node = previous
        return root

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
        return True


def kruskal(graph, trace=True):
    result, groups = Result(), DisjointSet(graph.nodes)
    for u, v, weight in sorted(graph.edges(), key=lambda edge: (edge[2], edge[0], edge[1])):
        event(result.steps, trace, 'examine', f'Examine {u} - {v}: {weight:g} m; compare its components.',
              edge=(u, v), weight=weight)
        accepted = groups.union(u, v)
        if accepted:
            result.edges.append((u, v, weight))
            result.total += weight
        event(result.steps, trace, 'accept' if accepted else 'reject',
              (f'Accept {u} - {v}: its two components can be joined without a cycle.' if accepted
               else f'Adding {u} - {v} would form a cycle, so Kruskal skips it.'),
              edge=(u, v), weight=weight)
    result.connected = bool(graph.nodes) and len(result.edges) == len(graph.nodes) - 1
    event(result.steps, trace, 'complete',
          f'Completed minimum spanning {"tree" if result.connected else "forest"}: {result.total:g} m.',
          total=result.total, connected=result.connected)
    return result
