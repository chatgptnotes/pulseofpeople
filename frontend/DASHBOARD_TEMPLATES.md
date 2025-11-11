# Dashboard Implementation Templates

Quick-start templates for implementing the remaining 5 dashboards using the established patterns.

## Template 1: Manager District Dashboard

```tsx
/**
 * Manager District Dashboard
 * District-level operations and team management
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Users, MapPin, Target, Activity, FileText, TrendingUp } from 'lucide-react';
import {
  useDistrictAnalytics,
  useConstituencies,
  useFeedbackList,
  useFieldReports,
} from '../../hooks/useApiHooks';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { StatCard } from '../../components/charts/StatCard';
import { GaugeChart } from '../../components/charts/GaugeChart';
import { BarChart } from '../../components/charts/BarChart';
import { LineChart } from '../../components/charts/LineChart';
import { ExportButton } from '../../components/common/ExportButton';
import { DateRangeFilter } from '../../components/filters/DateRangeFilter';
import { format, subDays } from 'date-fns';

export default function ManagerDistrictDashboard() {
  const { user } = useAuth();
  const districtId = user?.district_id || '1'; // Get from user profile

  const { data: analytics, isLoading, error, refetch } = useDistrictAnalytics(districtId);
  const { data: constituencies } = useConstituencies('TN', 'assembly');
  const { data: feedback } = useFeedbackList({ district_id: districtId, limit: 20 });
  const { data: reports } = useFieldReports(false);

  if (isLoading) return <LoadingSkeleton type="stats" count={4} />;
  if (error) return <ErrorMessage error={error} retry={refetch} />;

  const stats = {
    districtSentiment: (analytics?.sentiment_score || 0.68) * 100,
    totalFeedback: analytics?.total_feedback || 0,
    constituenciesActive: constituencies?.filter((c: any) => c.is_active).length || 0,
    totalConstituencies: constituencies?.length || 16,
    activeAnalysts: 12, // TODO: Add team members endpoint
    activeBoothAgents: 450,
    coveragePercentage: 67,
  };

  // Mock team performance data
  const teamPerformance = [
    { name: 'Analyst A', tasks: 25, reports: 18, rating: 4.8 },
    { name: 'Analyst B', tasks: 22, reports: 20, rating: 4.5 },
    { name: 'Analyst C', tasks: 20, reports: 15, rating: 4.2 },
  ];

  // Constituency sentiment data
  const constituencyData = constituencies?.slice(0, 10).map((c: any) => ({
    name: c.name,
    sentiment: 50 + Math.random() * 40,
    feedback: Math.floor(50 + Math.random() * 200),
  })) || [];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {analytics?.district_name || 'District'} Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Manage operations across {stats.totalConstituencies} constituencies
          </p>
        </div>
        <ExportButton
          data={constituencyData}
          filename={`district-analytics-${format(new Date(), 'yyyy-MM-dd')}`}
        />
      </div>

      {/* Sentiment Gauge + Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <GaugeChart
          value={stats.districtSentiment}
          title="District Sentiment"
          subtitle="Overall approval"
        />

        <div className="col-span-2 grid grid-cols-2 gap-4">
          <StatCard
            title="Total Feedback"
            value={stats.totalFeedback}
            icon={FileText}
            iconColor="blue"
            trend={{ value: 15, label: 'vs last week' }}
          />
          <StatCard
            title="Active Constituencies"
            value={`${stats.constituenciesActive}/${stats.totalConstituencies}`}
            icon={MapPin}
            iconColor="green"
          />
          <StatCard
            title="Team Members"
            value={stats.activeAnalysts}
            icon={Users}
            iconColor="purple"
          />
          <StatCard
            title="Coverage"
            value={`${stats.coveragePercentage}%`}
            icon={Target}
            iconColor="indigo"
          />
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <BarChart
          data={constituencyData}
          xKey="name"
          yKey="sentiment"
          title="Constituency Sentiment Comparison"
          colorByValue={true}
          height={350}
        />

        <BarChart
          data={teamPerformance}
          xKey="name"
          yKey="tasks"
          title="Team Performance"
          color="#8b5cf6"
          height={350}
        />
      </div>

      {/* Team Members Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Team Performance</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Name</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Tasks</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Reports</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Rating</th>
            </tr>
          </thead>
          <tbody>
            {teamPerformance.map((member, i) => (
              <tr key={i} className="border-b border-gray-100">
                <td className="py-3 px-4 font-medium">{member.name}</td>
                <td className="py-3 px-4">{member.tasks}</td>
                <td className="py-3 px-4">{member.reports}</td>
                <td className="py-3 px-4">⭐ {member.rating}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Recent Field Reports */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Field Reports</h2>
        <div className="space-y-3">
          {reports?.results?.slice(0, 5).map((report: any) => (
            <div key={report.id} className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900">{report.title}</h3>
              <p className="text-sm text-gray-600 mt-1">
                {report.constituency_name} • {format(new Date(report.created_at), 'MMM dd, yyyy')}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## Template 2: Analyst Constituency Dashboard

```tsx
/**
 * Analyst Constituency Dashboard
 * Constituency-level deep analytics
 */

import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { TrendingUp, Users, MessageSquare, Target } from 'lucide-react';
import {
  useConstituencyAnalytics,
  useFeedbackList,
  useVoterSegments,
} from '../../hooks/useApiHooks';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { StatCard } from '../../components/charts/StatCard';
import { GaugeChart } from '../../components/charts/GaugeChart';
import { PieChart } from '../../components/charts/PieChart';
import { LineChart } from '../../components/charts/LineChart';
import { format, subDays } from 'date-fns';

export default function AnalystConstituencyDashboard() {
  const { user } = useAuth();
  const constituencyCode = user?.constituency_code || 'TN001';

  const { data: analytics, isLoading, error } = useConstituencyAnalytics(constituencyCode);
  const { data: feedback } = useFeedbackList({ limit: 20 });
  const { data: segments } = useVoterSegments();

  if (isLoading) return <LoadingSkeleton type="stats" count={4} />;
  if (error) return <ErrorMessage error={error} />;

  const stats = {
    sentiment: (analytics?.sentiment_score || 0.65) * 100,
    totalVoters: analytics?.total_voters || 0,
    interactionsThisMonth: analytics?.interactions_count || 0,
    pendingFollowups: analytics?.pending_followups || 0,
  };

  // Demographics data
  const demographicsData = [
    { name: 'Youth (18-35)', value: 35 },
    { name: 'Middle-aged (36-55)', value: 40 },
    { name: 'Senior (55+)', value: 25 },
  ];

  // Sentiment trend
  const sentimentTrend = Array.from({ length: 7 }, (_, i) => ({
    date: format(subDays(new Date(), 6 - i), 'MMM dd'),
    sentiment: 60 + Math.random() * 15,
  }));

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        {analytics?.constituency_name || 'Constituency'} Analytics
      </h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="md:col-span-1">
          <GaugeChart value={stats.sentiment} title="Sentiment Score" size={200} />
        </div>

        <StatCard
          title="Total Voters"
          value={stats.totalVoters.toLocaleString()}
          icon={Users}
          iconColor="blue"
        />
        <StatCard
          title="Interactions (This Month)"
          value={stats.interactionsThisMonth}
          icon={MessageSquare}
          iconColor="green"
        />
        <StatCard
          title="Pending Follow-ups"
          value={stats.pendingFollowups}
          icon={Target}
          iconColor="orange"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <LineChart
          data={sentimentTrend}
          xKey="date"
          yKey="sentiment"
          title="Sentiment Trend (Last 7 Days)"
          color="#3b82f6"
          formatYAxis={(v) => `${v}%`}
        />

        <PieChart
          data={demographicsData}
          dataKey="value"
          nameKey="name"
          title="Voter Demographics"
        />
      </div>

      {/* Recent Feedback */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Voter Feedback</h2>
        <div className="space-y-3">
          {feedback?.results?.slice(0, 5).map((item: any) => (
            <div key={item.id} className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-800">{item.message_text}</p>
              <p className="text-xs text-gray-500 mt-2">
                {item.citizen_name} • {format(new Date(item.created_at), 'MMM dd, yyyy')}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

## Template 3: User Booth Dashboard

```tsx
/**
 * User Booth Dashboard
 * Booth-level operations and task management
 */

import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { CheckSquare, Users, FileText, TrendingUp } from 'lucide-react';
import { useFeedbackList, useFieldReports } from '../../hooks/useApiHooks';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { StatCard } from '../../components/charts/StatCard';

export default function UserBoothDashboard() {
  const { user } = useAuth();
  const { data: myReports, isLoading } = useFieldReports(true);
  const { data: feedback } = useFeedbackList({ limit: 10 });

  if (isLoading) return <LoadingSkeleton type="stats" count={4} />;

  const stats = {
    tasksToday: 5,
    interactionsLogged: myReports?.results?.length || 0,
    pendingTasks: 3,
    thisWeekReports: 12,
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">My Booth Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard title="Tasks Today" value={stats.tasksToday} icon={CheckSquare} iconColor="blue" />
        <StatCard title="Interactions Logged" value={stats.interactionsLogged} icon={Users} iconColor="green" />
        <StatCard title="Pending Tasks" value={stats.pendingTasks} icon={FileText} iconColor="orange" />
        <StatCard title="This Week Reports" value={stats.thisWeekReports} icon={TrendingUp} iconColor="purple" />
      </div>

      {/* My Tasks */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">My Tasks</h2>
        <div className="space-y-3">
          {['Visit Booth 101', 'Follow up with voters', 'Submit daily report', 'Attend team meeting'].map((task, i) => (
            <label key={i} className="flex items-center p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
              <input type="checkbox" className="mr-3 h-4 w-4" />
              <span className="text-sm text-gray-800">{task}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="p-6 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          Log New Interaction
        </button>
        <button className="p-6 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
          Submit Field Report
        </button>
        <button className="p-6 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
          Upload Photos
        </button>
      </div>
    </div>
  );
}
```

## Template 4: Volunteer Dashboard

```tsx
/**
 * Volunteer Dashboard
 * Field worker operations and contributions
 */

import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Calendar, MapPin, FileText, Award } from 'lucide-react';
import { useFieldReports } from '../../hooks/useApiHooks';
import { StatCard } from '../../components/charts/StatCard';

export default function VolunteerDashboard() {
  const { user } = useAuth();
  const { data: myReports } = useFieldReports(true);

  const stats = {
    todayEvents: 3,
    reportsSubmitted: myReports?.results?.length || 0,
    hoursContributed: 45,
    areasConvered: 12,
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Volunteer Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard title="Today's Events" value={stats.todayEvents} icon={Calendar} iconColor="blue" />
        <StatCard title="Reports Submitted" value={stats.reportsSubmitted} icon={FileText} iconColor="green" />
        <StatCard title="Hours Contributed" value={stats.hoursContributed} icon={Award} iconColor="purple" />
        <StatCard title="Areas Covered" value={stats.areasConvered} icon={MapPin} iconColor="orange" />
      </div>

      {/* Today's Schedule */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Today's Schedule</h2>
        <div className="space-y-3">
          {[
            { time: '09:00 AM', event: 'Morning Rally - Main Street', location: 'Zone A' },
            { time: '02:00 PM', event: 'Door-to-door Campaign', location: 'Ward 5' },
            { time: '06:00 PM', event: 'Evening Meeting', location: 'Community Hall' },
          ].map((item, i) => (
            <div key={i} className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <p className="font-medium text-gray-900">{item.event}</p>
                <p className="text-sm text-gray-600">{item.location}</p>
              </div>
              <span className="text-sm font-medium text-blue-600">{item.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Submit Report */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Ready to Submit?</h2>
        <p className="text-sm text-gray-600 mb-4">Submit your field report for today's activities</p>
        <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          Submit Field Report
        </button>
      </div>
    </div>
  );
}
```

## Template 5: Viewer Dashboard

```tsx
/**
 * Viewer Dashboard
 * Read-only analytics view
 */

import React from 'react';
import { Users, MessageSquare, TrendingUp, Activity } from 'lucide-react';
import { useAnalyticsOverview, useFeedbackStats } from '../../hooks/useApiHooks';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { StatCard } from '../../components/charts/StatCard';
import { LineChart } from '../../components/charts/LineChart';
import { PieChart } from '../../components/charts/PieChart';
import { format, subDays } from 'date-fns';

export default function ViewerDashboard() {
  const { data: analytics, isLoading } = useAnalyticsOverview();
  const { data: feedbackStats } = useFeedbackStats();

  if (isLoading) return <LoadingSkeleton type="stats" count={4} />;

  const sentimentData = Array.from({ length: 30 }, (_, i) => ({
    date: format(subDays(new Date(), 29 - i), 'MMM dd'),
    sentiment: 60 + Math.random() * 20,
  }));

  const issueData = [
    { name: 'Infrastructure', value: 35 },
    { name: 'Employment', value: 30 },
    { name: 'Healthcare', value: 20 },
    { name: 'Education', value: 15 },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Overview</h1>
      <p className="text-gray-600 mb-8">Read-only view of platform analytics</p>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Voters" value="1,250,000" icon={Users} iconColor="blue" />
        <StatCard title="Total Feedback" value={feedbackStats?.total || 0} icon={MessageSquare} iconColor="green" />
        <StatCard title="Active Campaigns" value="5" icon={Activity} iconColor="purple" />
        <StatCard title="Sentiment Score" value="67%" icon={TrendingUp} iconColor="indigo" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={sentimentData}
          xKey="date"
          yKey="sentiment"
          title="Sentiment Trend (Read-Only)"
          color="#6b7280"
        />

        <PieChart
          data={issueData}
          dataKey="value"
          nameKey="name"
          title="Issue Distribution (Read-Only)"
        />
      </div>

      {/* Note */}
      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          Note: This is a read-only view. You do not have permission to modify data.
        </p>
      </div>
    </div>
  );
}
```

## Quick Implementation Checklist

For each dashboard:

1. **Import Required Hooks**
   ```tsx
   import { useDistrictAnalytics, useFeedbackList } from '../../hooks/useApiHooks';
   ```

2. **Add Loading/Error States**
   ```tsx
   if (isLoading) return <LoadingSkeleton type="stats" count={4} />;
   if (error) return <ErrorMessage error={error} retry={refetch} />;
   ```

3. **Use Stat Cards**
   ```tsx
   <StatCard title="Title" value={123} icon={Users} iconColor="blue" />
   ```

4. **Add Charts**
   ```tsx
   <LineChart data={data} xKey="x" yKey="y" title="Chart Title" />
   ```

5. **Add Export Button**
   ```tsx
   <ExportButton data={data} filename="export" formats={['csv', 'excel']} />
   ```

6. **Add Filters**
   ```tsx
   <DateRangeFilter onDateChange={(start, end) => setRange({ start, end })} />
   ```

## Common Patterns

### Fetch Data Pattern
```tsx
const { data, isLoading, error, refetch } = useQueryHook(params);
```

### Submit Data Pattern
```tsx
const { mutate, isLoading } = useMutationHook();

const handleSubmit = () => {
  mutate(formData, {
    onSuccess: () => alert('Success!'),
    onError: (err) => alert(err.message),
  });
};
```

### Table Pattern
```tsx
<table className="w-full">
  <thead>
    <tr className="border-b">
      <th className="text-left py-3 px-4">Column</th>
    </tr>
  </thead>
  <tbody>
    {data.map((row) => (
      <tr key={row.id} className="border-b hover:bg-gray-50">
        <td className="py-3 px-4">{row.value}</td>
      </tr>
    ))}
  </tbody>
</table>
```

All templates follow the same architecture established in SuperAdmin and Admin State dashboards for consistency.
