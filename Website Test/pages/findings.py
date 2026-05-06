import dash
from dash import html, dcc
import pandas as pd
import numpy as np
import os

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_gcs import read_csv_from_gcs

dash.register_page(__name__, name="Major Findings", order=3)

CARD_STYLE = {
    "padding": "20px",
    "borderRadius": "12px",
    "backgroundColor": "white",
    "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
    "marginBottom": "20px"
}
PAGE_STYLE = {"padding": "20px", "backgroundColor": "#f4f6f9"}


def load_data():
    fao = read_csv_from_gcs(os.environ.get("FAO_BLOB", "fao.csv"))
    hpai = read_csv_from_gcs(os.environ.get("HPAI_BLOB", "hpai.csv"))

    fao["Latest date"] = pd.to_datetime(fao["Latest date"], errors="coerce")
    fao["Price (Latest date)"] = pd.to_numeric(fao["Price (Latest date)"], errors="coerce")
    fao = fao.dropna(subset=["Latest date", "Price (Latest date)", "Product", "Food Group"]).copy()
    fao["month"] = fao["Latest date"].dt.to_period("M").dt.to_timestamp()

    hpai["Confirmed"] = pd.to_datetime(hpai["Confirmed"], errors="coerce")
    hpai["Birds Affected"] = pd.to_numeric(hpai["Birds Affected"], errors="coerce")
    hpai = hpai.dropna(subset=["Confirmed"]).copy()
    hpai["month"] = hpai["Confirmed"].dt.to_period("M").dt.to_timestamp()

    return fao, hpai


def build_figures():
    fao, hpai = load_data()

    # food group monthly trend (interactive)
    fg_month = fao.groupby(["month", "Food Group"])["Price (Latest date)"].mean().reset_index()
    fig_fg = px.line(
        fg_month, x="month", y="Price (Latest date)", color="Food Group",
        title="Food Group Trends: Monthly Average Price Over Time"
    )
    fig_fg.update_layout(xaxis=dict(rangeslider=dict(visible=True)), hovermode="x unified")

    # egg vs birds affected (interactive dual-axis)
    egg = (
        fao[fao["Product"] == "Chicken Egg"]
        .groupby("month")["Price (Latest date)"].mean()
        .reset_index()
        .rename(columns={"Price (Latest date)": "egg_price"})
    )
    birds_m = (
        hpai.groupby("month")["Birds Affected"].sum()
        .reset_index()
        .rename(columns={"Birds Affected": "birds_affected"})
    )
    merged = egg.merge(birds_m, on="month", how="left").fillna({"birds_affected": 0}).sort_values("month")

    fig_egg_birds = make_subplots(specs=[[{"secondary_y": True}]])
    fig_egg_birds.add_trace(go.Scatter(x=merged["month"], y=merged["egg_price"], mode="lines", name="Egg price"), secondary_y=False)
    fig_egg_birds.add_trace(go.Scatter(x=merged["month"], y=merged["birds_affected"], mode="lines", name="Birds affected"), secondary_y=True)
    fig_egg_birds.update_layout(
        title="Bird Flu Event Alignment: Egg Price vs Birds Affected (Monthly)",
        hovermode="x unified",
        xaxis=dict(rangeslider=dict(visible=True))
    )
    fig_egg_birds.update_yaxes(title_text="Egg price", secondary_y=False)
    fig_egg_birds.update_yaxes(title_text="Birds affected", secondary_y=True)

    # boxplot by food group
    fig_box = px.box(
        fao, x="Food Group", y="Price (Latest date)",
        title="Food Group Variability: Price Distribution by Food Group"
    )

    # 1: overall percent change by food group (first to last month)
    fg_wide = fg_month.pivot(index="month", columns="Food Group", values="Price (Latest date)")
    chg_rows = []
    for fg in fg_wide.columns:
        s = fg_wide[fg].dropna()
        if len(s) >= 2:
            pct = (s.iloc[-1] - s.iloc[0]) / s.iloc[0] * 100
            chg_rows.append({"Food Group": fg, "percent_change": float(pct)})
    chg_df = pd.DataFrame(chg_rows).sort_values("percent_change", ascending=False)

    fig_group_change = px.bar(
        chg_df, x="Food Group", y="percent_change",
        title="Overall Percent Change by Food Group (First to Last Month)"
    )
    fig_group_change.update_yaxes(title_text="Percent change (%)")

    # 2: lagged correlation curve (birds lead egg % change)
    lag_df = merged[merged["month"] >= pd.Timestamp("2022-02-01")].copy()
    lag_df["egg_pct_change"] = lag_df["egg_price"].pct_change() * 100

    lag_results = []
    for L in range(0, 7):
        lag_df[f"birds_lag_{L}"] = lag_df["birds_affected"].shift(L)
        tmp = lag_df.dropna(subset=["egg_pct_change", f"birds_lag_{L}"])
        r = tmp[["egg_pct_change", f"birds_lag_{L}"]].corr().iloc[0, 1] if len(tmp) > 2 else np.nan
        lag_results.append({"birds_lead_months": L, "corr": float(r) if not np.isnan(r) else None})

    lag_corr_df = pd.DataFrame(lag_results)

    fig_lag = px.line(
        lag_corr_df, x="birds_lead_months", y="corr",
        markers=True,
        title="Lagged Correlation: Birds Affected Leading Egg % Change (2022+)"
    )
    fig_lag.update_layout(xaxis=dict(dtick=1))
    fig_lag.update_yaxes(title_text="Correlation")

    # 3: forecast backtest (train 2020–2023, predict 2024–2026 vs actual) for food groups
    train = fg_month[(fg_month["month"] >= "2020-01-01") & (fg_month["month"] <= "2023-12-01")].copy()
    test = fg_month[(fg_month["month"] >= "2024-01-01") & (fg_month["month"] <= "2026-12-01")].copy()

    future_months = pd.date_range("2024-01-01", "2026-12-01", freq="MS")
    preds = []

    for fg in train["Food Group"].unique():
        g = train[train["Food Group"] == fg].sort_values("month")
        t = np.arange(len(g))
        y = g["Price (Latest date)"].values
        b = np.cov(t, y, bias=True)[0, 1] / np.var(t)
        a = y.mean() - b * t.mean()
        t_future = np.arange(len(g), len(g) + len(future_months))
        y_future = a + b * t_future
        preds.append(pd.DataFrame({"month": future_months, "Food Group": fg, "pred": y_future}))

    pred_df = pd.concat(preds, ignore_index=True)

    fig_backtest = go.Figure()
    for fg in sorted(train["Food Group"].unique()):
        act = test[test["Food Group"] == fg].sort_values("month")
        pred = pred_df[pred_df["Food Group"] == fg].sort_values("month")

        fig_backtest.add_trace(go.Scatter(
            x=act["month"], y=act["Price (Latest date)"],
            mode="lines", name=f"{fg} actual (2024–2026)"
        ))
        fig_backtest.add_trace(go.Scatter(
            x=pred["month"], y=pred["pred"],
            mode="lines", line=dict(dash="dot"),
            name=f"{fg} predicted (2024–2026)"
        ))

    fig_backtest.update_layout(
        title="Forecast Backtest: Train 2020–2023, Predict 2024–2026 vs Actual (Food Groups)",
        xaxis_title="Month",
        yaxis_title="Average price",
        hovermode="x unified",
        xaxis=dict(rangeslider=dict(visible=True))
    )

    return fig_fg, fig_egg_birds, fig_box, fig_group_change, fig_lag, fig_backtest


fig_fg, fig_egg_birds, fig_box, fig_group_change, fig_lag, fig_backtest = build_figures()

layout = html.Div(
    style=PAGE_STYLE,
    children=[
        html.Div(style=CARD_STYLE, children=[
            html.H2("Major Findings"),
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Food group trends over time"),
            dcc.Graph(figure=fig_fg),
            html.P(
                "Monthly aggregation reveals long-term trends and periods of rapid change across food groups."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Bird flu event alignment and egg prices"),
            dcc.Graph(figure=fig_egg_birds),
            html.P(
                "The dual-axis time series preserves timing and supports inspection of alignment and possible lags."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Food group variability"),
            dcc.Graph(figure=fig_box),
            html.P(
                "Distribution differences across food groups indicate which categories have higher volatility."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Overall percent change by food group"),
            dcc.Graph(figure=fig_group_change),
            html.P(
                "This summarizes which food groups increased the most from the first available month to the last."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Lagged relationship: outbreak activity leading egg percent change"),
            dcc.Graph(figure=fig_lag),
            html.P(
                "This tests time dependency directly by evaluating whether birds affected leads egg % change by 0–6 months."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("Forecast backtest: predicted vs actual (2024–2026)"),
            dcc.Graph(figure=fig_backtest),
            html.P(
                "A baseline trend forecast is compared to actual outcomes for 2024–2026 to illustrate forecast gaps and "
                "where event-aware features may improve accuracy."
            )
        ])
    ]
)