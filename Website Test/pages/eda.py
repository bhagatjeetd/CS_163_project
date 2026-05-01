import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
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

fao = pd.read_csv('https://raw.githubusercontent.com/bhagatjeetd/CS_163_project/refs/heads/main/fao.csv')
hpai = pd.read_csv('https://raw.githubusercontent.com/bhagatjeetd/CS_163_project/refs/heads/main/hpai.csv')

layout = html.Div([
    html.Div([
        html.H3("Dataset Preview"),
        html.P("FAO"),
        dash_table.DataTable(data=fao.to_dict('records'), page_size=6),
        html.P(),
        html.P("Birds Affected"),
        dash_table.DataTable(data=hpai.to_dict('records'), page_size=6)
    ],style=CARD_STYLE),
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
    ], style=CARD_STYLE),
    html.Div([
        html.H3("Distributions"),
        html.Div([
            html.Div([
                html.Img(src="/assets/food_group_price_distribution.png", style={"wdith": "100%"}),
                html.P("Boxplot of price distribution by food group"),
            ], style={"width": "48%"}),
            html.Div([
                html.Img(src="/assets/overall_price_distribution.png", style={"wdith": "100%"}),
                html.P("Histogram of overall price distribution"),
            ], style={"width": "48%"})
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "gap": "4%"
        })
    ], style=CARD_STYLE),
    html.Div([
        html.H3("Egg Price vs Affected Bird Trend"),
        html.Img(src="/assets/eggPrice_vs_affected.png", style={"wdith": "100%"}),
        html.P("Overlaying trends showing egg price and affected bird count changes"),
    ], style=CARD_STYLE),
    html.Div([
        html.H3("Insights"),
        html.Li("Dairy and Protein products have the largest variability in their prices.", style={"padding": "10px"}),
        html.Li("Majority of prices lie between 4 to 6, with right-skeweness and a notable max greater than 14.", style={"padding": "10px"}),
        html.Li("When the amount of birds affected change, there is a small time lag until the egg prices change accordingly.", style={"padding": "10px"})
    ], style=CARD_STYLE),
],
    style={"padding": "20px", "backgroundColor": "#f4f6f9"}
)