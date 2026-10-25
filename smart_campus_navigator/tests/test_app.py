"""Streamlit integration tests exercise real session state and UI callbacks."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'


class ApplicationTests(unittest.TestCase):
    def test_all_pages_and_controls(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual([m.value for m in app.metric][:3],['10','17','6'])
        pages=['Campus Route Finder','Graph Exploration','Campus Network Optimizer','All-Pairs Route Analyzer','Learning Lab']
        for page in pages:
            with self.subTest(page=page):
                app.sidebar.radio[0].set_value(page).run()
                self.assertFalse(app.exception)
                if page=='Campus Route Finder':
                    self.assertEqual(app.metric[0].value,'830 m')
                    self.assertIn('Hostel',app.success[0].value)
                if page=='Campus Network Optimizer':
                    self.assertEqual(app.metric[0].value,'1690 m')
                    [s for s in app.selectbox if s.label=='MST algorithm'][0].set_value('Kruskal').run()
                    self.assertEqual(app.metric[0].value,'1690 m')
                if page in ('Graph Exploration','Learning Lab'):
                    next_button=[b for b in app.button if b.label=='Next →'][0]
                    next_button.click().run()
                    self.assertFalse(app.exception)
                    self.assertIn('Step 2',app.get('progress')[0].proto.text)
                    [b for b in app.button if b.label=='Reset steps'][0].click().run()
                    self.assertIn('Step 1',app.get('progress')[0].proto.text)
        for algorithm in ['BFS','DFS','Dijkstra','Floyd-Warshall','Prim','Kruskal']:
            [s for s in app.selectbox if s.label=='Study an algorithm'][0].set_value(algorithm).run()
            self.assertFalse(app.exception)
        [b for b in app.button if b.label=='Run small benchmark'][0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state['benchmark']),18)

    def test_edit_restore_and_same_node(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        app.sidebar.radio[0].set_value('Campus Route Finder').run()
        app.selectbox(key='routesource').set_value('Main Gate')
        app.selectbox(key='routetarget').set_value('Main Gate').run()
        self.assertEqual(app.metric[0].value,'0 m')
        app.selectbox(key='routetarget').set_value('Hostel').run()
        [s for s in app.selectbox if s.label=='Path endpoint A'][0].set_value('Main Gate')
        [s for s in app.selectbox if s.label=='Path endpoint B'][0].set_value('Hostel')
        app.number_input[0].set_value(10.0)
        [b for b in app.button if b.label=='Apply path change'][0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'10 m')
        [b for b in app.button if b.label=='Restore original graph'][0].click().run()
        self.assertEqual(app.metric[0].value,'830 m')
        self.assertFalse(app.exception)


    def test_disconnected_and_invalid_form(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        for endpoint in ['Administrative Block','Academic Block']:
            [s for s in app.selectbox if s.label=='Path endpoint A'][0].set_value('Main Gate')
            [s for s in app.selectbox if s.label=='Path endpoint B'][0].set_value(endpoint)
            [s for s in app.selectbox if s.label=='Action'][0].set_value('Remove')
            [b for b in app.button if b.label=='Apply path change'][0].click().run()
        app.sidebar.radio[0].set_value('Campus Route Finder').run()
        self.assertIn('unreachable',app.warning[0].value)
        app.sidebar.radio[0].set_value('Campus Network Optimizer').run()
        self.assertEqual(app.metric[0].value,'1550 m')
        self.assertIn('Disconnected graph',app.warning[0].value)
        [s for s in app.selectbox if s.label=='Path endpoint A'][0].set_value('Library')
        [s for s in app.selectbox if s.label=='Path endpoint B'][0].set_value('Library')
        [s for s in app.selectbox if s.label=='Action'][0].set_value('Add / update')
        [b for b in app.button if b.label=='Apply path change'][0].click().run()
        self.assertIn('Self loops',app.error[0].value)
        self.assertFalse(app.exception)


    def test_navigation_boundaries_for_all_six_algorithms(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        app.sidebar.radio[0].set_value('Learning Lab').run()
        for name in ['BFS','DFS','Dijkstra','Floyd-Warshall','Prim','Kruskal']:
            with self.subTest(algorithm=name):
                [s for s in app.selectbox if s.label=='Study an algorithm'][0].set_value(name).run()
                execution=app.session_state['_execution']
                self.assertEqual(execution.index,0)
                self.assertTrue(app.button(key='playback_previous').disabled)
                app.button(key='playback_next').click().run()
                self.assertEqual(app.session_state['_execution'].index,1)
                app.button(key='playback_previous').click().run()
                self.assertEqual(app.session_state['_execution'].index,0)
                execution=app.session_state['_execution']
                execution.index=len(execution.result.steps)-1
                app.run()
                self.assertTrue(app.button(key='playback_next').disabled)
                self.assertFalse(app.exception)
                app.button(key='playback_reset').click().run()
                self.assertEqual(app.session_state['_execution'].index,0)

    def test_session_state_stays_bounded_across_switches(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        app.sidebar.radio[0].set_value('Learning Lab').run()
        names=['BFS','DFS','Dijkstra','Floyd-Warshall','Prim','Kruskal']
        for iteration in range(36):
            [s for s in app.selectbox if s.label=='Study an algorithm'][0].set_value(names[iteration%6]).run()
            app.button(key='playback_next').click().run()
            self.assertFalse(app.exception)
        state=app.session_state.to_dict()
        self.assertLess(len(state),25)
        self.assertFalse(any(k.startswith(('lab_','explore_','route_','floyd_','mst_')) for k in state))
        app.sidebar.radio[0].set_value('Dashboard').run()
        self.assertNotIn('_execution',app.session_state.to_dict())

    def test_source_destination_and_page_changes_reset(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        app.sidebar.radio[0].set_value('Campus Route Finder').run()
        app.button(key='playback_next').click().run()
        app.selectbox(key='routetarget').set_value('Library').run()
        self.assertEqual(app.session_state['_execution'].index,0)
        self.assertEqual(app.metric[0].value,'450 m')
        app.button(key='playback_next').click().run()
        app.selectbox(key='routesource').set_value('Library').run()
        self.assertEqual(app.session_state['_execution'].index,0)
        self.assertEqual(app.metric[0].value,'0 m')
        app.sidebar.radio[0].set_value('Graph Exploration').run()
        self.assertEqual(app.session_state['_execution'].index,0)
        self.assertEqual(app.session_state['_execution'].algorithm,'BFS')

    def test_history_and_canvas_not_rebuilt_on_steps(self):
        from unittest.mock import patch
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        app.sidebar.radio[0].set_value('Graph Exploration').run()
        initial=app.session_state['_execution']
        with patch('campus.playback.bfs',side_effect=AssertionError('History was rebuilt')), patch('ui.steps.base_figure',side_effect=AssertionError('Canvas was rebuilt')):
            for _ in range(3):app.button(key='playback_next').click().run()
        self.assertFalse(app.exception)
        self.assertIs(app.session_state['_execution'].result,initial.result)

    def test_graph_edit_invalidates_history_and_restore(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        app.sidebar.radio[0].set_value('Campus Route Finder').run()
        app.button(key='playback_next').click().run()
        previous=app.session_state['_execution'].signature
        [s for s in app.selectbox if s.label=='Path endpoint A'][0].set_value('Main Gate')
        [s for s in app.selectbox if s.label=='Path endpoint B'][0].set_value('Hostel')
        app.number_input[0].set_value(100.0)
        [b for b in app.button if b.label=='Apply path change'][0].click().run()
        self.assertEqual(app.metric[0].value,'100 m')
        self.assertNotEqual(app.session_state['_execution'].signature,previous)
        self.assertEqual(app.session_state['_execution'].index,0)
        app.button(key='playback_next').click().run()
        [b for b in app.button if b.label=='Restore original graph'][0].click().run()
        self.assertEqual(app.metric[0].value,'830 m')
        self.assertEqual(app.session_state['_execution'].index,0)

    def test_two_sessions_do_not_share_graph_or_execution(self):
        first=AppTest.from_file(str(APP),default_timeout=30).run()
        second=AppTest.from_file(str(APP),default_timeout=30).run()
        first.session_state['graph'].set_edge('Main Gate','Hostel',10)
        for app in (first,second):app.sidebar.radio[0].set_value('Campus Route Finder').run()
        self.assertEqual(first.metric[0].value,'10 m')
        self.assertEqual(second.metric[0].value,'830 m')
        self.assertIsNot(first.session_state['_execution'],second.session_state['_execution'])

    def test_upgrade_cleans_legacy_indices_preserves_graph(self):
        app=AppTest.from_file(str(APP),default_timeout=30).run()
        app.session_state['_playback_schema']=1
        app.session_state['explore_BFS_Main Gate_0']=4
        app.session_state['lab_DFS_9']=8
        app.session_state['graph'].set_edge('Main Gate','Hostel',50)
        app.sidebar.radio[0].set_value('Campus Route Finder').run()
        self.assertNotIn('explore_BFS_Main Gate_0',app.session_state)
        self.assertNotIn('lab_DFS_9',app.session_state)
        self.assertEqual(app.metric[0].value,'50 m')
        self.assertEqual(app.session_state['_playback_schema'],2)

if __name__=='__main__':unittest.main()
