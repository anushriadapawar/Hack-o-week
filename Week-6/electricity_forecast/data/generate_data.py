"""
generate_data.py
Generates synthetic hourly electricity consumption data with event markers.
"""

import numpy as np
import pandas as pd
from datetime import timedelta

def generate_electricity_data(start_date="2022-01-01", end_date="2024-01-01", seed=42):
    np.random.seed(seed)

    date_range = pd.date_range(start=start_date, end=end_date, freq="h")
    n = len(date_range)

    hour_of_day = date_range.hour.to_numpy()
    day_of_week = date_range.dayofweek.to_numpy()
    month       = date_range.month.to_numpy()

    hourly_pattern = (
        100
        + 40 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
        + 20 * np.sin(4 * np.pi * (hour_of_day - 9) / 24)
    )

    weekend_factor = np.where(day_of_week >= 5, 0.80, 1.0)
    seasonal = 10 * np.cos(2 * np.pi * (month - 1) / 12) + 5 * np.sin(4 * np.pi * (month - 1) / 12)

    base_load = np.array(hourly_pattern * weekend_factor + seasonal, dtype=np.float64)
    noise = np.random.normal(0, 5, n)

    event_types = ["Sports", "Concert", "Holiday", "Festival", "Conference"]
    events = []
    used_days = set()

    for _ in range(80):
        idx = int(np.random.randint(0, n - 72))
        day_key = date_range[idx].date()
        if day_key in used_days:
            continue
        used_days.add(day_key)
        etype = str(np.random.choice(event_types))
        duration_hours = int(np.random.randint(2, 6))
        spike = float(np.random.uniform(30, 80))
        for h in range(duration_hours):
            if idx + h < n:
                base_load[idx + h] = base_load[idx + h] + spike
        events.append({
            "timestamp": date_range[idx],
            "event_type": etype,
            "duration_hours": duration_hours,
            "spike_kw": spike,
        })

    consumption = np.maximum(base_load + noise, 10)

    df = pd.DataFrame({
        "timestamp":       date_range,
        "consumption_kwh": consumption,
        "hour":            date_range.hour,
        "day_of_week":     date_range.dayofweek,
        "month":           date_range.month,
        "is_weekend":      (date_range.dayofweek >= 5).astype(int),
        "is_holiday":      0,
        "event_flag":      0,
        "event_type":      "None",
    })

    events_df = pd.DataFrame(events)
    for _, ev in events_df.iterrows():
        mask = (
            (df["timestamp"] >= ev["timestamp"])
            & (df["timestamp"] < ev["timestamp"] + timedelta(hours=int(ev["duration_hours"])))
        )
        df.loc[mask, "event_flag"] = 1
        df.loc[mask, "event_type"] = ev["event_type"]

    df.set_index("timestamp", inplace=True)
    return df, events_df


if __name__ == "__main__":
    df, events = generate_electricity_data()
    df.to_csv("data/electricity_data.csv")
    events.to_csv("data/events.csv", index=False)
    print(f"Generated {len(df)} hourly records with {len(events)} events.")
    print(df.head())