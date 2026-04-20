import dash
from dash import html

dash.register_page(__name__, name="Model", order=3)

layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("Page 4"),
        html.P("Content coming soon...")
    ]
)