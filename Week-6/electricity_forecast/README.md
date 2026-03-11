# ⚡ Electricity Post-Event Demand Forecasting — LSTM + Streamlit

A complete end-to-end pipeline that:
1. **Generates** synthetic hourly electricity consumption data with randomly injected events (Sports, Concert, Holiday, Festival, Conference)
2. **Trains** a 2-layer LSTM to predict the next 24h post-event demand using a 48h lookback window
3. **Visualises** forecasts, heatmaps, and event impact in an interactive Streamlit dashboard with sidebar filters

---

## 📁 Project Structure
```
electricity_forecast/
├── app.py                  ← Streamlit dashboard (main entry point)
├── train.py                ← Train LSTM + save artefacts
├── requirements.txt
├── data/
│   ├── generate_data.py    ← Synthetic data generator
│   ├── electricity_data.csv  (auto-generated)
│   └── events.csv            (auto-generated)
└── models/
    ├── lstm_model.py       ← LSTM architecture + helpers
    ├── best_lstm.pt          (saved after training)
    ├── scaler_X.pkl          (saved after training)
    ├── scaler_y.pkl          (saved after training)
    └── meta.pkl              (saved after training)
```

---

## 🚀 Quick Start (VS Code)

### 1 — Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate
```

### 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### 3 — Train the LSTM  *(run once)*
```bash
python train.py
```
This will:
- Generate ~17,500 hourly records spanning 2 years with 80 randomly injected events
- Train a 2-layer LSTM for up to 50 epochs (early-stopping enabled)
- Save `models/best_lstm.pt`, `scaler_X.pkl`, `scaler_y.pkl`, `meta.pkl`

Training takes **1–3 minutes** on CPU.

### 4 — Launch the dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`

---

## 🎛 Dashboard Features

| Tab | What you see |
|-----|-------------|
| **Forecast Explorer** | Pick any event, see 24h LSTM forecast vs actual post-event demand |
| **Patterns Heatmap** | Hour × Day-of-Week heatmap + box plots |
| **Event Impact** | Bar charts & overlay lines comparing event vs normal consumption |
| **Model Performance** | Training loss curve, architecture summary, bulk MAE evaluation |

### Sidebar Filters
- **Day Type**: All / Weekdays only / Weekends only
- **Event Type**: All / Sports / Concert / Holiday / Festival / Conference / No Event
- **Date Range**: Custom from–to date picker
- **Forecast Hours**: 6 / 12 / 18 / 24h post-event window
- **Event Index**: Navigate through events one by one

---

## 🧠 Model Details

| Setting | Value |
|---------|-------|
| Architecture | 2-layer LSTM |
| Input features | 8 (consumption, hour, DOW, month, weekend flag, holiday flag, event flag, cyclical hour) |
| Lookback | 48 hours |
| Forecast horizon | 24 hours |
| Hidden size | 64 |
| Optimizer | Adam (lr=1e-3) with ReduceLROnPlateau |
| Loss | MSE |
| Regularisation | Dropout 0.2, gradient clipping |

---

## 📦 Requirements
- Python 3.9+
- streamlit, plotly, pandas, numpy, torch, scikit-learn, matplotlib
