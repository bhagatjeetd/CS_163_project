import dash_bootstrap_components as dbc # additional package
from dash_bootstrap_templates import load_figure_template # additional package
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash

# Incorporate data
#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
fao = pd.read_csv('https://raw.githubusercontent.com/bhagatjeetd/CS_163_project/refs/heads/main/fao.csv')
hpai = pd.read_csv('https://raw.githubusercontent.com/bhagatjeetd/CS_163_project/refs/heads/main/hpai.csv')

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LITERA])

# load_figure_template('DARKLY')

# App layout
navbar = html.Div(
    style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "padding": "10px 20px",
        "backgroundColor": "#1f2c56",
        "color": "white"
    },
    children=[
        # Title (left)
        html.H2("CS163 Project", style={"margin": "0"}),

        # Navigation links (right)
        html.Div(
            [dcc.Link(
                page["name"],
                href=page["path"],
                style={
                    "marginLeft": "20px",
                    "color": "white",
                    "textDecoration": "none",
                    "fontWeight": "bold"
                }
            )
            for page in sorted(dash.page_registry.values(), 
                                key=lambda x: x.get('order', 10))
            ]
        )
    ]
)

app.layout = html.Div([
    navbar,
    dash.page_container
])


# Run the app
if __name__ == '__main__':
    app.run(debug=True)