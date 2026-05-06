import dash
from dash import html, dcc
import pandas as pd
import numpy as np
import os

import plotly.express as px

from data_gcs import read_csv_from_gcs

dash.register_page(__name__, name="Analytical Methods", order=2)

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

    # 1) Correlation heatmap (product co-movement)
    prod_month = fao.groupby(["month", "Product"])["Price (Latest date)"].mean().reset_index()
    wide = prod_month.pivot(index="month", columns="Product", values="Price (Latest date)")
    corr = wide.corr(min_periods=12)

    fig_corr = px.imshow(
        corr,
        aspect="auto",
        title="Correlation Heatmap (Monthly Average Prices by Product)"
    )

    # 2) Seasonality profile (month-of-year patterns)
    fg_month = fao.groupby(["month", "Food Group"])["Price (Latest date)"].mean().reset_index()
    fg_month["month_num"] = fg_month["month"].dt.month

    season = fg_month.groupby(["Food Group", "month_num"])["Price (Latest date)"].mean().reset_index()

    fig_season = px.line(
        season,
        x="month_num",
        y="Price (Latest date)",
        color="Food Group",
        markers=True,
        title="Seasonality Profile (Average Price by Month-of-Year, Food Groups)"
    )
    fig_season.update_layout(xaxis=dict(dtick=1), xaxis_title="Month of Year (1-12)")

    # 3) Rolling correlation (egg price vs birds affected)
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
    merged = merged[merged["month"] >= pd.Timestamp("2022-02-01")].copy()

    merged["roll_corr_6m"] = merged["egg_price"].rolling(6).corr(merged["birds_affected"])

    fig_roll = px.line(
        merged,
        x="month",
        y="roll_corr_6m",
        title="Rolling Correlation (6-month): Egg Price vs Birds Affected (2022+)"
    )
    fig_roll.update_layout(xaxis=dict(rangeslider=dict(visible=True)), hovermode="x unified")
    fig_roll.update_yaxes(title_text="Rolling correlation (6-month)")

    # 4) Concentration of large changes by month-of-year (heatmap)
    fg_wide = fg_month.pivot(index="month", columns="Food Group", values="Price (Latest date)")
    fg_pct = fg_wide.pct_change() * 100

    records = []
    for fg in fg_pct.columns:
        s = fg_pct[fg].dropna()
        if len(s) < 12:
            continue
        thresh = s.abs().quantile(0.90)
        flag = (s.abs() >= thresh)
        tmp = pd.DataFrame({"month": s.index, "Food Group": fg, "large": flag.values})
        tmp["month_of_year"] = tmp["month"].dt.month
        counts = tmp.groupby("month_of_year")["large"].sum().reset_index()
        counts["Food Group"] = fg
        records.append(counts)

    large_counts = pd.concat(records, ignore_index=True)
    heat = large_counts.pivot(index="Food Group", columns="month_of_year", values="large").fillna(0)

    fig_large = px.imshow(
        heat,
        aspect="auto",
        title="Large Change Concentration (Top 10% |Monthly % Change|) by Month-of-Year"
    )
    fig_large.update_layout(xaxis_title="Month of Year (1-12)", yaxis_title="Food Group")

    return fig_corr, fig_season, fig_roll, fig_large


fig_corr, fig_season, fig_roll, fig_large = build_figures()

layout = html.Div(
    style=PAGE_STYLE,
    children=[
        html.Div(style=CARD_STYLE, children=[
            html.H2("Analytical Methods"),
        ]),
        html.Div(style=CARD_STYLE, children=[
            html.H3("1) Correlation analysis (monthly product co-movement)"),
            dcc.Graph(figure=fig_corr),
            html.P(
                "Monthly averaging reduces short-term noise. The heatmap shows which products move together over time, "
                "suggesting shared drivers or broad inflation pressure across items."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("2) Seasonality analysis (month-of-year patterns)"),
            dcc.Graph(figure=fig_season),
            html.P(
                "This plot isolates predictable seasonal patterns by averaging prices by calendar month. "
                "Differences across food groups indicate which categories are more seasonally driven."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("3) Time-dependent event relationship (rolling correlation)"),
            dcc.Graph(figure=fig_roll),
            html.P(
                "Rolling correlation preserves time ordering and shows how the relationship between outbreak activity "
                "and egg prices changes over time, which scatter plots cannot capture."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("4) Concentration of extreme price changes by month-of-year"),
            dcc.Graph(figure=fig_large),
            html.P(
                "This heatmap counts how often each food group experiences extreme monthly moves (top 10% by magnitude) "
                "in each calendar month. Concentration suggests seasonality, while dispersed spikes suggest shocks."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("5) Using Machine Learning for HPAI"),
            html.Br(),
            html.H4("5.1) Selecting the Model"),
            html.P(
                "For our analysis, we want to make a numerical prediction; therefore, we needed to select "
                "a regression model. Since we want our features to influence the regression in a way similar "
                "to an if-else statement, we proceeded with a DecisionTreeRegressor. However, a decision tree can be"
                "unstable and overfit, so we decided to use a RandomForestRegressor. A random forest uses the averages"
                "averages of many trees and has better generalization."
            ),
            html.H4("5.2) Data Cleaning"),
            html.P(
                "Due to differences in dates, we cumulated affected birds count by dates "
                "set by the FAO dataset. For example, the first instance of egg prices is on 10-20-2022 "
                ", but there are about 10 records of bird affected. We sum those 10 records and set that as the "
                "number of birds affected for 10-20-2022."       
            ),
            html.H4("5.3) Lag Features"),
            html.P(
                "In the real world, prices do not change the moment an event happens. There is also some "
                "form of time delay. Five lag features we created to help with our model are:"       
            ),
            html.Ul([
                html.Li("Affected Birds Lag"),
                html.Li("Price Lag"),
                html.Li("Price Differnce Lag"),
                html.Li("Severity Lag"),
                html.Li("Severity Lag 2")
            ]),
            html.P(
                "Affected Birds Lag is similar to Severity Lag in the way that it uses the previous record's "
                "information as a factor in the next record. Price Lag and Price Difference Lag uses price "
                "instead of affected birds to predict prices, which is common in economics. "
                "Lastly, Severity Lag 2 is a lag feature that goes up 2 rows; this is useful for demonstrating "
                "long-term event shock." 
            ),
            html.H4("5.4) Model Performance"),
            html.P(
                "For our model we use the following parameters for both chicken and eggs:"
            ),
            html.Ul([
                html.Li("n_estimators = 200"),
                html.Li("max_depth = 10"),
                html.Li("min_samples_leaf = 3")
            ]),
            html.P(
                "Using a tolerance of $0.05, we counted the prediction as correct as long as the prediction "
                "is within a 5 cent range of the actual price."
            ),
            html.P(
                "The model for chicken scored an accuracy of 0.963."
            ),
            html.P(
                "The model for egg scored an accuracy of 0.778."
            )
        ]),

        html.Div(style=CARD_STYLE, children=[
            html.H3("References"),
            html.Ul([
                html.Li("FAO Daily Food Prices Monitor dataset"),
                html.Li("USDA APHIS HPAI detections dataset"),
                html.Li("USDA ERS Food Price Outlook"),
                html.Li("BLS CPI supplemental files"),
            ])
        ])
    ]
)