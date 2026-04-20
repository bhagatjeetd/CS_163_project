import dash
from dash import html

dash.register_page(__name__, path="/", name="Home", order=0)

CARD_STYLE = {
    "padding": "20px",
    "borderRadius": "12px",
    "backgroundColor": "white",
    "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
    "marginBottom": "20px"
}

layout = html.Div([
    html.Div([
        html.H2("Grocery Price Analysis"),
        html.P("Group ID: 9"),
        html.P("Members: Benny Chen, Bhagatjeet Dhillon")],
        style=CARD_STYLE),
    html.Div([
        html.H3("Project Summary"),
        html.P("blah blah blah")],
        style=CARD_STYLE),
    html.Div([
        html.H3("Broader Impacts"),
        html.P("blah blah blah")],
        style=CARD_STYLE),
    html.Div([
        html.H3("Data Sources"),
        html.P("blah blah blah")],
        style=CARD_STYLE)
    ],
    style={"padding": "20px", "backgroundColor": "#f4f6f9"}
)