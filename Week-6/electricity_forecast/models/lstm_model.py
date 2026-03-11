"""
lstm_model.py
Simple LSTM model for hourly electricity consumption forecasting.
"""

import torch
import torch.nn as nn
import numpy as np


class ElectricityLSTM(nn.Module):
    def __init__(self, input_size=8, hidden_size=64, num_layers=2, output_size=24, dropout=0.2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, output_size),
        )

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])  # Use last timestep
        return out


def prepare_sequences(df, feature_cols, target_col, lookback=48, forecast_horizon=24):
    """Create sliding window sequences from time-series dataframe."""
    features = df[feature_cols].values.astype(np.float32)
    target = df[target_col].values.astype(np.float32)

    X, y = [], []
    for i in range(lookback, len(features) - forecast_horizon + 1):
        X.append(features[i - lookback : i])
        y.append(target[i : i + forecast_horizon])

    return np.array(X), np.array(y)


class EarlyStopping:
    def __init__(self, patience=10, min_delta=0.01):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.stop = False

    def __call__(self, val_loss):
        if self.best_loss is None or val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.stop = True
