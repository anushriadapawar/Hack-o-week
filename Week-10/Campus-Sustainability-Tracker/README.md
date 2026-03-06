# Campus-Wide Sustainability Tracker

A comprehensive dashboard for analyzing and predicting campus energy and sustainability metrics using advanced data analysis and machine learning models.

## 📋 Features

### Dashboard Metrics (KPIs)
- **Total Energy Usage**: Track cumulative energy consumption across campus
- **Carbon Emissions**: Monitor total carbon footprint
- **Carbon Savings Potential**: Estimate potential CO₂ reductions through renewable energy
- **Water Consumption**: Track water usage metrics
- **Waste Generation**: Monitor waste production
- **Average Daily Energy**: Analyze average energy consumption patterns

### Interactive Charts
- **Energy Usage Over Time**: Line chart showing energy consumption trends
- **Carbon Emissions Trend**: Visualize carbon footprint evolution
- **Waste Generation Chart**: Bar chart for waste metrics
- **Water Consumption**: Track water usage patterns

### Predictive Analytics
- **Linear Regression**: 30-day energy consumption forecast
- **Moving Average (7-Day)**: Smoothed trend analysis
- **Exponential Smoothing**: Advanced trend forecasting with α=0.3

### Building-Level Analysis
- Drill-down feature for building-specific KPIs
- Compare energy usage, carbon emissions, and waste by building
- Analyze patterns for individual facilities

### File Upload
- Upload custom CSV datasets
- Flexible data import for custom campus data
- Support for multiple sustainability metrics

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python Flask
- **Data Analysis**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (Linear Regression)
- **Visualization**: Chart.js
- **Design**: Responsive CSS with green sustainability theme

## 📦 Installation & Setup

### Requirements
- Python 3.7+
- pip (Python package manager)

### Step 1: Navigate to Project Directory
```bash
cd Campus-Sustainability-Tracker
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected packages:**
- Flask==2.3.3
- pandas==2.0.3
- numpy==1.24.3
- scikit-learn==1.3.0

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Access the Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 📊 Project Structure

```
Campus-Sustainability-Tracker/
├── app.py                          # Flask backend application
├── dataset.csv                     # Sample sustainability data
├── requirements.txt                # Python dependencies
│
├── templates/
│   └── index.html                 # Main dashboard HTML
│
└── static/
    ├── style.css                  # Green-themed styling
    └── script.js                  # JavaScript for charts & interactions
```

## 🎨 Dashboard UI

### Color Scheme (Sustainability Green Theme)
- Primary Green: #2ecc71
- Dark Green: #27ae60
- Accent Teal: #1abc9c
- Responsive design for mobile and desktop

### Layout Sections
1. **Header**: Title, upload, and quick actions
2. **KPI Cards**: 6 key metrics with icons
3. **Filter Section**: Building-wise data filtering
4. **Charts Grid**: 4 interactive visualizations
5. **Predictive Analytics**: Forecast models and trends
6. **Building Details**: Drill-down analytics
7. **Footer**: Project information

## 📈 Data Format

### CSV Structure
Your custom dataset should include these columns:
```csv
Date,Building,Energy_Usage_kWh,Water_Usage_Liters,Waste_kg,Carbon_Emissions
```

### Sample Data
- Date: YYYY-MM-DD format
- Building: Name of campus building
- Energy_Usage_kWh: Daily energy consumption in kilowatt-hours
- Water_Usage_Liters: Daily water consumption in liters
- Waste_kg: Daily waste generated in kilograms
- Carbon_Emissions: Daily carbon emissions in kg CO₂

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard page |
| `/api/load-data` | POST | Load default dataset |
| `/api/upload` | POST | Upload custom CSV file |
| `/api/forecast` | GET | Get 30-day energy forecast |
| `/api/smoothing` | GET | Get 7-day moving average |
| `/api/exponential-smoothing` | GET | Get exponential smoothing |
| `/api/building/<name>` | GET | Get building-specific data |

## 📊 Predictive Models

### 1. Linear Regression
- Forecasts future energy consumption
- Uses historical trends to predict 30-day outlook
- Based on scikit-learn's LinearRegression model

### 2. Moving Average
- 7-day window for trend smoothing
- Removes noise from daily fluctuations
- Helps identify underlying patterns

### 3. Exponential Smoothing
- Advanced time series forecasting
- Alpha (α) = 0.3 for balanced weighting
- Recent data weighted more heavily than older data

## 🚀 Usage Guide

### 1. Initial Load
Click **"Load Default Data"** to populate the dashboard with sample data (60 days of campus data).

### 2. Upload Custom Data
Click **"Upload CSV"** to import your own sustainability dataset.

### 3. View Metrics
- KPI cards display aggregate metrics
- Charts update automatically with uploaded data

### 4. Filter by Building
1. Select a building from the dropdown
2. Click **"Apply Filter"**
3. View building-specific KPIs in the details section

### 5. Run Predictions
- **30-Day Forecast**: Linear regression-based energy prediction
- **Moving Average**: 7-day smoothed trend
- **Exponential Smoothing**: Advanced trend analysis

## 📝 Sustainability Calculations

### Carbon Savings Estimate
```
Estimated Savings = Total Carbon Emissions × 25%
(Assumes 25% reduction through renewable energy adoption)
```

### Average Energy/Day
```
Average = Total Energy Usage / Number of Days
```

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is busy, modify `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change to 5001
```

### Module Import Errors
Ensure all dependencies are installed:
```bash
pip install --upgrade -r requirements.txt
```

### CSV Upload Issues
- Verify CSV has required columns
- Check date format (YYYY-MM-DD)
- Ensure numeric values are properly formatted

## 🔐 Security Notes

- This application is for educational/development purposes
- Not recommended for production without additional security measures
- Disable Flask debug mode in production

## 📚 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Chart.js Documentation](https://www.chartjs.org/)

## 🎯 Future Enhancements

- Database integration (SQL/MongoDB)
- User authentication system
- Advanced statistical models (ARIMA, Prophet)
- Real-time data streaming
- Mobile app version
- API integration with IoT sensors
- Sustainability recommendations engine

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and enhance this project for your campus sustainability initiatives.

---

**Created**: 2024
**Developed for**: Campus Sustainability Tracking and Analysis
**Dashboard URL**: http://127.0.0.1:5000
