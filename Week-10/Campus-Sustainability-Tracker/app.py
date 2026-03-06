from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os
import json

class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy data types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = NumpyEncoder

# Global data storage
data = None
dataset_file = 'dataset.csv'

def load_dataset():
    """Load the CSV dataset"""
    global data
    if os.path.exists(dataset_file):
        data = pd.read_csv(dataset_file)
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.sort_values('Date')
        return True
    return False

def calculate_kpis(df):
    """Calculate key sustainability KPIs"""
    total_energy = df['Energy_Usage_kWh'].sum()
    total_carbon = df['Carbon_Emissions'].sum()
    total_water = df['Water_Usage_Liters'].sum()
    total_waste = df['Waste_kg'].sum()
    
    # Estimate carbon savings (assuming 25% reduction if using renewable energy)
    carbon_savings = total_carbon * 0.25
    
    avg_energy = df['Energy_Usage_kWh'].mean()
    avg_carbon = df['Carbon_Emissions'].mean()
    
    return {
        'total_energy': float(round(total_energy, 2)),
        'total_carbon': float(round(total_carbon, 2)),
        'total_water': float(round(total_water, 2)),
        'total_waste': float(round(total_waste, 2)),
        'carbon_savings': float(round(carbon_savings, 2)),
        'avg_energy': float(round(avg_energy, 2)),
        'avg_carbon': float(round(avg_carbon, 2))
    }

def linear_regression_forecast(df, days_ahead=30):
    """Forecast energy consumption using linear regression"""
    # Prepare data
    df_sorted = df.sort_values('Date')
    X = np.arange(len(df_sorted)).reshape(-1, 1)
    y = df_sorted['Energy_Usage_kWh'].values
    
    # Fit model
    model = LinearRegression()
    model.fit(X, y)
    
    # Forecast
    future_X = np.arange(len(df_sorted), len(df_sorted) + days_ahead).reshape(-1, 1)
    predictions = model.predict(future_X)
    
    # Generate dates
    last_date = df_sorted['Date'].max()
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
    
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
        'predictions': [float(max(0, round(p, 2))) for p in predictions]
    }

def moving_average(df, window=7):
    """Calculate moving average for smoothing"""
    df_sorted = df.sort_values('Date')
    ma = df_sorted['Energy_Usage_kWh'].rolling(window=window).mean()
    return {
        'dates': df_sorted['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'values': [float(x) if pd.notna(x) else float(df_sorted['Energy_Usage_kWh'].iloc[i]) 
                   for i, x in enumerate(ma)]
    }

def exponential_smoothing(df, alpha=0.3):
    """Exponential smoothing for trend analysis"""
    df_sorted = df.sort_values('Date')
    energy = df_sorted['Energy_Usage_kWh'].values
    
    # Manual exponential smoothing
    result = [float(energy[0])]
    for i in range(1, len(energy)):
        smoothed = alpha * energy[i] + (1 - alpha) * result[-1]
        result.append(float(smoothed))
    
    return {
        'dates': df_sorted['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'values': [round(v, 2) for v in result]
    }

def get_building_data(df, building_name):
    """Get data for a specific building"""
    building_df = df[df['Building'] == building_name]
    if building_df.empty:
        return None
    
    return {
        'building': str(building_name),
        'total_energy': float(round(building_df['Energy_Usage_kWh'].sum(), 2)),
        'total_carbon': float(round(building_df['Carbon_Emissions'].sum(), 2)),
        'total_water': float(round(building_df['Water_Usage_Liters'].sum(), 2)),
        'total_waste': float(round(building_df['Waste_kg'].sum(), 2)),
        'avg_energy': float(round(building_df['Energy_Usage_kWh'].mean(), 2)),
        'max_energy': float(round(building_df['Energy_Usage_kWh'].max(), 2))
    }

def get_time_series_data(df):
    """Prepare time series data for charts"""
    df_sorted = df.sort_values('Date')
    
    return {
        'dates': df_sorted['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'energy': [float(x) for x in df_sorted['Energy_Usage_kWh'].round(2).values],
        'carbon': [float(x) for x in df_sorted['Carbon_Emissions'].round(2).values],
        'waste': [float(x) for x in df_sorted['Waste_kg'].round(2).values],
        'water': [float(x) for x in df_sorted['Water_Usage_Liters'].round(2).values]
    }

@app.route('/')
def index():
    """Render dashboard"""
    return render_template('index.html')

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Load dataset and calculate initial metrics"""
    if load_dataset():
        kpis = calculate_kpis(data)
        time_series = get_time_series_data(data)
        buildings = data['Building'].unique().tolist()
        
        return jsonify({
            'success': True,
            'kpis': kpis,
            'time_series': time_series,
            'buildings': buildings
        })
    return jsonify({'success': False, 'message': 'Dataset not found'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and file.filename.endswith('.csv'):
        try:
            file.save(dataset_file)
            if load_dataset():
                kpis = calculate_kpis(data)
                time_series = get_time_series_data(data)
                buildings = data['Building'].unique().tolist()
                
                return jsonify({
                    'success': True,
                    'kpis': kpis,
                    'time_series': time_series,
                    'buildings': buildings
                })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': False, 'message': 'Invalid file format'})

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    """Get energy consumption forecast"""
    if data is None:
        return jsonify({'success': False, 'message': 'No data loaded'})
    
    forecast = linear_regression_forecast(data, days_ahead=30)
    return jsonify({'success': True, 'forecast': forecast})

@app.route('/api/smoothing', methods=['GET'])
def get_smoothing():
    """Get moving average smoothing"""
    if data is None:
        return jsonify({'success': False, 'message': 'No data loaded'})
    
    ma = moving_average(data, window=7)
    return jsonify({'success': True, 'moving_average': ma})

@app.route('/api/exponential-smoothing', methods=['GET'])
def get_exp_smoothing():
    """Get exponential smoothing"""
    if data is None:
        return jsonify({'success': False, 'message': 'No data loaded'})
    
    exp_smooth = exponential_smoothing(data, alpha=0.3)
    return jsonify({'success': True, 'exponential_smoothing': exp_smooth})

@app.route('/api/building/<building_name>', methods=['GET'])
def get_building(building_name):
    """Get data for specific building"""
    if data is None:
        return jsonify({'success': False, 'message': 'No data loaded'})
    
    building_data = get_building_data(data, building_name)
    if building_data:
        return jsonify({'success': True, 'data': building_data})
    return jsonify({'success': False, 'message': 'Building not found'})

if __name__ == '__main__':
    # Load dataset on startup
    load_dataset()
    app.run(debug=True, host='127.0.0.1', port=5000)
