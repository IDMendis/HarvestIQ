# 🌱 HarvestIQ — Sri Lankan Vegetable Price Prediction

### Machine Learning-Based Vegetable Price Forecasting Using Ensemble Learning

## Project Overview

HarvestIQ is a machine learning-based web application developed to predict vegetable prices in Sri Lankan markets.

The project uses historical Sri Lankan vegetable price data and three ensemble learning techniques: **Bagging, Boosting, and Stacking**.

An interactive web dashboard allows users to explore historical prices, compare machine learning models, and generate seven-day-ahead vegetable price forecasts.

##  Dataset

The project uses historical Sri Lankan vegetable price data.

- **Total records:** 85,471
- **Vegetables:** 8
- **Markets:** 3
- **Price types:** Retail and Wholesale
- **Date range:** August 2016 – November 2026
- **Total price series:** 40

The dataset was processed using data cleaning, feature engineering, lag features, and rolling statistics.

## Machine Learning Models

Three ensemble learning techniques were implemented:

| Technique | Algorithm |
|---|---|
| Bagging | Random Forest Regressor |
| Boosting | Gradient Boosting and XGBoost |
| Stacking | Ensemble of Random Forest, Gradient Boosting, and XGBoost with a Ridge Regression meta-model |

The final Stacking Ensemble is used to generate seven-day-ahead vegetable price predictions.

### Model Evaluation

The models were evaluated using MAE, RMSE, and R².

| Metric | Stacking Ensemble |
|---|---|
| MAE | 64.42 |
| RMSE | 102.08 |
| R² | 0.794 |

These results represent a historical evaluation benchmark and should not be interpreted as guaranteed future forecasting accuracy.

## Technologies Used

**Machine Learning:** Python, Scikit-learn, XGBoost, Pandas, NumPy

**Backend:** FastAPI

**Frontend:** React, Vite, Tailwind CSS, Recharts

**Development:** Google Colab, VS Code

##  Dashboard Features

- Seven-day-ahead vegetable price prediction
- Vegetable, market, and price-type selection
- Historical vegetable price visualization
- Machine learning model comparison
- Dataset exploration and statistics
- Interactive and responsive dashboard

##  System Architecture

The React frontend communicates with a Python FastAPI backend through REST APIs.

The backend loads the trained ensemble learning model and generates price predictions using the historical dataset.

##  Project Components

- `notebooks/` — Data preprocessing, model training, and evaluation notebooks
- `models/` — Trained model artifacts and evaluation results
- `data/` — Historical vegetable price datasets
- `web-app/backend/` — FastAPI backend
- `web-app/frontend/` — React frontend

##  Running the Application

Install the backend dependencies and start the FastAPI server:

```bash
cd web-app/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

In another terminal, install and start the frontend:

```bash
cd web-app/frontend
npm install
npm run dev
```

Open the local URL displayed by Vite, typically `http://localhost:5173`.

**Note:** The application requires the trained model artifacts and dataset files. Ensure these are available in the expected project directories before running it.

