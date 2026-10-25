import itertools
import math
import unittest
from campus.graph import Graph, load_campus
from campus.algorithms import bfs, dfs, dijkstra, floyd_warshall, prim, kruskal, DisjointSet
from campus.benchmark import generated_graph


class AlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.graph=Graph('ABCD',[('A','B',2),('B','C',1),('A','C',5),('C','D',3),('B','D',8)])

    def test_bfs_order(self):
        self.assertEqual(bfs(self.graph,'A').order,list('ABCD'))

    def test_dfs_order(self):
        self.assertEqual(dfs(self.graph,'A').order,list('ABCD'))

    def test_dijkstra_known_route(self):
        result=dijkstra(self.graph,'A','D')
        self.assertEqual(result.path,list('ABCD'))
        self.assertEqual(result.distance,6)
        self.assertEqual(result.distances,dict(A=0,B=2,C=3,D=6))

    def test_floyd_reconstruction(self):
        result=floyd_warshall(self.graph)
        self.assertEqual(result.path('A','D'),list('ABCD'))
        self.assertEqual(result.distances['A']['D'],6)
        self.assertEqual(result.path('D','A'),list('DCBA'))

    def test_known_mst(self):
        for algorithm in (prim,kruskal):
            result=algorithm(self.graph)
            self.assertTrue(result.connected)
            self.assertEqual(result.total,6)
            self.assertEqual(len(result.edges),3)

    def test_disconnected(self):
        graph=Graph('ABCDE',[('A','B',2),('C','D',1)])
        for algorithm in (bfs,dfs):
            result=algorithm(graph,'A')
            self.assertEqual(result.order,list('AB'))
            self.assertFalse(result.connected)
        result=dijkstra(graph,'A','E')
        self.assertEqual(result.path,[])
        self.assertEqual(result.distance,math.inf)
        allpairs=floyd_warshall(graph)
        self.assertEqual(allpairs.path('A','E'),[])
        for algorithm in (prim,kruskal):
            result=algorithm(graph)
            self.assertFalse(result.connected)
            self.assertEqual(result.total,3)
            self.assertEqual(len(result.edges),2)

    def test_zero_weights(self):
        graph=Graph('ABC',[('A','B',0),('B','C',0),('A','C',4)])
        self.assertEqual(dijkstra(graph,'A','C').distance,0)
        self.assertEqual(floyd_warshall(graph).path('A','C'),list('ABC'))
        self.assertEqual(prim(graph).total,0)
        self.assertEqual(kruskal(graph).total,0)

    def test_same_source_destination(self):
        result=dijkstra(self.graph,'B','B')
        self.assertEqual((result.path,result.distance),(['B'],0))
        self.assertEqual(floyd_warshall(self.graph).path('B','B'),['B'])

    def test_invalid_locations(self):
        for algorithm in (bfs,dfs,dijkstra,prim):
            with self.assertRaises(ValueError):algorithm(self.graph,'Unknown')
        with self.assertRaises(ValueError):dijkstra(self.graph,'A','Unknown')
        with self.assertRaises(ValueError):floyd_warshall(self.graph).path('A','Unknown')

    def test_invalid_weights(self):
        for weight in (-1,math.nan,math.inf,True,'10',None):
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                self.graph.set_edge('A','B',weight)
        self.assertEqual(self.graph.adj['A']['B'],2)

    def test_graph_edits_and_restore(self):
        graph,_=load_campus()
        original=graph.edges()
        graph.set_edge('Main Gate','Hostel',10)
        self.assertEqual(dijkstra(graph,'Main Gate','Hostel').distance,10)
        graph.set_edge('Main Gate','Hostel',20)
        self.assertEqual(graph.adj['Hostel']['Main Gate'],20)
        graph.remove_edge('Hostel','Main Gate')
        self.assertEqual(graph.edges(),original)
        graph.remove_edge('Main Gate','Academic Block')
        restored,_=load_campus()
        self.assertEqual(restored.edges(),original)
        self.assertNotEqual(graph.edges(),restored.edges())

    def test_invalid_graph_operations(self):
        for args in [('A','A',1),('A','X',1)]:
            with self.assertRaises(ValueError):self.graph.set_edge(*args)
        with self.assertRaises(ValueError):self.graph.remove_edge('A','D')
        with self.assertRaises(ValueError):Graph(['A','A'])
        with self.assertRaises(ValueError):Graph([''])

    def test_empty_and_singleton(self):
        empty=Graph([])
        self.assertEqual(floyd_warshall(empty).distances,{})
        for algorithm in (prim,kruskal):
            self.assertFalse(algorithm(empty).connected)
            result=algorithm(Graph(['A']))
            self.assertTrue(result.connected)
            self.assertEqual(result.total,0)
        self.assertEqual(dijkstra(Graph(['A']),'A','A').distance,0)

    def test_trace_disabled_and_determinism(self):
        for algorithm in (bfs,dfs,dijkstra):
            self.assertEqual(algorithm(self.graph,'A',trace=False).steps,[])
            self.assertEqual(algorithm(self.graph,'A').steps,algorithm(self.graph,'A').steps)
        for algorithm in (prim,kruskal,floyd_warshall):
            self.assertEqual(algorithm(self.graph,trace=False).steps,[])

    def test_all_pairs_agree_on_generated_graphs(self):
        for size in (3,7,12):
            graph=generated_graph(size)
            allpairs=floyd_warshall(graph,False)
            for source in graph.nodes:
                result=dijkstra(graph,source,trace=False)
                self.assertEqual(result.distances,allpairs.distances[source])
                for target in graph.nodes:
                    path=allpairs.path(source,target)
                    self.assertEqual(sum(graph.adj[u][v] for u,v in zip(path,path[1:])),result.distances[target])

    def test_mst_against_exhaustive_tiny_graph(self):
        # Independent oracle: enumerate all V-1 edge subsets, check connectivity.
        minimum=math.inf
        for edges in itertools.combinations(self.graph.edges(),3):
            candidate=Graph(self.graph.nodes,edges)
            if len(bfs(candidate,'A',False).order)==4:
                minimum=min(minimum,sum(w for _,_,w in edges))
        self.assertEqual(prim(self.graph).total,minimum)
        self.assertEqual(kruskal(self.graph).total,minimum)

    def test_tied_mst_and_cycles(self):
        graph=Graph('ABCD',[(u,v,1) for u,v in itertools.combinations('ABCD',2)])
        for algorithm in (prim,kruskal):
            result=algorithm(graph)
            self.assertEqual(result.total,3)
            self.assertEqual(len(result.edges),3)
            self.assertTrue(result.connected)
        self.assertTrue(any(e['kind']=='reject' for e in kruskal(graph).steps))

    def test_disjoint_set(self):
        groups=DisjointSet('ABCDE')
        self.assertTrue(groups.union('A','B'))
        self.assertTrue(groups.union('C','D'))
        self.assertTrue(groups.union('B','D'))
        self.assertEqual(groups.find('A'),groups.find('C'))
        self.assertFalse(groups.union('A','D'))
        self.assertNotEqual(groups.find('E'),groups.find('A'))

    def test_deep_iterative_dfs(self):
        nodes=[f'N{i:04}' for i in range(1200)]
        graph=Graph(nodes,[(nodes[i-1],nodes[i],1) for i in range(1,len(nodes))])
        self.assertEqual(len(dfs(graph,nodes[0],False).order),1200)

    def test_campus_acceptance(self):
        graph,coordinates=load_campus()
        self.assertEqual((len(graph.nodes),len(graph.edges())),(10,17))
        self.assertEqual(set(coordinates),set(graph.nodes))
        result=dijkstra(graph,'Main Gate','Hostel')
        self.assertEqual(result.distance,830)
        self.assertEqual(result.path,['Main Gate','Academic Block','Library','Canteen','Hostel'])
        self.assertEqual(prim(graph,'Main Gate').total,1690)
        self.assertEqual(kruskal(graph).total,1690)
        # Walking paths cannot be shorter than their diagram's straight-line length.
        for u,v,w in graph.edges():self.assertGreaterEqual(w,math.dist(coordinates[u],coordinates[v]))


if __name__=='__main__':unittest.main()
