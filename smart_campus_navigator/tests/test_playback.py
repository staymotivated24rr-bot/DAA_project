"""Regression tests for the state actually supplied to the step renderer."""
import math
import unittest
from unittest.mock import patch
from campus.graph import Graph, load_campus
from campus.algorithms import bfs, dfs, dijkstra, floyd_warshall, prim, kruskal
from campus.playback import execution_for, replay, table_path
from campus.visualization import base_figure, campus_figure, TEAL, AMBER, REJECTED, FRONTIER
from ui.steps import matrix_html


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph('ABCD',[('A','B',2),('A','C',5),('B','C',1),('C','D',3)])

    def test_context_reuse_and_parameter_reset(self):
        execution=execution_for(None,'route',self.graph,'Dijkstra','A','D')
        execution.move(1)
        self.assertIs(execution_for(execution,'route',self.graph,'Dijkstra','A','D'),execution)
        for page,name,source,target in [('other','Dijkstra','A','D'),('route','BFS','A',None),('route','Dijkstra','B','D'),('route','Dijkstra','A','C')]:
            changed=execution_for(execution,page,self.graph,name,source,target)
            self.assertEqual(changed.index,0)
            self.assertIsNot(changed,execution)

    def test_edits_cannot_reuse_stale_results(self):
        execution=execution_for(None,'route',self.graph,'Dijkstra','A','D')
        self.graph.set_edge('A','D',1)
        updated=execution_for(execution,'route',self.graph,'Dijkstra','A','D')
        self.assertEqual(updated.result.distance,1)
        self.assertEqual(updated.index,0)
        self.graph.remove_edge('A','D')
        restored=execution_for(updated,'route',self.graph,'Dijkstra','A','D')
        self.assertEqual(restored.result.distance,6)

    def test_floyd_parameter_change_reuses_readonly_answer_resets_position(self):
        execution=execution_for(None,'pairs',self.graph,'Floyd-Warshall','A','D')
        execution.move(7)
        with patch('campus.playback.floyd_warshall',side_effect=AssertionError('unnecessary recomputation')):
            changed=execution_for(execution,'pairs',self.graph,'Floyd-Warshall','B','C')
        self.assertIs(changed.result,execution.result)
        self.assertEqual(changed.index,0)

    def test_navigation_clamped_and_reversible_for_each_algorithm(self):
        for name in ['BFS','DFS','Dijkstra','Floyd-Warshall','Prim','Kruskal']:
            source='A' if name not in ('Floyd-Warshall','Kruskal') else None
            execution=execution_for(None,'lab',self.graph,name,source,'D' if name=='Dijkstra' else None)
            snapshots=[]
            for index in range(len(execution.result.steps)):
                self.assertEqual(execution.index,index)
                snapshots.append(replay(self.graph,name,execution.result.steps,index))
                execution.move(1)
            self.assertEqual(execution.index,len(snapshots)-1)
            for index in reversed(range(len(snapshots))):
                self.assertEqual(replay(self.graph,name,execution.result.steps,execution.index),snapshots[index])
                execution.move(-1)
            self.assertEqual(execution.index,0)
            execution.move(10**6);execution.move();self.assertEqual(execution.index,0)

    def test_floyd_every_comparison_matches_independent_matrix(self):
        result=floyd_warshall(self.graph)
        nodes=self.graph.nodes
        expected={u:{v:0 if u==v else self.graph.adj[u].get(v,math.inf) for v in nodes} for u in nodes}
        initial=replay(self.graph,'Floyd-Warshall',result.steps,0)
        self.assertNotEqual(initial.matrix,result.distances)
        position=1
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    step=result.steps[position]
                    self.assertEqual((step['k'],step['i'],step['j']),(k,i,j))
                    self.assertEqual(step['before'],expected[i][j])
                    self.assertEqual(step['left'],expected[i][k])
                    self.assertEqual(step['right'],expected[k][j])
                    candidate=expected[i][k]+expected[k][j]
                    self.assertEqual(step['candidate'],candidate)
                    self.assertEqual(step['improved'],candidate<expected[i][j])
                    expected[i][j]=min(expected[i][j],candidate)
                    frame=replay(self.graph,'Floyd-Warshall',result.steps,position)
                    self.assertEqual(frame.matrix,expected)
                    position+=1
        self.assertEqual(expected,result.distances)
        self.assertEqual(len(result.steps),len(nodes)**3+2)
        final=replay(self.graph,'Floyd-Warshall',result.steps,len(result.steps)-1)
        self.assertEqual(final.matrix,result.distances)
        for u in nodes:
            for v in nodes:self.assertEqual(table_path(final.next_hop,u,v),result.path(u,v))

    def test_campus_floyd_final_matrix_and_backward_update(self):
        graph,_=load_campus();result=floyd_warshall(graph)
        final=replay(graph,'Floyd-Warshall',result.steps,len(result.steps)-1)
        self.assertEqual(final.matrix,result.distances)
        updated=next(i for i,s in enumerate(result.steps) if s.get('improved'))
        step=result.steps[updated]
        before=replay(graph,'Floyd-Warshall',result.steps,updated-1)
        after=replay(graph,'Floyd-Warshall',result.steps,updated)
        self.assertEqual(before.matrix[step['i']][step['j']],step['before'])
        self.assertEqual(after.matrix[step['i']][step['j']],step['candidate'])

    def test_floyd_highlights_only_real_graph_paths(self):
        result=floyd_warshall(self.graph)
        for index in range(len(result.steps)):
            frame=replay(self.graph,'Floyd-Warshall',result.steps,index)
            for u,v in frame.current_edges:self.assertIn(v,self.graph.adj[u])

    def test_bfs_discovery_is_not_visiting(self):
        result=bfs(self.graph,'A')
        initial=replay(self.graph,'BFS',result.steps,0)
        self.assertEqual(initial.visited,set())
        self.assertEqual(initial.frontier,{'A'})
        visited=replay(self.graph,'BFS',result.steps,1)
        self.assertEqual(visited.visited,{'A'})
        self.assertEqual(visited.frontier,set())

    def test_dfs_stack_backtracks(self):
        result=dfs(self.graph,'A')
        for index,step in enumerate(result.steps):
            frame=replay(self.graph,'DFS',result.steps,index)
            if step['kind']=='backtrack':self.assertNotIn(step['node'],frame.active)
            for u,v in frame.current_edges:self.assertIn(v,self.graph.adj[u])
        self.assertEqual(frame.active,[])
        self.assertEqual(frame.visited,set(self.graph.nodes))

    def test_dijkstra_retains_settled_tree_on_relaxation(self):
        result=dijkstra(self.graph,'A','D')
        index=next(i for i,s in enumerate(result.steps) if s['kind']=='relax' and s.get('node')=='D')
        frame=replay(self.graph,'Dijkstra',result.steps,index)
        self.assertIn(('A','B'),frame.selected)
        self.assertIn(('B','C'),frame.selected)
        self.assertEqual(frame.current_edges,[('C','D')])
        self.assertEqual(frame.distances['D'],6)
        final=replay(self.graph,'Dijkstra',result.steps,len(result.steps)-1)
        self.assertEqual(final.distances,result.distances)

    def test_kruskal_examine_accept_reject_complete(self):
        result=kruskal(self.graph)
        for index,step in enumerate(result.steps):
            frame=replay(self.graph,'Kruskal',result.steps,index)
            if step['kind']=='examine':self.assertEqual(frame.current_edges,[step['edge']])
            if step['kind']=='reject':
                self.assertIn(step['edge'],frame.rejected)
                self.assertIn('cycle',step['message'])
        self.assertEqual(result.steps[-1]['kind'],'complete')
        self.assertEqual(frame.selected,[e[:2] for e in result.edges])
        self.assertTrue(frame.rejected)

    def test_prim_final_forest(self):
        graph=Graph('ABCDE',[('A','B',1),('C','D',2)])
        result=prim(graph,'A')
        frame=replay(graph,'Prim',result.steps,len(result.steps)-1)
        self.assertEqual(frame.visited,set(graph.nodes))
        self.assertEqual(frame.selected,[e[:2] for e in result.edges])

    def test_figure_overlay_colors_and_base_is_immutable(self):
        coordinates=dict(A=(0,0),B=(100,0),C=(50,80),D=(150,80))
        from copy import deepcopy
        base=base_figure(self.graph,coordinates)
        original=deepcopy(base)
        fig=campus_figure(self.graph,coordinates,[('A','B')],['A'],frontier=['C'],rejected=[('A','C')],current_edges=[('B','C')],base=base)
        self.assertEqual(base,original)
        colors={t.name:t.line.color for t in fig.data if t.mode=='lines'}
        self.assertEqual(colors['Selected edges'],TEAL)
        self.assertEqual(colors['Rejected cycle edges'],REJECTED)
        self.assertEqual(colors['Currently examined'],AMBER)
        self.assertEqual(fig.data[-1].marker.color[2],FRONTIER)
        self.assertEqual(len(fig.data),5)
        with self.assertRaises(ValueError):campus_figure(self.graph,coordinates,[('A','D')])

    def test_matrix_highlights_and_escapes_labels(self):
        result=floyd_warshall(self.graph)
        index=next(i for i,s in enumerate(result.steps) if s.get('improved'))
        frame=replay(self.graph,'Floyd-Warshall',result.steps,index)
        html=matrix_html(self.graph.nodes,frame.matrix,result.steps[index])
        self.assertIn('class="improved"',html)
        self.assertIn('aria-label="Floyd-Warshall',html)
        self.assertIn('overflow-x:auto',html)
        html=matrix_html(['<A>'],{'<A>':{'<A>':0}})
        self.assertIn('&lt;A&gt;',html)
        self.assertNotIn('<A>',html)

    def test_invalid_index_and_algorithm(self):
        with self.assertRaises(ValueError):replay(self.graph,'BFS',[],0)
        with self.assertRaises(ValueError):execution_for(None,'lab',self.graph,'Unknown')


    def test_late_callback_cannot_change_replaced_execution(self):
        from ui.steps import move_current
        old=execution_for(None,'lab',self.graph,'BFS','A')
        new=execution_for(old,'lab',self.graph,'DFS','A')
        with patch('ui.steps.st.session_state',{'_execution':new}):
            move_current(old.signature,1)
            self.assertEqual(new.index,0)
            move_current(new.signature,1)
            self.assertEqual(new.index,1)

if __name__=='__main__':unittest.main()
