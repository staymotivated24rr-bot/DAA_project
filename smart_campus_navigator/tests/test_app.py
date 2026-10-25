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

if __name__=='__main__':unittest.main()
