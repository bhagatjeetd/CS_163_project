import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

dash.register_page(__name__, name="EDA", order=1)

# Example dataset
CARD_STYLE = {
    "padding": "20px",
    "borderRadius": "12px",
    "backgroundColor": "white",
    "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
    "marginBottom": "20px"
}

layout = html.Div([
    html.Div([
        html.H3("Dataset Summary"),
        html.P("FAO Dataset"),
        html.P("Birds Affected")],
        style=CARD_STYLE),
    html.Div([
        html.Div('Overall Price Summary',
                 style={'flex': '1', 'paddingRight': '10px'}
                 ),
                 
    ])
    ],
    style={"padding": "20px", "backgroundColor": "#f4f6f9"}
)