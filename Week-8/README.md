# 🚗 Smart Parking Lot Lighting Forecast using Polynomial Regression

A **data-driven smart parking system** that predicts parking lot occupancy using **sensor data** and dynamically determines **optimal lighting levels** to improve energy efficiency and parking management.

This project demonstrates how **machine learning and time-series sensor data** can be used to build **intelligent infrastructure for smart cities**.

---

# 📌 Project Overview

Modern parking systems often waste electricity by keeping lights fully active even when parking areas are empty.

This project proposes a **sensor-based predictive system** that:

- Uses **parking bay sensor data**
- Predicts **future vehicle occupancy**
- Adjusts **lighting levels dynamically**
- Detects **abnormal parking patterns**

The system combines **data preprocessing, time-series aggregation, polynomial regression, and anomaly detection** to simulate a **smart parking lighting control system**.

---

# 🧠 Key Features

✔ Sensor-based vehicle detection  
✔ Time-series parking occupancy analysis  
✔ Polynomial Regression forecasting  
✔ Dynamic lighting level prediction  
✔ Anomaly detection in parking activity  
✔ Real-time parking monitoring visualization  

---

# ⚙️ Technologies Used

| Technology | Purpose |
|------------|--------|
| Python | Core programming language |
| Pandas | Data preprocessing and aggregation |
| NumPy | Numerical computation |
| Scikit-learn | Machine learning model |
| Matplotlib | Forecast visualization |
| Plotly | Interactive real-time charts |
| Google Colab | Development environment |

---

# 📂 Dataset

Dataset used:

**On-Street Parking Bay Sensors Dataset**

The dataset contains sensor updates from multiple parking bays including:

- `status_timestamp` → Time of sensor update
- `status_description` → Parking status (Present / Unoccupied)
- parking bay sensor events

From this data, the system calculates **parking lot occupancy over time**.


---

# 🤖 Machine Learning Model

The project uses **Polynomial Regression** to model non-linear parking occupancy trends.

Steps involved:

1. Create a **time index feature**
2. Apply **Polynomial Feature Transformation**
3. Train **Linear Regression on polynomial features**
4. Predict **future vehicle counts**

This helps capture **non-linear parking behavior patterns over time**.

---

# 💡 Smart Lighting Logic

Based on predicted vehicle counts, lighting levels are adjusted:

| Vehicle Count | Lighting Level |
|---------------|---------------|
| Low traffic | Low |
| Moderate traffic | Medium |
| Heavy traffic | High |

This approach helps simulate **energy-efficient smart parking infrastructure**.

---

# 🚨 Anomaly Detection

The system also detects unusual parking activity.
