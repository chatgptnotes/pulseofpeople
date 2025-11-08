import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts'
import { mockSentimentData } from '../data/mockData'

export default function SentimentByIssue() {
  const data = mockSentimentData.map(item => ({
    issue: item.issue,
    sentiment: item.sentiment,
    color: item.sentiment > 0.6 ? '#22c55e' : item.sentiment > 0.5 ? '#3b82f6' : '#ef4444'
  }))

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Sentiment by Issue</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis 
              dataKey="issue" 
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              domain={[0, 1]}
              tick={{ fontSize: 12 }}
              label={{ value: 'Sentiment Score', angle: -90, position: 'insideLeft' }}
            />
            <Bar 
              dataKey="sentiment" 
              fill="#3b82f6"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}