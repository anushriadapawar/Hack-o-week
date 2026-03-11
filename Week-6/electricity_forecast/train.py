"""
train.py
Train the LSTM model on synthetic electricity data and save the model + scaler.
Run this ONCE before launching the Streamlit dashboard.
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Make sure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.generate_data import generate_electricity_data
from models.lstm_model import ElectricityLSTM, prepare_sequences, EarlyStopping

# ── Config ────────────────────────────────────────────────────────────────────
LOOKBACK          = 48      # hours of history used
FORECAST_HORIZON  = 24      # hours ahead to predict
HIDDEN_SIZE       = 64
NUM_LAYERS        = 2
DROPOUT           = 0.2
BATCH_SIZE        = 64
EPOCHS            = 50
LR                = 1e-3
DEVICE            = "cuda" if torch.cuda.is_available() else "cpu"

FEATURE_COLS = [
    "consumption_kwh",
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "is_holiday",
    "event_flag",
    "hour_sin",   # cyclical encoding
]
TARGET_COL = "consumption_kwh"
# ─────────────────────────────────────────────────────────────────────────────


def add_cyclical_features(df):
    df = df.copy()
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    return df


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    models_dir = os.path.join(script_dir, "models")

    print("=" * 60)
    print("  Electricity LSTM Training")
    print("=" * 60)

    # 1. Generate / load data
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, "electricity_data.csv")
    events_path = os.path.join(data_dir, "events.csv")
    if os.path.exists(data_path):
        print("Loading existing data …")
        df = pd.read_csv(data_path, index_col="timestamp", parse_dates=True)
    else:
        print("Generating synthetic data …")
        df, events = generate_electricity_data()
        df.to_csv(data_path)
        events.to_csv(events_path, index=False)

    os.makedirs(models_dir, exist_ok=True)

    df = add_cyclical_features(df)
    print(f"Dataset: {len(df):,} hourly records  |  device: {DEVICE}")

    # 2. Scale features
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    df[FEATURE_COLS] = scaler_X.fit_transform(df[FEATURE_COLS])
    df[[TARGET_COL]]  = scaler_y.fit_transform(df[[TARGET_COL]])

    # 3. Build sequences
    print("Building sequences …")
    X, y = prepare_sequences(df, FEATURE_COLS, TARGET_COL, LOOKBACK, FORECAST_HORIZON)
    print(f"X shape: {X.shape}   y shape: {y.shape}")

    # 4. Train / val split (no shuffle — time-series)
    split = int(len(X) * 0.85)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    def to_tensor(a): return torch.tensor(a, dtype=torch.float32).to(DEVICE)

    train_ds = TensorDataset(to_tensor(X_train), to_tensor(y_train))
    val_ds   = TensorDataset(to_tensor(X_val),   to_tensor(y_val))
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_dl   = DataLoader(val_ds,   batch_size=BATCH_SIZE)

    # 5. Model
    model = ElectricityLSTM(
        input_size=len(FEATURE_COLS),
        hidden_size=HIDDEN_SIZE,
        num_layers=NUM_LAYERS,
        output_size=FORECAST_HORIZON,
        dropout=DROPOUT,
    ).to(DEVICE)
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    criterion = nn.MSELoss()
    es = EarlyStopping(patience=10)

    # 6. Training loop
    print("\nTraining …")
    history = {"train": [], "val": []}
    best_val = float("inf")

    for epoch in range(1, EPOCHS + 1):
        model.train()
        train_losses = []
        for xb, yb in train_dl:
            optimizer.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_losses.append(loss.item())

        model.eval()
        val_losses = []
        with torch.no_grad():
            for xb, yb in val_dl:
                pred = model(xb)
                val_losses.append(criterion(pred, yb).item())

        tl = np.mean(train_losses)
        vl = np.mean(val_losses)
        history["train"].append(tl)
        history["val"].append(vl)
        scheduler.step(vl)

        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{EPOCHS}  train={tl:.4f}  val={vl:.4f}")

        if vl < best_val:
            best_val = vl
            model_path = os.path.join(models_dir, "best_lstm.pt")
            torch.save(model.state_dict(), model_path)

        es(vl)
        if es.stop:
            print(f"  Early stopping at epoch {epoch}")
            break

    print(f"\nBest val loss: {best_val:.4f}")

    # 7. Save artefacts
    scaler_x_path = os.path.join(models_dir, "scaler_X.pkl")
    scaler_y_path = os.path.join(models_dir, "scaler_y.pkl")
    meta_path = os.path.join(models_dir, "meta.pkl")
    with open(scaler_x_path, "wb") as f: pickle.dump(scaler_X, f)
    with open(scaler_y_path, "wb") as f: pickle.dump(scaler_y, f)

    meta = {
        "feature_cols":       FEATURE_COLS,
        "target_col":         TARGET_COL,
        "lookback":           LOOKBACK,
        "forecast_horizon":   FORECAST_HORIZON,
        "hidden_size":        HIDDEN_SIZE,
        "num_layers":         NUM_LAYERS,
        "dropout":            DROPOUT,
        "history":            history,
    }
    with open(meta_path, "wb") as f: pickle.dump(meta, f)

    print("Saved: models/best_lstm.pt, models/scaler_X.pkl, models/scaler_y.pkl, models/meta.pkl")
    print("Done! Launch the dashboard with:  streamlit run app.py")


if __name__ == "__main__":
    main()
