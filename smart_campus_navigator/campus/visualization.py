"""Shared Plotly canvas with algorithm-specific overlays and short mobile labels."""
from copy import deepcopy
import plotly.graph_objects as go

NAVY = '#0b1220'
TEAL = '#35d9c0'
AMBER = '#fbbf24'
REJECTED = '#fb7185'
FRONTIER = '#c4b5fd'
SHORT_NAMES = {'Main Gate':'Gate', 'Administrative Block':'Admin', 'Academic Block':'Academic',
    'Laboratory':'Lab', 'Medical Centre':'Medical', 'Sports Ground':'Sports'}


def base_figure(graph, coordinates):
    """Build unchanged paths/labels once for an active execution."""
    fig = go.Figure()
    x, y, hover = [], [], []
    for u, v, weight in graph.edges():
        x1, y1 = coordinates[u]
        x2, y2 = coordinates[v]
        x.extend([x1, x2, None]); y.extend([y1, y2, None])
        hover.extend([f'{u} ↔ {v}<br>{weight:g} m']*3)
        fig.add_annotation(x=(x1+x2)/2, y=(y1+y2)/2, text=f'{weight:g}', showarrow=False,
            font=dict(size=11, color='#e2eaf7'), bgcolor=NAVY, borderpad=2)
    fig.add_trace(go.Scatter(x=x, y=y, text=hover, mode='lines', name='Available paths',
        line=dict(color='#64748b', width=2), hovertemplate='%{text}<extra></extra>', showlegend=False))
    fig.update_layout(height=470, autosize=True, paper_bgcolor=NAVY, plot_bgcolor=NAVY,
        margin=dict(l=15, r=15, t=30, b=30), font=dict(color='#edf3ff'),
        xaxis=dict(visible=False, range=[-100,740], fixedrange=False),
        yaxis=dict(visible=False, range=[-75,550], fixedrange=False),
        dragmode='pan', uirevision='campus-layout')
    return fig.to_plotly_json()


def campus_figure(graph, coordinates, highlighted=(), visited=(), current=None,
                  *, frontier=(), rejected=(), current_edges=(), base=None):
    fig = go.Figure(deepcopy(base) if base is not None else base_figure(graph, coordinates))
    for edges, color, name, dash in [(highlighted,TEAL,'Selected edges','solid'),
                                    (rejected,REJECTED,'Rejected cycle edges','dash'),
                                    (current_edges,AMBER,'Currently examined','solid')]:
        x, y, hover = [], [], []
        for u,v in sorted({tuple(sorted(edge[:2])) for edge in edges}):
            if v not in graph.adj[u]:
                raise ValueError(f'Cannot highlight a missing path: {u} - {v}')
            x.extend([coordinates[u][0],coordinates[v][0],None])
            y.extend([coordinates[u][1],coordinates[v][1],None])
            hover.extend([f'{u} ↔ {v}<br>{graph.adj[u][v]:g} m · {name}']*3)
        if x:
            fig.add_trace(go.Scatter(x=x,y=y,text=hover,mode='lines',name=name,
                line=dict(color=color,width=4,dash=dash),hovertemplate='%{text}<extra></extra>',showlegend=False))
    nodes = graph.nodes
    colors = [AMBER if n == current else TEAL if n in visited else FRONTIER if n in frontier else '#8caeef' for n in nodes]
    fig.add_trace(go.Scatter(x=[coordinates[n][0] for n in nodes],y=[coordinates[n][1] for n in nodes],
        mode='markers+text',text=[SHORT_NAMES.get(n,n) for n in nodes],customdata=list(nodes),textposition='top center',
        textfont=dict(size=12,color='#edf3ff'),marker=dict(size=15,color=colors,line=dict(width=2,color=NAVY)),
        hovertemplate='%{customdata}<extra></extra>',name='Locations',showlegend=False))
    return fig
