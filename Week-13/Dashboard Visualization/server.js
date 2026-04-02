import express from 'express';
import cors from 'cors';
// import path from 'path'; // unused

const app = express();
const PORT = 5000;

app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}));
app.use(express.static('public'));
app.use(express.json());

// Catch-all for root to prevent 404 on browser devtools probes
app.get('/', (req, res) => {
  res.json({ message: 'Dashboard Backend API - Use /api/activity for data' });
});

// Mock 'decrypted' data sim
const decryptData = (data) => data.replace('encrypted_', 'decrypted_');

const dailyActivity = Array.from({length: 30}, (_, i) => ({
  date: new Date(Date.now() - i * 24*60*60*1000).toISOString().split('T')[0],
  steps: 7000 + Math.floor(Math.random() * 4000),
  views: 1000 + Math.floor(Math.random() * 1000),
  sales: 200 + Math.floor(Math.random() * 200)
})).reverse();

app.get('/api/activity', (req, res) => {
  const decrypted = decryptData('encrypted_daily_activity');
  res.json({
    status: 'success',
    decrypted,
    data: dailyActivity,
    trends: {
      avgSteps: dailyActivity.reduce((a, b) => a + b.steps, 0) / dailyActivity.length,
      totalViews: dailyActivity.reduce((a, b) => a + b.views, 0),
    }
  });
});

app.listen(PORT, () => {
  console.log(`Mock Backend (Decrypted Data API) running on http://localhost:${PORT}`);
  console.log(`API endpoint: http://localhost:${PORT}/api/activity`);
});

