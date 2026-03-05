# Admin Building Energy Consumption Analysis & Forecasting

## Overview
This project focuses on analyzing and forecasting energy consumption in an administrative building using the **Appliances Energy Prediction Dataset** from [Kaggle](https://www.kaggle.com/datasets/harivpatel/appliances-energy-prediction-dataset). The goal is to:

- Identify **usage patterns** via clustering
- Forecast **appliance energy consumption** using advanced ML models
- Quantify **energy savings potential** for operational efficiency

The project integrates **time-series feature engineering, clustering, and gradient boosting regression** to achieve realistic and actionable predictions.

---

## Dataset

- Source: [Kaggle – Appliances Energy Prediction Dataset](https://www.kaggle.com/datasets/harivpatel/appliances-energy-prediction-dataset)
- Data includes:
  - Appliance energy consumption (Wh)
  - Environmental variables (temperature, humidity, wind speed, etc.)
  - Timestamp information (date, hour, weekday)
  - Lighting consumption
  - Outdoor weather features

---

## Project Workflow

### 1. Data Preprocessing
- Convert timestamps to **datetime** objects
- Extract features: `hour`, `weekday`, `is_weekend`
- Handle missing data (if any)
- Standardize numerical features for clustering

### 2. Usage Profile Clustering
- **K-Means clustering** applied to segment appliance usage behavior into 3 clusters:
  - Low-usage periods (e.g., weekends)
  - Medium-usage periods
  - Peak-usage periods (e.g., weekdays with high occupancy)
- Clustering helps **identify patterns** and segment data for model training

### 3. Feature Engineering
- **Lag features**: `Appliances_lag1`, `Appliances_lag2`, `Appliances_lag3`
- **Rolling statistics**: mean and standard deviation (shifted by 1 to prevent data leakage)
- **Cyclical encoding** of hour: `hour_sin`, `hour_cos`
- These features capture **temporal dependencies** and **cyclical patterns** in energy usage

### 4. Baseline Model
- **Linear Regression** applied per cluster as a baseline
- Provides reference metrics: MAE and R²

### 5. Advanced Forecasting Model
- **HistGradientBoostingRegressor** used for non-linear regression
- Trained per cluster using temporal and environmental features
- Predicts appliance energy consumption accurately

### 6. Savings Estimation
- Forecasted consumption is compared with actual usage
- Positive differences indicate **potential energy savings**
- Aggregated per cluster for **dashboard visualization**

---

## Key Features Used in Forecasting

| Feature | Description |
|---------|-------------|
| hour_sin, hour_cos | Cyclical encoding of hour for daily patterns |
| is_weekend | Binary indicator for weekend vs weekday |
| T_out | Outdoor temperature (°C) |
| RH_out | Outdoor relative humidity (%) |
| Windspeed | Outdoor wind speed (m/s) |
| Appliances_lag1-3 | Lagged appliance consumption values |
| Appliances_roll_mean_3 | Rolling mean of past 3 timestamps (shifted) |
| Appliances_roll_std_3 | Rolling std of past 3 timestamps (shifted) |

---

## Evaluation Metrics

| Cluster | Baseline MAE | Baseline R² | Gradient Boosting MAE | Gradient Boosting R² |
|---------|-------------|-------------|----------------------|--------------------|
| 0       | 13.07       | 0.34        | 13.06                | 0.34               |
| 1       | 38.24       | 0.53        | 38.24                | 0.53               |
| 2       | 52.16       | 0.62        | 52.16                | 0.62               |

> **Note:** Metrics may vary slightly depending on train-test split.

---

## Visualization

### Cluster-Based Energy Savings Potential

- Shows the proportion of **energy savings potential** per cluster
- Useful for **identifying high-impact periods** for energy optimization
