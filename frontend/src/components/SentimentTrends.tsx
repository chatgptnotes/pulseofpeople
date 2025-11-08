import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts'
import { mockTrendData } from '../data/mockData'

export default function SentimentTrends() {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Trends Over Time</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={mockTrendData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              domain={[0, 1]}
              tick={{ fontSize: 12 }}
              label={{ value: 'Sentiment Score', angle: -90, position: 'insideLeft' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="jobs" 
              stroke="#22c55e" 
              strokeWidth={2}
              name="Jobs"
              dot={{ r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="infrastructure" 
              stroke="#f59e0b" 
              strokeWidth={2}
              name="Infrastructure"
              dot={{ r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="health" 
              stroke="#3b82f6" 
              strokeWidth={2}
              name="Health"
              dot={{ r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="education" 
              stroke="#8b5cf6" 
              strokeWidth={2}
              name="Education"
              dot={{ r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="lawOrder" 
              stroke="#ef4444" 
              strokeWidth={2}
              name="Law & Order"
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}