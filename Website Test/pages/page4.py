import dash
from dash import html, dcc, callback, Output, Input, State
import requests
import json
import os

dash.register_page(__name__, name="Forecast (Cloud Run)", order=4)

CARD_STYLE = {
    "padding": "20px",
    "borderRadius": "12px",
    "backgroundColor": "white",
    "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
    "marginBottom": "20px"
}

PAGE_STYLE = {"padding": "20px", "backgroundColor": "#f4f6f9"}

FOOD_GROUPS = ["Dairy", "Fruit", "Grain", "Protein", "Vegetable"]
SEVERITY_LEVELS = ["Very Low", "Low", "Medium", "High"]

layout = html.Div(
    style=PAGE_STYLE,
    children=[
        html.Div(style=CARD_STYLE, children=[
            html.H2("Food Group Price Forecast (Cloud Run)"),
            html.P(
                "Forecast the average price for a selected food group under a selected event severity level and forecast horizon."
            ),
            html.P(
                "Inputs: food groups and severity levels. Output is a predicted average price."
            ),
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Prediction Inputs"),

            html.Label("Food group"),
            dcc.Dropdown(
                id="fg",
                options=[{"label": x, "value": x} for x in FOOD_GROUPS],
                value="Dairy",
                clearable=False
            ),

            html.Br(),

            html.Label("Severity level"),
            dcc.Dropdown(
                id="sev",
                options=[{"label": x, "value": x} for x in SEVERITY_LEVELS],
                value="High",
                clearable=False
            ),

            html.Br(),

            html.Label("Forecast horizon (months)"),
            dcc.Input(
                id="horizon",
                type="number",
                value=36,
                min=1,
                step=1
            ),

            html.Br(),
            html.Br(),

            html.Button("Predict", id="btn_predict", n_clicks=0),

            html.Br(),
            html.Br(),

            html.Div(id="pred_out", style={"whiteSpace": "pre-wrap"})
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("How to interpret this output"),
            html.Ul([
                html.Li("Food group controls which category is being forecast (Dairy, Fruit, Grain, Protein, Vegetable)."),
                html.Li("Severity level represents the assumed event intensity (Very Low to High)."),
                html.Li("Horizon is how many months ahead the forecast is produced (36 months = 3 years)."),
                html.Li("The returned predicted price is intended as an estimated average price for that category at the chosen horizon.")
            ])
        ])
    ]
)

@callback(
    Output("pred_out", "children"),
    Input("btn_predict", "n_clicks"),
    State("fg", "value"),
    State("sev", "value"),
    State("horizon", "value"),
)
def call_inference(n_clicks, fg, sev, horizon):
    if n_clicks == 0:
        return ""

    infer_url = os.environ.get("INFER_URL", "").strip()
    if not infer_url:
        return "INFER_URL is not set in app.yaml."

    if horizon is None:
        return "Horizon is required."

    payload = {
        "food_group": fg,
        "severity_level": sev,
        "horizon_months": int(horizon)
    }

    try:
        r = requests.post(
            infer_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=30
        )
    except Exception as e:
        return f"Request failed: {type(e).__name__}: {e}"

    if r.status_code != 200:
        return f"Error {r.status_code}: {r.text}"

    try:
        out = r.json()
    except Exception:
        return f"Prediction returned non-JSON response: {r.text}"

    # Expected response
    pred = out.get("predicted_price")
    return (
        f"Request sent to: {infer_url}\n"
        f"Inputs: food_group={fg}, severity_level={sev}, horizon_months={int(horizon)}\n"
        f"Predicted average price: {pred}"
    )