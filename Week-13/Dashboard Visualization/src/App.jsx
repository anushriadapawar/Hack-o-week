import { useState, useEffect } from 'react';
import axios from 'axios';
import LineChartComponent from './components/LineChart';
import BarChartComponent from './components/BarChart';
import PieChartComponent from './components/PieChart';
import './App.css';

function App() {
  const [activityData, setActivityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/activity');
        setActivityData(response.data.data);
        console.log('Fetched decrypted data:', response.data);
      } catch (err) {
        setError('Failed to fetch data (Backend at localhost:5000 required)');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading dashboard data...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
      <header className="mb-12">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
          Dashboard Visualization
        </h1>
        <p className="text-xl text-gray-600">Daily Activity Trends - Decrypted Data</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
        {/* Line Chart - Trends */}
        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-white/50">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">Daily Trends</h2>
          <LineChartComponent data={activityData} />
        </div>

        {/* Bar Chart - Sales */}
        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-white/50">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">Sales Performance</h2>
          <BarChartComponent data={activityData} />
        </div>

        {/* Pie Chart - Averages */}
        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-white/50">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">Metrics Summary</h2>
          <PieChartComponent data={activityData} />
        </div>
      </div>

      <footer className="mt-16 text-center text-gray-500">
        Data auto-refreshes every 30s from backend API. Backend: http://localhost:5000
      </footer>
    </div>
  );
}

export default App;

