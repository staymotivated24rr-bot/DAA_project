"""Only this fragment reruns when a playback control is clicked."""
from html import escape
from math import isinf
import streamlit as st
from campus.playback import replay
from campus.visualization import base_figure, campus_figure


def number(value):
    return '∞' if isinf(value) else f'{value:g}'


def matrix_html(nodes, matrix, comparison=None):
    """A horizontally scrollable, labelled table; only the current cells are colored."""
    cells = {}
    if comparison and comparison['kind'] == 'compare':
        i,j,k = (comparison[key] for key in ('i','j','k'))
        cells[(i,k)] = cells[(k,j)] = ('operand','Operand through K')
        cells[(i,j)] = ('improved' if comparison['improved'] else 'inspected','Compared distance I → J')
    head = ''.join(f'<th scope="col" title="{escape(n)}">{index+1}</th>' for index,n in enumerate(nodes))
    rows = []
    for index,u in enumerate(nodes):
        values = []
        for v in nodes:
            category,description = cells.get((u,v),('','Distance'))
            values.append(f'<td class="{category}" title="{escape(description+": "+u+" → "+v)}">{number(matrix[u][v])}</td>')
        rows.append(f'<tr><th scope="row">{index+1}. {escape(u)}</th>{"".join(values)}</tr>')
    return '''<style>
.matrix-scroll{overflow-x:auto;max-width:100%;border:1px solid #42526d;border-radius:8px}
.matrix{border-collapse:collapse;background:#0b1220;color:#edf3ff;font-size:14px;min-width:620px;width:100%}
.matrix td,.matrix th{padding:7px 9px;border:1px solid #334155;text-align:center}
.matrix th{background:#16263e}.matrix th[scope=row]{text-align:left;white-space:nowrap;position:sticky;left:0;z-index:1}
.matrix caption{caption-side:top;text-align:left;padding:8px;color:#e2eaf7}
.matrix .operand{background:#234375;color:#fff}.matrix .inspected{background:#785200;color:#fff}
.matrix .improved{background:#126457;color:#fff;font-weight:700}
</style><div class="matrix-scroll"><table class="matrix" aria-label="Floyd-Warshall replay distances in metres">
<caption>Replay distance matrix (metres). Column numbers match the numbered locations.</caption>
<thead><tr><th scope="col">From / To</th>'''+head+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def move_current(signature, delta=None):
    """Ignore a late callback belonging to a replaced execution."""
    execution = st.session_state.get('_execution')
    if execution is not None and execution.signature == signature:
        execution.move(delta)


@st.fragment
def step_viewer(graph, coordinates, execution):
    steps = execution.result.steps
    if not steps:
        st.info('No steps for this input.')
        return
    left, middle, right = st.columns(3)
    left.button('← Previous',key='playback_previous',on_click=move_current,args=(execution.signature,-1),disabled=execution.index==0)
    middle.button('Next →',key='playback_next',on_click=move_current,args=(execution.signature,1),disabled=execution.index==len(steps)-1)
    right.button('Reset steps',key='playback_reset',on_click=move_current,args=(execution.signature,None))
    index = execution.index
    st.progress((index+1)/len(steps),text=f'Step {index+1} / {len(steps)}')
    step = steps[index]
    st.info(step['message'])
    frame = replay(graph,execution.algorithm,steps,index)
    if execution.algorithm == 'Floyd-Warshall':
        if step['kind']=='compare':
            st.write(f'**K (intermediate):** {step["k"]} · **I (source):** {step["i"]} · **J (destination):** {step["j"]}')
            st.write(f'Before: **{number(step["before"])} m** · Via K: **{number(step["left"])} + {number(step["right"])} = {number(step["candidate"])} m** · '+('**Improved**' if step['improved'] else '**Keep previous distance**'))
        st.html(matrix_html(graph.nodes,frame.matrix,step))
        st.caption('Blue cells: operands d[I,K] and d[K,J] · Amber: compared cell d[I,J] · Teal: improved value. The table reflects this step, including backwards navigation.')
    elif execution.algorithm == 'BFS':
        st.caption('Discovered but not visited: '+(', '.join(sorted(frame.frontier)) or 'none'))
    elif execution.algorithm == 'DFS':
        st.caption('Active stack: '+(' → '.join(frame.active) or 'empty (exploration complete)'))
    elif execution.algorithm == 'Dijkstra':
        st.dataframe([{'Location':node,'Distance (m)':number(value),'State':'settled' if node in frame.visited else 'tentative'} for node,value in frame.distances.items()],hide_index=True,width='stretch')
    if execution.base_figure is None:
        execution.base_figure = base_figure(graph,coordinates)
    fig = campus_figure(graph,coordinates,frame.selected,frame.visited,frame.current,
        frontier=frame.frontier,rejected=frame.rejected,current_edges=frame.current_edges,base=execution.base_figure)
    st.plotly_chart(fig,width='stretch',key='playback_chart',config={'displaylogo':False,'responsive':True})
    st.caption('Teal: selected edges / visited nodes · Lavender: discovered or tentative nodes · Amber: current node / examined edge · Rose dashed: rejected cycle edge. Muted paths remain available. Hover for full location names.')
    with st.expander('Current structured event'):
        st.json(step)
