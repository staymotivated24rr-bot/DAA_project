"""Exhaust all 64 edge subsets on four vertices, without reference libraries."""
import itertools
import math
import unittest
from campus.graph import Graph
from campus.algorithms import bfs, dfs, dijkstra, floyd_warshall, prim, kruskal


def component_sets(graph):
    remaining=set(graph.nodes);components=[]
    while remaining:
        reached=set();pending=[min(remaining)]
        while pending:
            u=pending.pop()
            if u not in reached:
                reached.add(u);pending.extend(graph.adj[u])
        remaining-=reached;components.append(frozenset(reached))
    return set(components)


def shortest_simple_path(graph,source,target):
    best=math.inf
    def visit(u,cost,seen):
        nonlocal best
        if u==target:best=min(best,cost);return
        for v,w in graph.adj[u].items():
            if v not in seen:visit(v,cost+w,seen|{v})
    visit(source,0,{source})
    return best


class OracleTests(unittest.TestCase):
    def test_every_four_vertex_edge_subset(self):
        possible=[(u,v,w) for (u,v),w in zip(itertools.combinations('ABCD',2),[0,2,2,5,1,3])]
        for mask in range(64):
            with self.subTest(mask=mask):
                edges=[e for i,e in enumerate(possible) if mask&(1<<i)]
                graph=Graph('ABCD',edges)
                components=component_sets(graph)
                allpairs=floyd_warshall(graph,False)
                for source in graph.nodes:
                    expected_component=next(c for c in components if source in c)
                    for traverse in (bfs,dfs):
                        result=traverse(graph,source,False)
                        self.assertEqual(set(result.order),set(expected_component))
                        self.assertEqual(len(result.order),len(set(result.order)))
                    single=dijkstra(graph,source,trace=False)
                    for target in graph.nodes:
                        expected=shortest_simple_path(graph,source,target)
                        self.assertEqual(single.distances[target],expected)
                        self.assertEqual(allpairs.distances[source][target],expected)
                        path=allpairs.path(source,target)
                        if math.isinf(expected):self.assertEqual(path,[])
                        else:
                            self.assertEqual((path[0],path[-1]),(source,target))
                            self.assertEqual(sum(graph.adj[u][v] for u,v in zip(path,path[1:])),expected)
                needed=len(graph.nodes)-len(components)
                minimum=math.inf
                for subset in itertools.combinations(edges,needed):
                    if component_sets(Graph(graph.nodes,subset))==components:
                        minimum=min(minimum,sum(w for _,_,w in subset))
                for algorithm in (prim,kruskal):
                    result=algorithm(graph,trace=False)
                    self.assertEqual(result.total,minimum)
                    self.assertEqual(len(result.edges),needed)
                    self.assertEqual(result.connected,len(components)==1)
                    self.assertEqual(component_sets(Graph(graph.nodes,result.edges)),components)

    def test_empty_singleton_floats_and_equal_cost_ties(self):
        for traverse in (bfs,dfs,dijkstra):
            with self.assertRaises(ValueError):traverse(Graph([]),'A')
            result=traverse(Graph(['A']),'A')
            self.assertEqual(result.order,['A'])
        graph=Graph('ABCD',[('A','B',.5),('A','C',.5),('B','D',.5),('C','D',.5)])
        result=dijkstra(graph,'A','D')
        self.assertEqual(result.path,list('ABD'))
        self.assertEqual(result.distance,1)
        self.assertEqual(floyd_warshall(graph).path('A','D'),list('ABD'))
        for algorithm in (prim,kruskal):self.assertEqual(algorithm(graph).total,1.5)


if __name__=='__main__':unittest.main()
