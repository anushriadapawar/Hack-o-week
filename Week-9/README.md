# Hostel Laundry Demand Prediction and Forecasting

A machine learning project that predicts washing machine usage in a hostel environment and forecasts future laundry demand.  
The project uses a classification model to determine usage levels and a time-series model to forecast future demand.

---

## Project Overview

Hostel laundry facilities often experience uneven demand during the day. At certain times machines remain unused, while during peak hours students may have to wait.

This project analyzes washing machine usage data and applies machine learning techniques to:

- Predict whether laundry demand will be **Low, Medium, or Peak**
- Forecast future washing machine usage
- Help optimize machine availability in hostels

The system combines **classification** and **time-series forecasting** techniques to provide both real-time predictions and future demand insights.

---

## Technologies Used

| Technology | Purpose |
|------------|--------|
| Python | Programming language |
| Pandas | Data processing and analysis |
| NumPy | Numerical computations |
| Matplotlib | Data visualization |
| Scikit-learn | Machine learning algorithms |
| Prophet | Time series forecasting |

---

## Dataset

The dataset used in this project is synthetically generated to simulate hostel laundry usage.

### Dataset Features

| Feature | Description |
|--------|-------------|
| Timestamp | Date and time of laundry record |
| Machine ID | Identifier for washing machines |
| Loads | Number of washing loads recorded |
| Occupancy | Number of students in hostel |
| Hour | Hour extracted from timestamp |
| Day of Week | Day number of the week |
| Usage Category | Laundry demand level |
| Usage Encoded | Numerical representation of usage category |

### Usage Categories

Laundry usage is divided into three levels:

| Category | Description |
|---------|-------------|
| Low | Very few washing loads |
| Medium | Moderate laundry demand |
| Peak | High laundry usage |

These categories help the model classify usage patterns based on time and hostel occupancy.

---

## Methodology

The project follows these major steps:

### 1. Data Generation

A dataset containing hourly records of washing machine activity is created to simulate real hostel laundry behavior.

### 2. Data Preprocessing

Important features such as **hour of the day** and **day of the week** are extracted from the timestamp.  
These features help identify patterns in laundry usage.

### 3. Usage Classification

A **Naive Bayes classification model** is used to predict the laundry usage category based on:

- Hour of the day
- Day of the week
- Hostel occupancy

The model learns patterns in the dataset and predicts whether usage will be **Low, Medium, or Peak**.

### 4. Model Evaluation

The classification model is evaluated using common machine learning metrics including:

- Precision
- Recall
- F1-score
- Accuracy

These metrics help measure how well the model predicts laundry demand.

### 5. Demand Forecasting

To predict future washing machine demand, the project uses **Prophet**, a time-series forecasting library.

The forecasting model analyzes historical washing load data and predicts future trends in laundry usage.

### 6. Visualization

The predicted results are visualized through graphs that show:

- Daily usage patterns
- Trend of washing demand over time
- Predicted future laundry demand

---

## Applications

This project can be applied in several real-world scenarios:

- Smart hostel infrastructure
- University campus resource planning
- Automated laundry scheduling
- Predictive facility management

By forecasting demand, administrators can improve machine availability and reduce waiting time for students.

---

## Project Structure
