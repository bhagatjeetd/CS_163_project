import dash
from dash import html

dash.register_page(__name__, name="Analysis", order=2)

layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("Page 3"),
        html.P("Content coming soon...")
    ]
)