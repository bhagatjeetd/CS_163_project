from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model.model import load, predict_food_group

app = FastAPI()

class FoodGroupRequest(BaseModel):
    food_group: str
    severity_level: str
    horizon_months: int

@app.on_event("startup")
def startup():
    load()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict_food_group")
def predict_food_group_endpoint(req: FoodGroupRequest):
    try:
        pred = predict_food_group(req.food_group, req.horizon_months, req.severity_level)
        return {"food_group": req.food_group, "severity_level": req.severity_level, "horizon_months": req.horizon_months, "predicted_price": pred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))