import dash
from dash import html

dash.register_page(__name__, name="Analytical Methods", order=2)

CARD_STYLE = {
    "padding": "20px",
    "borderRadius": "12px",
    "backgroundColor": "white",
    "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
    "marginBottom": "20px"
}

layout = html.Div(
    style={"padding": "20px", "backgroundColor": "#f4f6f9"},
    children=[
        html.Div(style=CARD_STYLE, children=[
            html.H2("Analytical Methods"),
            html.Ul([
                html.Li("Descriptive statistics by product and food group"),
                html.Li("Monthly aggregation and trend analysis"),
                html.Li("Correlation analysis on monthly averages (co-movement)"),
                html.Li("Event alignment: Birds Affected vs Egg prices"),
                html.Li("Severity buckets using quantiles of Birds Affected"),
                html.Li("Regression forecasting for food-group average prices")
            ])
        ]),
        html.Div(style=CARD_STYLE, children=[
            html.H3("References"),
            html.Ul([
                html.Li("FAO Daily Food Prices Monitor dataset"),
                html.Li("USDA APHIS HPAI detections dataset"),
                html.Li("USDA ERS Food Price Outlook"),
                html.Li("BLS CPI supplemental files")
            ])
        ])
    ]
)