"""Simple undirected graph with finite, nonnegative walking distances."""
import json
import math
from numbers import Real
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / 'data' / 'campus.json'


class Graph:
    def __init__(self, nodes, edges=()):
        nodes = list(nodes)
        if any(not isinstance(n, str) or not n.strip() for n in nodes):
            raise ValueError('Locations must have nonempty string names.')
        if len(set(nodes)) != len(nodes):
            raise ValueError('Duplicate locations are not allowed.')
        self.adj = {node: {} for node in sorted(nodes)}
        for u, v, weight in edges:
            self.set_edge(u, v, weight)

    @property
    def nodes(self):
        return tuple(self.adj)

    def require_node(self, node):
        if node not in self.adj:
            raise ValueError(f'Unknown location: {node}')

    def set_edge(self, u, v, weight):
        self.require_node(u)
        self.require_node(v)
        if u == v:
            raise ValueError('Self loops are not campus paths.')
        if isinstance(weight, bool) or not isinstance(weight, Real) or not math.isfinite(weight) or weight < 0:
            raise ValueError('Distance must be a finite nonnegative number.')
        self.adj[u][v] = weight
        self.adj[v][u] = weight
        # Sort at modification time: algorithm neighbor scans stay linear.
        self.adj[u] = dict(sorted(self.adj[u].items()))
        self.adj[v] = dict(sorted(self.adj[v].items()))

    def remove_edge(self, u, v):
        self.require_node(u)
        self.require_node(v)
        if v not in self.adj[u]:
            raise ValueError('That path does not exist.')
        del self.adj[u][v]
        del self.adj[v][u]

    def edges(self):
        return [(u, v, w) for u in self.nodes for v, w in self.adj[u].items() if u < v]

    def copy(self):
        return Graph(self.nodes, self.edges())


def load_campus():
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    return Graph(data['locations'], data['edges']), data['locations']
