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
        html.P("Based on the grocery prices provided by FAO and the HPAI detections by USDA, this project aims to analyze and predict how grocery price changes with a focus on chicken and eggs based on event severity.")],
        style=CARD_STYLE),
    html.Div([
        html.H3("Broader Impacts"),
        html.Li("Budget Planning: Provide info to help consumers create better grocery budgets.", style={"padding": "10px"}),
        html.Li("Understanding External Factors: Examine how different severity levels could influence prices", style={"padding": "10px"}),
        html.Li("Future Planning: Based on severity, predict how prices may change in the future.", style={"padding": "10px"})],
        style=CARD_STYLE),
    html.Div([
        html.H3("Data Sources"),
        html.A("FAO Dataset", href="https://data.apps.fao.org/catalog/dataset/food-prices-monitor/resource/2bca62cf-13c0-4421-9568-2b68afea8fd2", target="_blank"),
        html.Br(),
        html.A("HPAI Detections", href="https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks", target="_blank")],
        style=CARD_STYLE)
    ],
    style={"padding": "20px", "backgroundColor": "#f4f6f9"}
)