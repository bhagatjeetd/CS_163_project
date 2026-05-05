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

layout = html.Div(
    style={"padding": "20px", "backgroundColor": "#f4f6f9"},
    children=[
        html.Div(style=CARD_STYLE, children=[
            html.H2("Food Price Inflation Analysis"),
            html.P("Group ID: 9"),
            html.P("Members: Benny Chen, Bhagatjeet Dhillon"),
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Project Summary"),
            html.P(
                "This project uses machine learning to analyze grocery prices and past events to better understand how events influence "
                "the price of food, and to predict how prices may change while accounting for the severity of possible future events."
            ),
            html.P(
                "The project uses FAO food price data from February 9, 2020 to February 1, 2026 (United States subset). "
                "Fourteen food items are analyzed individually and also grouped by food category."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Project Objective"),
            html.P(
                "Help consumers create a better grocery budget by analyzing how events (for example bird flu or Covid-19) influence "
                "food prices and by providing a reasonable idea of how prices may change if similar events occur again."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Project Questions"),
            html.Ul([
                html.Li("Which food group had the greatest overall increase in price?"),
                html.Li("What will be the average price of each food group three years into the future?"),
                html.Li("What is the interval of percent price change for each severity level?"),
                html.Li("How quickly do prices change after an event, and how long do effects last per category?"),
                html.Li("Are large price changes concentrated in the same months, and do shocks amplify normal seasonal patterns?"),
                html.Li("Which food category shows the most short-term changes versus long-term effects after an event?")
            ])
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Broader Impacts"),
            html.Ul([
                html.Li("Budget planning support for consumers."),
                html.Li("Understanding how event severity relates to short-term vs long-term price changes."),
                html.Li("Improved planning for organizations and businesses that manage food purchasing and distribution.")
            ])
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Data Sources"),
            html.Div([
                html.A(
                    "FAO Daily Food Prices Monitor (main)",
                    href="https://data.apps.fao.org/catalog/dataset/food-prices-monitor/resource/2bca62cf-13c0-4421-9568-2b68afea8fd2",
                    target="_blank"
                ),
                html.Br(),
                html.A(
                    "USDA APHIS HPAI detections (supplemental)",
                    href="https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks",
                    target="_blank"
                ),
                html.Br(),
                html.A(
                    "USDA ERS Food Price Outlook (supplemental)",
                    href="https://www.ers.usda.gov/data-products/food-price-outlook/summary-findings/",
                    target="_blank"
                ),
                html.Br(),
                html.A(
                    "BLS CPI supplemental files (supplemental)",
                    href="https://www.bls.gov/cpi/tables/supplemental-files/",
                    target="_blank"
                ),
                html.Br(),
                html.A(
                    "HDX Producer prices dataset for USA (supplemental)",
                    href="https://data.humdata.org/dataset/faostat-food-prices-for-united-states-of-america/resource/e81ed039-0dbf-4a1e-97a8-d23d04cbd155",
                    target="_blank"
                ),
            ])
        ]),
    ]
)