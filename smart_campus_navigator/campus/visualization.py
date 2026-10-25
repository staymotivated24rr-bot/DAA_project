"""Plotly uses local coordinates; the diagram is illustrative, not a real map."""
import plotly.graph_objects as go

NAVY = '#0b1220'
TEAL = '#35d9c0'


def campus_figure(graph, coordinates, highlighted=(), visited=(), current=None):
    selected = {frozenset(edge[:2]) for edge in highlighted}
    fig = go.Figure()
    for u, v, weight in graph.edges():
        x1, y1 = coordinates[u]
        x2, y2 = coordinates[v]
        active = frozenset((u, v)) in selected
        fig.add_trace(go.Scatter(x=[x1, x2], y=[y1, y2], mode='lines',
            line=dict(color=TEAL if active else '#42526d', width=5 if active else 2),
            hovertemplate=f'{u} ↔ {v}<br>{weight:g} m<extra></extra>', showlegend=False))
        fig.add_annotation(x=(x1+x2)/2, y=(y1+y2)/2, text=f'{weight:g}', showarrow=False,
            font=dict(size=11, color='#d8e2f0'), bgcolor=NAVY, borderpad=2)
    nodes = graph.nodes
    colors = ['#fbbf24' if n == current else TEAL if n in visited else '#6b9fff' for n in nodes]
    fig.add_trace(go.Scatter(x=[coordinates[n][0] for n in nodes], y=[coordinates[n][1] for n in nodes],
        mode='markers+text', text=list(nodes), textposition='top center',
        textfont=dict(size=12, color='#edf3ff'), marker=dict(size=17, color=colors, line=dict(width=2, color=NAVY)),
        hovertemplate='%{text}<extra></extra>', showlegend=False))
    fig.update_layout(height=540, paper_bgcolor=NAVY, plot_bgcolor=NAVY,
        margin=dict(l=35, r=45, t=35, b=30), font=dict(color='#edf3ff'),
        xaxis=dict(visible=False, range=[-100, 740]),
        yaxis=dict(visible=False, range=[-55, 545], scaleanchor='x', scaleratio=1), dragmode='pan')
    return fig
