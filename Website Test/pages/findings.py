import dash
from dash import html, dcc
import pandas as pd
import numpy as np
import os
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from data_gcs import read_csv_from_gcs

dash.register_page(__name__, name="Major Findings", order=3)

CARD_STYLE = {
    "padding": "20px",
    "borderRadius": "12px",
    "backgroundColor": "white",
    "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
    "marginBottom": "20px"
}

# Load from GCS
fao = read_csv_from_gcs(os.environ.get("FAO_BLOB", "fao.csv"))
hpai = read_csv_from_gcs(os.environ.get("HPAI_BLOB", "hpai.csv"))

# Clean types
fao["Latest date"] = pd.to_datetime(fao["Latest date"], errors="coerce")
fao["Price (Latest date)"] = pd.to_numeric(fao["Price (Latest date)"], errors="coerce")
fao = fao.dropna(subset=["Latest date", "Price (Latest date)"]).copy()

fao["month"] = fao["Latest date"].dt.to_period("M").dt.to_timestamp()

# Food group trend (monthly)
fg = fao.groupby(["month", "Food Group"])["Price (Latest date)"].mean().reset_index()
fig_fg = px.line(fg, x="month", y="Price (Latest date)", color="Food Group",
                 title="Monthly Average Price by Food Group (Interactive)")

# Egg monthly
egg = (
    fao[fao["Product"] == "Chicken Egg"]
    .groupby("month")["Price (Latest date)"]
    .mean()
    .reset_index()
    .rename(columns={"Price (Latest date)": "egg_price"})
)

# HPAI monthly (birds affected)
hpai["Confirmed"] = pd.to_datetime(hpai["Confirmed"], errors="coerce")
hpai["Birds Affected"] = pd.to_numeric(hpai["Birds Affected"], errors="coerce")
hpai = hpai.dropna(subset=["Confirmed"]).copy()
hpai["month"] = hpai["Confirmed"].dt.to_period("M").dt.to_timestamp()

birds_m = (
    hpai.groupby("month")["Birds Affected"]
    .sum()
    .reset_index()
    .rename(columns={"Birds Affected": "birds_affected"})
)

merged = egg.merge(birds_m, on="month", how="left").fillna({"birds_affected": 0}).sort_values("month")

# Interactive dual-axis plot
fig_egg_birds = make_subplots(specs=[[{"secondary_y": True}]])
fig_egg_birds.add_trace(go.Scatter(x=merged["month"], y=merged["egg_price"], mode="lines", name="Egg price"), secondary_y=False)
fig_egg_birds.add_trace(go.Scatter(x=merged["month"], y=merged["birds_affected"], mode="lines", name="Birds affected"), secondary_y=True)

fig_egg_birds.update_layout(
    title="Egg Price vs Birds Affected (Interactive, Monthly)",
    hovermode="x unified",
    xaxis=dict(rangeslider=dict(visible=True))
)
fig_egg_birds.update_yaxes(title_text="Egg price", secondary_y=False)
fig_egg_birds.update_yaxes(title_text="Birds affected", secondary_y=True)

# Variability boxplot
fig_box = px.box(fao, x="Food Group", y="Price (Latest date)", title="Price Variation by Food Group (Boxplot)")

layout = html.Div(
    style={"padding": "20px", "backgroundColor": "#f4f6f9"},
    children=[
        html.Div(style=CARD_STYLE, children=[
            html.H2("Major Findings"),
            html.P("Key results and visual evidence based on FAO prices and bird-flu event data.")
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Food group trends over time"),
            dcc.Graph(figure=fig_fg),
            html.P(
                "This time-series view shows how monthly average prices evolve by food group and helps identify which groups "
                "rise faster or exhibit spikes over time."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Bird flu activity and egg prices (time-dependent analysis)"),
            dcc.Graph(figure=fig_egg_birds),
            html.P(
                "The interactive dual-axis chart supports inspection of timing, potential lag, and persistence of egg price changes "
                "relative to outbreak activity (Birds Affected)."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Food group variability"),
            dcc.Graph(figure=fig_box),
            html.P(
                "This distribution plot highlights differences in volatility across food groups, indicating which categories have "
                "higher price uncertainty."
            )
        ])
    ]
)