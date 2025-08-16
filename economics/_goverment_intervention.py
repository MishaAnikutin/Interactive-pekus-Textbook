import numpy as np
import sympy as sp

import dash
from dash import dcc, html, Input, Output

import plotly.io as pio
import plotly.graph_objects as go


pio.templates.default = "plotly_white"
goverment_intervention = dash.Dash(__name__)

P, Q, t = sp.symbols('P Q t')
Q_range = np.linspace(0, 100, 500)

Qd = 100 - P
Qs = P

font_style = {
    'fontFamily': 'Helvetica, Arial, sans-serif'
}

goverment_intervention.layout = html.Div(style={**font_style}, children=[
    html.H2("Потоварный налог на рынке СК"),
    
    dcc.Graph(id='market-graph'),
    html.Div([
        html.Label("Размер налога t:", style={'display': 'inline-block', 'verticalAlign': 'middle', 'marginRight': '10px'}),
        html.Div(
            dcc.Slider(
                id='tax-slider',
                min=0,
                max=100,
                step=1,
                value=0,
                marks={i: str(i) for i in range(0, 101, 5)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            style={'display': 'inline-block', 'width': '80%', 'verticalAlign': 'middle'}
        )
    ], style={'display': 'flex', 'alignItems': 'center', 'margin': '20px'}),
    
    html.Div(id='market-stats', style={'margin': '20px', 'fontSize': '16px'})
])

@goverment_intervention.callback(
    [Output('market-graph', 'figure'),
     Output('market-stats', 'children')],
    [Input('tax-slider', 'value')]
)
def update_graph(t_value):
    Pe_initial = float(sp.solve(Qd - Qs, P)[0])
    Qe_initial = float(Qd.subs(P, Pe_initial))
    
    Qs_tax = P - t 
    Pe_tax = float(sp.solve(Qd - Qs_tax.subs(t, t_value), P)[0])
    Qe_tax = float(Qd.subs(P, Pe_tax))
    Ps_tax = Pe_tax - t_value  
    
    CS = 0.5 * (100 - Pe_tax) * Qe_tax
    PS = 0.5 * Ps_tax * Qe_tax
    DWL = 0.5 * (Pe_tax - Ps_tax) * (Qe_initial - Qe_tax)
    
    
    p_demand = 100 - Q_range
    p_supply_initial = Q_range
    p_supply_tax = Q_range + t_value
    
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Q_range, y=p_demand, mode='lines', name='Спрос (D)',
                            line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=Q_range, y=p_supply_initial, mode='lines', name='Предложение (S)',
                            line=dict(color='green', width=2)))
    fig.add_trace(go.Scatter(x=Q_range, y=p_supply_tax, mode='lines', name=f'Предложение после налога',
                            line=dict(color='red', width=2, dash='dash')))
    
    fig.add_shape(type="line", x0=0, y0=Pe_tax, x1=Qe_tax, y1=Pe_tax,
                  line=dict(color="gray", width=1, dash="dot"))
    fig.add_shape(type="line", x0=Qe_tax, y0=0, x1=Qe_tax, y1=Pe_tax,
                  line=dict(color="gray", width=1, dash="dot"))
    
    fig.add_trace(go.Scatter(
        x=[0, Qe_tax, 0], 
        y=[Pe_tax, Pe_tax, 100],
        fill='toself',
        fillcolor='rgba(0, 100, 255, 0.2)',
        line=dict(color='rgba(0, 100, 255, 0.5)'),
        name='CS (Излишек потребителя)'
    ))
    
    fig.add_trace(go.Scatter(
        x=[0, Qe_tax, 0], 
        y=[0, Ps_tax, Ps_tax],
        fill='toself',
        fillcolor='rgba(0, 200, 0, 0.2)',
        line=dict(color='rgba(0, 200, 0, 0.5)'),
        name='PS (Излишек производителя)'
    ))
    
    fig.add_trace(go.Scatter(
        x=[Qe_tax, Qe_initial, Qe_tax], 
        y=[Pe_tax, Pe_initial, Ps_tax],
        fill='toself',
        fillcolor='rgba(0, 0, 0, 0.2)',
        line=dict(color='rgba(0, 0, 0, 0.5)'),
        name='DWL (Потери мертвого груза)'
    ))
    
    fig.update_layout(
        xaxis_title='Количество (Q)',
        yaxis_title='Цена (P)',
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, 100]),
        showlegend=True
    )
    
    stats = html.Div([
        html.P(f"Pd = {Pe_tax:.2f}, Ps = {Ps_tax:.2f}, Qe = {Qe_tax:.2f}"),
        html.P(f"CS = {CS:.2f}, PS = {PS:.2f}, DWL = {DWL:.2f}, Tx = {t_value * Qe_tax:.2f}")
    ])
    
    return fig, stats