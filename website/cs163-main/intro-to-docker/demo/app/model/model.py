import json
import os

ARTIFACT_PATH = os.path.join(os.path.dirname(__file__), "artifacts.json")

_artifacts = None

def load():
    global _artifacts
    if os.path.exists(ARTIFACT_PATH):
        with open(ARTIFACT_PATH, "r") as f:
            _artifacts = json.load(f)
    else:
        _artifacts = None

def predict_food_group(food_group: str, horizon_months: int, severity_level: str) -> float:
    global _artifacts
    if _artifacts is None:
        raise RuntimeError("Model not loaded. Run train.py first.")

    if food_group not in _artifacts["food_group_models"]:
        raise ValueError("Unknown food_group")

    if severity_level not in _artifacts["severity_offsets"]:
        raise ValueError("Unknown severity_level")

    a = _artifacts["food_group_models"][food_group]["a"]
    b = _artifacts["food_group_models"][food_group]["b"]

    base_pred = a + b * horizon_months
    sev_offset = _artifacts["severity_offsets"][severity_level]

    return float(base_pred + sev_offset)