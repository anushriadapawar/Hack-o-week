import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const PieChartComponent = ({ data }) => {
// const recentData = data.slice(-7); // Last 7 days (unused removed)
  const summary = [
    { name: 'Avg Steps', value: data.reduce((a, b) => a + b.steps, 0) / data.length },
    { name: 'Avg Views', value: data.reduce((a, b) => a + b.views, 0) / data.length },
    { name: 'Avg Sales', value: data.reduce((a, b) => a + b.sales, 0) / data.length },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={summary}
          cx="50%"
          cy="50%"
          outerRadius={80}
          dataKey="value"
          label
        >
          {summary.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default PieChartComponent;

