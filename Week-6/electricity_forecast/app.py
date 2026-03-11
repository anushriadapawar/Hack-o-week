"""
app.py — Streamlit Dashboard
Electricity Post-Event Forecasting with LSTM
"""

import os, sys, pickle
import numpy as np
import pandas as pd
import torch
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.lstm_model import ElectricityLSTM, prepare_sequences

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚡ Electricity Post-Event Forecast",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background: linear-gradient(135deg, #1e3a5f, #0d2137);
                border-radius: 12px; padding: 12px; border: 1px solid #2d5986; }
    .stMetric label { color: #7ec8f7 !important; font-size: 0.8rem; }
    .stMetric [data-testid="metric-container"] > div { color: #ffffff; }
    h1 { color: #7ec8f7 !important; }
    h2, h3 { color: #a0d4f5 !important; }
    .sidebar-title { font-size: 1.2rem; font-weight: bold; color: #7ec8f7; margin-bottom: 8px; }
    div[data-testid="stSidebar"] { background-color: #0d1b2a; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_PATH   = "models/best_lstm.pt"
SCALER_X     = "models/scaler_X.pkl"
SCALER_Y     = "models/scaler_y.pkl"
META_PATH    = "models/meta.pkl"
DATA_PATH    = "data/electricity_data.csv"
EVENTS_PATH  = "data/events.csv"
DAY_NAMES    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
EVENT_COLORS = {
    "Sports":     "#e74c3c",
    "Concert":    "#9b59b6",
    "Holiday":    "#f1c40f",
    "Festival":   "#e67e22",
    "Conference": "#2ecc71",
    "None":       "#95a5a6",
}


@st.cache_resource
def load_model_and_data():
    """Load model, scalers, metadata, and electricity data (cached)."""
    if not os.path.exists(MODEL_PATH):
        return None, None, None, None, None, None

    with open(META_PATH,  "rb") as f: meta     = pickle.load(f)
    with open(SCALER_X,   "rb") as f: scaler_X = pickle.load(f)
    with open(SCALER_Y,   "rb") as f: scaler_y = pickle.load(f)

    model = ElectricityLSTM(
        input_size      = len(meta["feature_cols"]),
        hidden_size     = meta["hidden_size"],
        num_layers      = meta["num_layers"],
        output_size     = meta["forecast_horizon"],
        dropout         = meta["dropout"],
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    df = pd.read_csv(DATA_PATH, index_col="timestamp", parse_dates=True)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)

    events = pd.read_csv(EVENTS_PATH, parse_dates=["timestamp"]) if os.path.exists(EVENTS_PATH) else pd.DataFrame()

    return model, scaler_X, scaler_y, meta, df, events


def add_cyclical_features(df):
    df = df.copy()
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    return df


def predict(model, scaler_X, scaler_y, meta, df_raw, start_idx):
    """Run LSTM inference from a given index in the raw df."""
    feature_cols     = meta["feature_cols"]
    lookback         = meta["lookback"]
    forecast_horizon = meta["forecast_horizon"]

    df_scaled = df_raw.copy()
    df_scaled[feature_cols] = scaler_X.transform(df_scaled[feature_cols])

    window = df_scaled[feature_cols].values[start_idx - lookback : start_idx]
    x      = torch.tensor(window[np.newaxis], dtype=torch.float32)

    with torch.no_grad():
        pred_scaled = model(x).numpy()[0]

    pred = scaler_y.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()
    return pred


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚡ Dashboard Controls</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**📅 Day Type Filter**")
    day_type = st.radio(
        "Select day type",
        ["All Days", "Weekdays Only", "Weekends Only"],
        index=0,
    )

    st.divider()
    st.markdown("**🎯 Event Type Filter**")
    event_types_all = ["All", "Sports", "Concert", "Holiday", "Festival", "Conference", "No Event"]
    event_filter    = st.selectbox("Filter by event type", event_types_all)

    st.divider()
    st.markdown("**📆 Date Range**")
    date_start = st.date_input("From", value=pd.Timestamp("2023-01-01"))
    date_end   = st.date_input("To",   value=pd.Timestamp("2023-06-30"))

    st.divider()
    st.markdown("**🔮 Forecast Settings**")
    forecast_hours = st.slider("Post-event hours to forecast", 6, 24, 24, step=6)
    selected_event_idx = st.number_input("Event index to inspect (0-based)", min_value=0, value=0, step=1)

    st.divider()
    show_training = st.checkbox("Show training loss curve", value=False)


# ── Main ───────────────────────────────────────────────────────────────────────
st.title("⚡ Post-Event Electricity Demand Forecasting")
st.markdown("LSTM-based hourly prediction — filtered by day type and event category")

# ── Load data ──────────────────────────────────────────────────────────────────
model, scaler_X, scaler_y, meta, df_raw, events = load_model_and_data()

if model is None:
    st.error("⚠️ Model not found! Please run `python train.py` first.")
    st.code("cd electricity_forecast\npython train.py", language="bash")
    st.stop()

st.success("✅ Model loaded successfully!", icon="✅")

# ── Apply day-type filter ──────────────────────────────────────────────────────
df_filtered = df_raw.copy()
df_filtered = df_filtered[
    (df_filtered.index >= pd.Timestamp(date_start)) &
    (df_filtered.index <= pd.Timestamp(date_end) + pd.Timedelta(hours=23))
]

if day_type == "Weekdays Only":
    df_filtered = df_filtered[df_filtered["day_of_week"] < 5]
elif day_type == "Weekends Only":
    df_filtered = df_filtered[df_filtered["day_of_week"] >= 5]

if event_filter == "No Event":
    df_filtered = df_filtered[df_filtered["event_flag"] == 0]
elif event_filter != "All":
    df_filtered = df_filtered[df_filtered["event_type"] == event_filter]

# ── KPI metrics ────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total Records",      f"{len(df_filtered):,}")
col2.metric("⚡ Avg Consumption",    f"{df_filtered['consumption_kwh'].mean():.1f} kWh")
col3.metric("📈 Peak Consumption",   f"{df_filtered['consumption_kwh'].max():.1f} kWh")
col4.metric("🎪 Event Hours",        f"{df_filtered['event_flag'].sum():,}")

st.divider()

# ── Tab layout ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Forecast Explorer", "🔥 Patterns Heatmap", "🎪 Event Impact", "📉 Model Performance"])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Forecast Explorer
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Post-Event LSTM Forecast")
    
    # Filter events in range
    ev_in_range = events[
        (events["timestamp"] >= pd.Timestamp(date_start)) &
        (events["timestamp"] <= pd.Timestamp(date_end))
    ].reset_index(drop=True)

    if event_filter not in ["All", "No Event"]:
        ev_in_range = ev_in_range[ev_in_range["event_type"] == event_filter].reset_index(drop=True)

    if len(ev_in_range) == 0:
        st.warning("No events found for the selected filters.")
    else:
        idx = min(int(selected_event_idx), len(ev_in_range) - 1)
        ev  = ev_in_range.iloc[idx]
        st.info(f"**Event {idx+1}/{len(ev_in_range)}** | Type: `{ev['event_type']}` | Time: `{ev['timestamp']}` | Duration: `{ev['duration_hours']}h`")

        # Find position in df_raw
        ev_ts    = pd.Timestamp(ev["timestamp"])
        ev_end   = ev_ts + pd.Timedelta(hours=int(ev["duration_hours"]))
        pred_end = ev_end + pd.Timedelta(hours=forecast_hours)

        # Idx of event end in df_raw
        raw_idx = df_raw.index.searchsorted(ev_end)
        raw_idx = max(meta["lookback"], raw_idx)
        raw_idx = min(raw_idx, len(df_raw) - forecast_hours)

        pred = predict(model, scaler_X, scaler_y, meta, add_cyclical_features(df_raw), raw_idx)
        pred = pred[:forecast_hours]

        # Build forecast timeline
        forecast_index = pd.date_range(start=ev_end, periods=forecast_hours, freq="H")
        actual_window  = df_raw["consumption_kwh"][ev_ts : pred_end]
        event_window   = df_raw["consumption_kwh"][ev_ts : ev_end]

        fig = go.Figure()

        # Historical before event
        pre_start = ev_ts - pd.Timedelta(hours=24)
        hist_window = df_raw["consumption_kwh"][pre_start : ev_ts]
        fig.add_trace(go.Scatter(
            x=hist_window.index, y=hist_window.values,
            mode="lines", name="Historical (24h pre-event)",
            line=dict(color="#5dade2", width=1.5, dash="dot"),
        ))

        # During event (actual)
        fig.add_trace(go.Scatter(
            x=event_window.index, y=event_window.values,
            mode="lines", name="During Event (Actual)",
            line=dict(color=EVENT_COLORS.get(ev["event_type"], "#e74c3c"), width=2.5),
            fill="tozeroy", fillcolor="rgba(231,76,60,0.08)",
        ))

        # Post-event actual
        post_actual = df_raw["consumption_kwh"][ev_end : pred_end]
        fig.add_trace(go.Scatter(
            x=post_actual.index, y=post_actual.values,
            mode="lines", name="Post-Event Actual",
            line=dict(color="#58d68d", width=2),
        ))

        # LSTM forecast
        fig.add_trace(go.Scatter(
            x=forecast_index[:len(pred)], y=pred,
            mode="lines", name="LSTM Forecast",
            line=dict(color="#f39c12", width=2.5, dash="dash"),
        ))

        # MAE annotation
        min_len = min(len(post_actual), len(pred))
        if min_len > 0:
            mae = np.mean(np.abs(post_actual.values[:min_len] - pred[:min_len]))
            fig.add_annotation(
                x=forecast_index[min_len // 2], y=pred.max() * 1.05,
                text=f"MAE: {mae:.1f} kWh", showarrow=False,
                bgcolor="#f39c12", font=dict(color="black", size=12),
                bordercolor="#f39c12", borderwidth=1,
            )

        # Event shading
        fig.add_vrect(
            x0=ev_ts, x1=ev_end, fillcolor="rgba(231,76,60,0.12)",
            layer="below", line_width=0,
            annotation_text="Event", annotation_position="top left",
            annotation_font_color="#e74c3c",
        )

        fig.update_layout(
            template="plotly_dark",
            title=f"Forecast: Post-{ev['event_type']} Demand Recovery",
            xaxis_title="Time",
            yaxis_title="Consumption (kWh)",
            legend=dict(orientation="h", y=-0.2),
            height=480,
            margin=dict(l=40, r=40, t=60, b=80),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Forecast table
        with st.expander("📋 Forecast vs Actual Table"):
            rows = []
            for i in range(min_len):
                rows.append({
                    "Hour": i + 1,
                    "Timestamp": str(forecast_index[i]),
                    "Forecast (kWh)": round(float(pred[i]), 2),
                    "Actual (kWh)": round(float(post_actual.values[i]), 2),
                    "Error (kWh)": round(float(pred[i] - post_actual.values[i]), 2),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Heatmap
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Hourly Consumption Heatmap by Day of Week")

    pivot = df_filtered.groupby(["day_of_week", "hour"])["consumption_kwh"].mean().reset_index()
    pivot_table = pivot.pivot(index="day_of_week", columns="hour", values="consumption_kwh")

    pivot_table.index = [DAY_NAMES[i] for i in pivot_table.index]

    fig_hm = px.imshow(
        pivot_table,
        labels=dict(x="Hour of Day", y="Day of Week", color="Avg kWh"),
        color_continuous_scale="Viridis",
        title=f"Average Hourly Consumption — {day_type}",
        aspect="auto",
    )
    fig_hm.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_hm, use_container_width=True)

    # Daily distribution
    st.subheader("Daily Consumption Distribution")
    fig_box = px.box(
        df_filtered.reset_index(),
        x="day_of_week", y="consumption_kwh",
        color="day_of_week",
        labels={"day_of_week": "Day (0=Mon)", "consumption_kwh": "Consumption (kWh)"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_box.update_layout(template="plotly_dark", height=350, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Event Impact
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Event vs. Non-Event Consumption Comparison")

    c1, c2 = st.columns(2)

    with c1:
        avg_by_type = df_raw.groupby("event_type")["consumption_kwh"].mean().reset_index()
        avg_by_type.columns = ["Event Type", "Avg kWh"]
        avg_by_type["Color"] = avg_by_type["Event Type"].map(EVENT_COLORS).fillna("#aaaaaa")
        fig_bar = px.bar(
            avg_by_type, x="Event Type", y="Avg kWh",
            color="Event Type",
            color_discrete_map=EVENT_COLORS,
            title="Average Consumption by Event Type",
        )
        fig_bar.update_layout(template="plotly_dark", height=380, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        hourly_event = df_raw[df_raw["event_flag"] == 1].groupby("hour")["consumption_kwh"].mean()
        hourly_none  = df_raw[df_raw["event_flag"] == 0].groupby("hour")["consumption_kwh"].mean()

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=hourly_event.index, y=hourly_event.values,
                                      name="During Events", line=dict(color="#e74c3c", width=2)))
        fig_line.add_trace(go.Scatter(x=hourly_none.index, y=hourly_none.values,
                                      name="Normal Days",  line=dict(color="#5dade2", width=2)))
        fig_line.update_layout(
            template="plotly_dark", height=380,
            title="Avg Hourly Load: Event vs Normal",
            xaxis_title="Hour of Day", yaxis_title="Avg kWh",
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # Spike analysis
    st.subheader("Event Spike Distribution")
    if os.path.exists(EVENTS_PATH):
        ev_df = pd.read_csv(EVENTS_PATH)
        fig_hist = px.histogram(
            ev_df, x="spike_kw", color="event_type",
            barmode="overlay", nbins=20,
            color_discrete_map=EVENT_COLORS,
            title="Distribution of Event Demand Spikes (kWh)",
        )
        fig_hist.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_hist, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — Model Performance
# ──────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("LSTM Training History")

    if show_training and meta.get("history"):
        history = meta["history"]
        epochs  = list(range(1, len(history["train"]) + 1))
        fig_loss = go.Figure()
        fig_loss.add_trace(go.Scatter(x=epochs, y=history["train"], name="Train Loss",
                                      line=dict(color="#5dade2", width=2)))
        fig_loss.add_trace(go.Scatter(x=epochs, y=history["val"],   name="Val Loss",
                                      line=dict(color="#f39c12", width=2)))
        fig_loss.update_layout(
            template="plotly_dark", height=400,
            title="Training vs Validation MSE Loss",
            xaxis_title="Epoch", yaxis_title="MSE Loss",
        )
        st.plotly_chart(fig_loss, use_container_width=True)
    else:
        st.info("Enable 'Show training loss curve' in the sidebar to view this chart.")

    st.subheader("Model Architecture")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
| Parameter | Value |
|-----------|-------|
| Model type | LSTM |
| Lookback window | {meta['lookback']} hours |
| Forecast horizon | {meta['forecast_horizon']} hours |
| Hidden size | {meta['hidden_size']} |
| LSTM layers | {meta['num_layers']} |
| Dropout | {meta['dropout']} |
        """)
    with col_b:
        st.markdown(f"""
| Feature | Description |
|---------|-------------|
| consumption_kwh | Target + input feature |
| hour | Hour of day (0–23) |
| day_of_week | Mon=0, Sun=6 |
| month | 1–12 |
| is_weekend | Binary flag |
| is_holiday | Binary flag |
| event_flag | Event in progress |
| hour_sin | Cyclical hour encoding |
        """)

    st.subheader("Bulk Evaluation on Filtered Data")
    if st.button("▶ Run Evaluation on 30 Sample Events"):
        ev_sample = events.sample(min(30, len(events)), random_state=0)
        maes = []
        df_cyc = add_cyclical_features(df_raw)
        for _, ev in ev_sample.iterrows():
            ev_end  = pd.Timestamp(ev["timestamp"]) + pd.Timedelta(hours=int(ev["duration_hours"]))
            raw_idx = df_raw.index.searchsorted(ev_end)
            raw_idx = max(meta["lookback"], min(raw_idx, len(df_raw) - meta["forecast_horizon"]))
            pred = predict(model, scaler_X, scaler_y, meta, df_cyc, raw_idx)
            actual = df_raw["consumption_kwh"].values[raw_idx : raw_idx + forecast_hours]
            if len(actual) > 0:
                maes.append(np.mean(np.abs(pred[:len(actual)] - actual)))

        if maes:
            st.metric("Mean Absolute Error (avg over 30 events)", f"{np.mean(maes):.2f} kWh")
            fig_mae = px.histogram(maes, nbins=15, title="MAE Distribution across Events",
                                   labels={"value": "MAE (kWh)"}, color_discrete_sequence=["#5dade2"])
            fig_mae.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig_mae, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small>⚡ Electricity LSTM Dashboard — built with Streamlit + PyTorch + Plotly</small></center>",
    unsafe_allow_html=True,
)
