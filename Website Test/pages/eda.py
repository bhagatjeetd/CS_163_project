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
        html.H3("Dataset Preview"),
        html.P("FAO Dataset"),
        html.Img(src="/assets/fao_preview_original.png", style={"wdith": "100%"}),
        html.P(),
        html.P("Birds Affected"),
        html.Img(src="/assets/hpai_preview_original.png", style={"wdith": "50%"}),],
        style=CARD_STYLE),
    html.Div([
        html.H3("Price Statistics"),
        html.Div([
            html.Div([
                html.Img(src="/assets/product_price_stats.png", style={"wdith": "100%"}),
                html.P("Individual Products")
            ], style={"width": "48%"}),
            html.Div([
                html.Img(src="/assets/food_group_stats.png", style={"wdith": "100%"}),
                html.P("Food Group")
            ], style={"width": "48%"})
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "gap": "4%"
        })
    ], style=CARD_STYLE)
    ],
    style={"padding": "20px", "backgroundColor": "#f4f6f9"}
)