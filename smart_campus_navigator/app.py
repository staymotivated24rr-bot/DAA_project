"""Run with: python -m streamlit run app.py"""
import math
import streamlit as st
import plotly.graph_objects as go
from campus.graph import load_campus
from campus.algorithms import bfs, dfs, dijkstra, floyd_warshall, prim, kruskal
from campus.visualization import campus_figure
from campus.learning import ALGORITHMS, COMPLEXITY_NOTE, PSEUDOCODE, CORRECTNESS

st.set_page_config(page_title='Smart Campus Navigator', page_icon='🧭', layout='wide')
st.markdown('''<style>
.block-container{max-width:1420px;padding-top:4.5rem;padding-bottom:3rem}
h1{font-size:2.5rem!important;letter-spacing:-.05em} h2{letter-spacing:-.025em}
[data-testid="stMetric"]{background:#111c2e;border:1px solid #26364e;border-radius:12px;padding:16px}
[data-testid="stSidebar"]{border-right:1px solid #26364e}
.stButton>button{border-radius:8px} .eyebrow{color:#35d9c0;font-size:.8rem;letter-spacing:.18em;font-weight:700}
</style>''', unsafe_allow_html=True)
if 'graph' not in st.session_state:
    st.session_state.graph, st.session_state.coordinates = load_campus()
    st.session_state.revision = 0

graph, coordinates = st.session_state.graph, st.session_state.coordinates
with st.sidebar:
    st.markdown('### 🧭 Campus Navigator')
    st.caption('DESIGN & ANALYSIS OF ALGORITHMS')
    page = st.radio('Workspace', ['Dashboard', 'Campus Route Finder', 'Graph Exploration', 'Campus Network Optimizer', 'All-Pairs Route Analyzer', 'Learning Lab'])
    st.divider()
    st.caption('01AI0506 · Unit 4 + Unit 1')
    st.caption('Fictional campus · undirected graph · metres')
    with st.expander('Edit campus paths'):
        st.caption('Changes stay in this browser session. Zero distance is supported for teaching; it is not realistic walking data.')
        with st.form('editor'):
            u = st.selectbox('Path endpoint A', graph.nodes)
            v = st.selectbox('Path endpoint B', graph.nodes, index=1)
            action = st.selectbox('Action', ['Add / update', 'Remove'])
            weight = st.number_input('Walking distance (m)', min_value=0.0, value=150.0, step=10.0)
            submit = st.form_submit_button('Apply path change')
        if submit:
            try:
                if action == 'Remove': graph.remove_edge(u, v)
                else: graph.set_edge(u, v, weight)
                st.session_state.revision += 1
                st.rerun()
            except ValueError as error:
                st.error(str(error))
        if st.button('Restore original graph'):
            st.session_state.graph, st.session_state.coordinates = load_campus()
            st.session_state.revision += 1
            st.rerun()
    st.caption(f'Graph revision {st.session_state.revision}')

st.markdown('<div class="eyebrow">SMART CAMPUS / ALGORITHM STUDIO</div>', unsafe_allow_html=True)
st.title('Smart Campus Navigator')
st.caption('Interactive Graph Algorithm Visualizer and Route Optimizer')
st.divider()


def show_graph(edges=(), visited=(), current=None):
    st.plotly_chart(campus_figure(graph, coordinates, edges, visited, current), width='stretch')
    st.caption('Teal edges: selected route/tree · Teal nodes: visited · Amber: current step. Edge labels are metres. Local illustrative coordinates; not a real university.')


def selectors(prefix):
    a, b = st.columns(2)
    source = a.selectbox('Source', graph.nodes, index=graph.nodes.index('Main Gate'), key=prefix+'source')
    target = b.selectbox('Destination', graph.nodes, index=graph.nodes.index('Hostel'), key=prefix+'target')
    return source, target


def step_viewer(steps, key):
    """Explicit controls avoid timers and keep live demonstrations reliable."""
    if not steps:
        st.info('No steps for this input.')
        return
    key = f'{key}_{st.session_state.revision}'
    if key not in st.session_state:
        st.session_state[key] = 0
    st.session_state[key] = min(st.session_state[key], len(steps)-1)
    def move(delta=None):
        st.session_state[key] = 0 if delta is None else max(0, min(len(steps)-1, st.session_state[key]+delta))
    left, middle, right = st.columns([1,1,1])
    left.button('← Previous', key=key+'prev', on_click=move, args=(-1,), disabled=st.session_state[key]==0)
    middle.button('Next →', key=key+'next', on_click=move, args=(1,), disabled=st.session_state[key]==len(steps)-1)
    right.button('Reset steps', key=key+'reset', on_click=move)
    index = st.session_state[key]
    st.progress((index+1)/len(steps), text=f'Step {index+1} / {len(steps)}')
    step = steps[index]
    st.info(step['message'])
    prefix = steps[:index+1]
    visited = [e['node'] for e in prefix if e['kind'] in ('visit','settle','root','accept') and 'node' in e]
    edges = [e['edge'] for e in prefix if 'edge' in e and e['kind'] in ('accept','visit','discover')]
    if step['kind'] == 'relax': edges = [step['edge']]
    show_graph(edges, visited, step.get('node'))
    with st.expander('Structured history events'):
        st.json(steps[:index+1])


if page == 'Dashboard':
    st.subheader('A clearer way across campus')
    st.write('Students need short walking routes. Administrators need an economical connected pathway network. Explore both questions on the same ten-location graph.')
    cols = st.columns(4)
    for column, title, value in zip(cols, ['Locations','Walkable paths','Algorithms','Edge weights'], [len(graph.nodes), len(graph.edges()), 6, 'Metres']):
        column.metric(title, value)
    show_graph()
    a, b = st.columns(2)
    a.markdown('#### Find a route\nDijkstra minimizes the sum of walking distances between two locations. Floyd-Warshall answers every source/destination pair.')
    b.markdown('#### Connect the campus\nPrim and Kruskal minimize the total length of the whole connecting network. A tree route can be longer than a shortest route.')
    st.markdown('#### Explore the structure\nBFS explores in layers. DFS follows a branch and backtracks. Both reveal which locations are reachable.')
    st.caption('Available: BFS · DFS · Dijkstra · Floyd-Warshall · Prim · Kruskal. Use the sidebar to edit or restore paths.')
elif page == 'Campus Route Finder':
    st.subheader('Campus Route Finder')
    source, target = selectors('route')
    result = dijkstra(graph, source, target)
    if result.path:
        a,b,c = st.columns(3)
        a.metric('Shortest distance', f'{result.distance:g} m')
        b.metric('Paths on route', len(result.path)-1)
        c.metric('Nodes settled', len(result.order))
        st.success(' → '.join(result.path))
    else: st.warning('Destination unreachable: there is no path between these locations.')
    show_graph(list(zip(result.path,result.path[1:])), result.path)
    st.write(CORRECTNESS['Dijkstra'])
    st.caption('This implementation completes all reachable single-source distances; “Nodes settled” counts that complete search, not only the destination search prefix.')
    with st.expander('Step-by-step Dijkstra', expanded=False):
        step_viewer(result.steps, f'route_{source}_{target}')
    st.dataframe([{'Location': n, 'Distance (m)': '∞' if math.isinf(d) else f'{d:g}'} for n,d in result.distances.items()], hide_index=True, width='stretch')
elif page == 'Graph Exploration':
    st.subheader('Graph Exploration')
    name = st.selectbox('Traversal', ['BFS','DFS'])
    source = st.selectbox('Starting location', graph.nodes, index=graph.nodes.index('Main Gate'))
    result = (bfs if name == 'BFS' else dfs)(graph, source)
    st.write('**Traversal order:** ' + ' → '.join(result.order))
    st.metric('Locations reachable', f'{len(result.order)} / {len(graph.nodes)}')
    if not result.connected: st.warning('The graph is disconnected. This traversal covers only the starting component.')
    st.write('BFS uses a FIFO queue to visit layers. DFS uses a stack of iterator frames to follow branches and backtrack. Alphabetical neighbors make both reproducible.')
    st.info('BFS minimizes the number of edges in an unweighted graph. It does not necessarily minimize walking distance in this weighted graph.')
    step_viewer(result.steps, f'explore_{name}_{source}')
elif page == 'Campus Network Optimizer':
    st.subheader('Campus Network Optimizer')
    name = st.selectbox('MST algorithm', ['Prim','Kruskal'])
    result = prim(graph, 'Main Gate') if name == 'Prim' else kruskal(graph)
    if not result.connected: st.warning('Disconnected graph: a full spanning tree cannot be constructed. Showing a minimum spanning forest across all components.')
    a,b = st.columns(2)
    a.metric('Total construction distance', f'{result.total:g} m')
    b.metric('Selected edges', len(result.edges))
    show_graph(result.edges)
    st.dataframe([{'Order':i+1,'From':u,'To':v,'Length (m)':w} for i,(u,v,w) in enumerate(result.edges)], hide_index=True, width='stretch')
    st.write(CORRECTNESS[name])
    st.info('Both algorithms attain the same minimum total weight. Equal-weight choices can produce different optimal trees. This optimizes total network length, not every individual journey; construction cost is assumed proportional to distance.')
    with st.expander('Inspect selection steps'): step_viewer(result.steps, 'mst_'+name)
elif page == 'All-Pairs Route Analyzer':
    st.subheader('All-Pairs Route Analyzer')
    result = floyd_warshall(graph)
    st.latex(r'd[i,j] \leftarrow \min(d[i,j],\ d[i,k]+d[k,j])')
    st.write('Allow one more intermediate location k at each outer iteration. Ask whether going through k improves each source-to-destination distance.')
    # HTML-free labelled table: Streamlit bundles the display assets locally.
    st.dataframe([{'From / To':u, **{v:'∞' if math.isinf(result.distances[u][v]) else f'{result.distances[u][v]:g}' for v in graph.nodes}} for u in graph.nodes], hide_index=True, width='stretch')
    st.caption('Distance matrix in metres. ∞ means unreachable; diagonal entries are zero.')
    source,target = selectors('allpairs')
    path = result.path(source,target)
    if path:
        st.success(f'{result.distances[source][target]:g} m · ' + ' → '.join(path))
    else: st.warning('Destination unreachable.')
    show_graph(list(zip(path,path[1:])), path)
    with st.expander('Intermediate-node update steps'): step_viewer(result.steps, 'floyd')
else:
    st.subheader('Algorithm Comparison & Learning Lab')
    st.write('Big O describes how resource use grows as input grows. O(V + E) scales with locations and paths; doubling V makes a cubic V³ term about eight times as large. It is a growth bound, not a stopwatch prediction.')
    st.dataframe(ALGORITHMS, hide_index=True, width='stretch')
    st.caption(COMPLEXITY_NOTE)
    name = st.selectbox('Study an algorithm', [row['name'] for row in ALGORITHMS])
    st.code(PSEUDOCODE[name], language='text')
    st.write(CORRECTNESS[name])
    st.markdown('#### Small worked example')
    st.write('Triangle: A—B = 2, B—C = 1, A—C = 5. From A, BFS discovers B and C in one hop. Dijkstra improves C from 5 to 3 through B. An MST selects B—C and A—B for total 3; the direct A—C edge would create a cycle.')
    runners = {'BFS':lambda:bfs(graph,'Main Gate'), 'DFS':lambda:dfs(graph,'Main Gate'), 'Dijkstra':lambda:dijkstra(graph,'Main Gate','Hostel'), 'Floyd-Warshall':lambda:floyd_warshall(graph), 'Prim':lambda:prim(graph,'Main Gate'), 'Kruskal':lambda:kruskal(graph)}
    step_viewer(runners[name]().steps, 'lab_'+name)
    st.markdown('#### Experimental timing')
    st.caption('Same generated graphs; repeated perf_counter measurements with history disabled. Compare BFS with DFS and Prim with Kruskal; shortest-path workloads differ (one source versus all pairs). No overall winner is implied.')
    if st.button('Run small benchmark'):
        from campus.benchmark import measure
        with st.spinner('Measuring 12, 24 and 48 vertices…'):
            rows = measure()
        st.session_state.benchmark = rows
    if 'benchmark' in st.session_state:
        rows = st.session_state.benchmark
        st.dataframe(rows, hide_index=True)
        fig = go.Figure()
        for algorithm in [r['name'] for r in ALGORITHMS]:
            series=[r for r in rows if r['Algorithm']==algorithm]
            fig.add_trace(go.Scatter(x=[r['V'] for r in series],y=[r['Median ms'] for r in series],name=algorithm,mode='lines+markers'))
        fig.update_layout(xaxis_title='Vertices',yaxis_title='Median milliseconds (experimental)',template='plotly_dark',height=350)
        st.plotly_chart(fig,width='stretch')
        st.caption('Small timings are sensitive to machine load and Python overhead. They do not prove theoretical complexity. See docs/benchmark_results.csv for the recorded submission run.')
