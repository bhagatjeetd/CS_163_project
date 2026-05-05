import json
import pandas as pd
import numpy as np

FOOD_GROUPS = ["Dairy", "Fruit", "Grain", "Protein", "Vegetable"]
SEVERITY_LEVELS = ["Very Low", "Low", "Medium", "High"]

def main():
    df = pd.read_csv("fao.csv")
    df["Latest date"] = pd.to_datetime(df["Latest date"], errors="coerce")
    df["Price (Latest date)"] = pd.to_numeric(df["Price (Latest date)"], errors="coerce")
    df = df.dropna(subset=["Latest date", "Price (Latest date)", "Food Group"])

    df["month"] = df["Latest date"].dt.to_period("M").dt.to_timestamp()
    fg = df.groupby(["month", "Food Group"])["Price (Latest date)"].mean().reset_index()

    artifacts = {"food_group_models": {}, "severity_offsets": {}}

    # Simple severity offsets: consistent, deterministic ordering
    # You can replace these later with learned offsets from event data.
    artifacts["severity_offsets"] = {
        "Very Low": 0.00,
        "Low": 0.01,
        "Medium": 0.02,
        "High": 0.03
    }

    for g in FOOD_GROUPS:
        sub = fg[fg["Food Group"] == g].sort_values("month").copy()
        if len(sub) < 6:
            continue

        # time index in months
        t = np.arange(len(sub))
        y = sub["Price (Latest date)"].values

        # y = a + b*t (least squares)
        b = np.cov(t, y, bias=True)[0, 1] / np.var(t)
        a = y.mean() - b * t.mean()

        artifacts["food_group_models"][g] = {
            "a": float(a),
            "b": float(b),
            "t0_month": str(sub["month"].iloc[0].date())
        }

    with open("model/artifacts.json", "w") as f:
        json.dump(artifacts, f, indent=2)

if __name__ == "__main__":
    main()