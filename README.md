# CS 163 Project: Food Price Inflation Analysis

## 1) What is this repo?
This repository contains all the files related to our project concerning U.S. grocery prices. The project uses FAO grocery price data (Feb 2020 to Feb 2026) and an HPAI/birds-affected dataset to support severity-based event analysis and forecasting by food group. The results and an interactive inference model is published on a cloud-hosted website provided by Google Cloud. 

## 2) Repository structure
Top-level directories/files:

* `CS_163_Data_Preprocessing (3).ipynb`
  Data cleaning and EDA on FAO prices (monthly aggregation, food group analysis, correlation, forecasting backtests).
* `Affected_Birds_Analysis.ipynb`
  Event-focused analysis linking birds-affected activity to egg and chicken prices using time-dependent visualizations and lag analyses.
* `Website Test/`
  Dash website deployed on Google App Engine with pages for landing/objective, analytical methods, major findings, and an inference UI.
* `website/cs163-main/intro-to-docker/demo/`
  Docker + FastAPI inference service deployed on Google Cloud Run.

Data files:

* `fao.csv` - FAO price data used in notebooks and website
* `Affected_Birds.csv` - affected birds data by the USDA
* `hpai.csv` (clean version of Affected_Birds.csv)
* `producer-prices_usa (1).csv` (supplemental dataset)

## 3) Setup instructions (local development)

### A) Python environment

Recommended: Python 3.10+ for the Dash website, and Python 3.9+ for the inference service container.

Install common packages for notebooks (run from repo root):

```bash
pip install pandas numpy matplotlib plotly
```

### B) Run the Dash website locally

From:

```bash
cd "Website Test"
pip install -r requirements.txt
python app7.py
```

Then open:

* `http://127.0.0.1:8050`

### C) Run the inference service locally (FastAPI)

From:

```bash
cd "website/cs163-main/intro-to-docker/demo"
pip install -r app/requirements.txt
```

Train artifacts (required before building/deploying so the model is available at runtime):

```bash
python app/model/train.py
```

Run server locally:

```bash
fastapi run app/main.py --host 0.0.0.0 --port 8080
```

Then open:

* `http://127.0.0.1:8080/docs`

## 4) Pipeline overview (end-to-end flow)

This project follows the pipeline below, from raw data → analysis → web publication → inference:

1. **Data loading**

   * Load FAO price data and USDA's bird affected data. 
2. **Preprocessing + feature creation (notebooks)**

   * Convert dates, clean missing/inconsistent values, group products into food groups, compute monthly averages, and build derived features for analysis (percent changes, correlations, seasonal profiles) in `CS_163_Data_Preprocessing (3).ipynb`.
3. **Analysis + visualization (`CS_163_Data_Preprocessing (3).ipynb`)**

   * Time-dependent event alignment (egg prices vs birds affected), correlation structure among products, seasonality vs shocks, and baseline forecasting comparisons.
4. **Machine Learning Model**

   * In `Affected_Birds_Analysis.ipynb`, train two RandomForestRegressor models on a joined dataset between birds affected and chicken and another for eggs. Using results from the models, conduct additional analyses related to model predictions.
5. **Website publication (App Engine)**

   * Dash website displays interactive plots and short explanations for Objective, Analytical Methods, and Major Findings (rubric requirement). 
6. **Inference service (Cloud Run)**

   * A Dockerized FastAPI service provides a `/predict_food_group` endpoint for forecasting, and the website calls this endpoint (rubric requirement). 

## 5) System design (how components connect + scalability)

### Architecture diagram

```
                 +------------------------+
                 |      Google Cloud      |
                 |                        |
User Browser --->|  App Engine (Dash)     |-----> Cloud Run (FastAPI)
                 |  Website Test/         |       /predict_food_group
                 |                        |
                 |      |                 |
                 |      v                 |
                 |  Cloud Storage (GCS)   |
                 |  fao.csv, hpai.csv     |
                 +------------------------+
```

### How data is stored in the cloud and consumed by the website

The website reads from Google Cloud Service (GCS) using `Website Test/data_gcs.py` and environment variables defined in `Website Test/app.yaml`.

### Scalability discussion

* **App Engine (website):** automatically manages instances based on request load; Dash pages primarily do read + aggregation and serve Plotly interactive charts. 
* **Cloud Run (inference):** scales the inference container based on incoming request rate; the service must bind to `PORT` and respond quickly to avoid startup timeouts. 

## 6) Inference service (Cloud Run) details

### Location of Docker/inference code

* `website/cs163-main/intro-to-docker/demo/`

  * `Dockerfile` (build container)
  * `app/main.py` (FastAPI app)
  * `app/model/train.py` (creates trained artifacts)
  * `app/model/model.py` (loads artifacts and serves predictions)

### Endpoint and I/O

Base URL (current deployment):

* `https://infser-90695129128.us-west2.run.app`

Health check:

* `GET /health` → `{"status":"ok"}`

Forecast endpoint:

* `POST /predict_food_group`
* Request JSON:

```json
{
  "food_group": "Dairy",
  "severity_level": "High",
  "horizon_months": 36
}
```

* Response JSON:

```json
{
  "food_group": "Dairy",
  "severity_level": "High",
  "horizon_months": 36,
  "predicted_price": 6.82
}
```

## 7) Data store in Cloud
The dataset we have stored in the Cloud are:
 * `hpai.csv` - the clean version of the birds affected dataset used to show correlation between egg prices and birds affected in our Analytical Methods and Major Findings page
 * `fao.csv` - updated version of the FAO data, also used in visualizations shown in our Analytical Methods and Major Findings page

These datasets are stored in our project buckets and are used by our website through 
  * fao = read_csv_from_gcs(os.environ.get("FAO_BLOB", "fao.csv"))
  * hpai = read_csv_from_gcs(os.environ.get("HPAI_BLOB", "hpai.csv"))

## 8) Website Link
https://essential-wares-489018-r0.uw.r.appspot.com
