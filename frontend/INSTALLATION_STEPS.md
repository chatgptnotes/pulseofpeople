# Dashboard Integration - Installation Steps

## Step-by-Step Installation Guide

### Step 1: Install Dependencies

```bash
cd /Users/murali/Downloads/pulseofpeople/frontend

# Install React Query (required)
npm install @tanstack/react-query@^5.0.0

# Install React Query Devtools (development only)
npm install -D @tanstack/react-query-devtools@^5.0.0

# Install Virtual Scrolling (optional, for large lists)
npm install react-window@^1.8.10

# Verify installations
npm list @tanstack/react-query react-window
```

**Already Installed (verify in package.json):**
- ✅ recharts ^2.8.0
- ✅ date-fns ^4.1.0
- ✅ xlsx ^0.18.5
- ✅ html2canvas ^1.4.1

### Step 2: Update App Entry Point

**Option A: Update `/src/main.tsx` (Vite projects)**

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { QueryProvider } from './providers/QueryProvider';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryProvider>
      <App />
    </QueryProvider>
  </React.StrictMode>
);
```

**Option B: Update `/src/App.tsx`**

```tsx
import { QueryProvider } from './providers/QueryProvider';
import { AuthProvider } from './contexts/AuthContext';
import { BrowserRouter } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <QueryProvider>
        <AuthProvider>
          {/* Your existing app structure */}
        </AuthProvider>
      </QueryProvider>
    </BrowserRouter>
  );
}

export default App;
```

### Step 3: Update Router Configuration

Update `/src/App.tsx` or your router file to use the new enhanced dashboards:

```tsx
import { Routes, Route } from 'react-router-dom';
import SuperAdminDashboardEnhanced from './pages/dashboards/SuperAdminDashboardEnhanced';
import AdminStateDashboardEnhanced from './pages/dashboards/AdminStateDashboardEnhanced';

function App() {
  return (
    <Routes>
      {/* Update these routes */}
      <Route path="/super-admin/dashboard" element={<SuperAdminDashboardEnhanced />} />
      <Route path="/admin/dashboard" element={<AdminStateDashboardEnhanced />} />

      {/* Keep your other routes */}
      <Route path="/" element={<Home />} />
      {/* ... */}
    </Routes>
  );
}
```

### Step 4: Environment Variables

Add to `/frontend/.env`:

```env
# Django API URL
VITE_DJANGO_API_URL=http://127.0.0.1:8000/api

# Mapbox Token (if using maps)
VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here

# App Info
VITE_APP_NAME=Pulse of People
VITE_APP_VERSION=1.0

# Optional: Custom refresh intervals (milliseconds)
VITE_STATS_REFRESH_INTERVAL=60000
VITE_FEEDBACK_REFRESH_INTERVAL=30000
VITE_ANALYTICS_REFRESH_INTERVAL=60000
```

### Step 5: Start Development Server

```bash
# Ensure Django backend is running
cd /Users/murali/Downloads/pulseofpeople/backend
python manage.py runserver

# In another terminal, start frontend
cd /Users/murali/Downloads/pulseofpeople/frontend
npm run dev
```

Expected output:
```
  VITE v5.0.8  ready in 523 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### Step 6: Test the Integration

**Test SuperAdmin Dashboard:**
1. Navigate to: http://localhost:5173/super-admin/dashboard
2. Should see:
   - 6 stat cards loading
   - User growth chart (line chart)
   - Role distribution chart (donut)
   - Organization table
   - Export button

**Test Admin State Dashboard:**
1. Navigate to: http://localhost:5173/admin/dashboard
2. Should see:
   - Sentiment gauge
   - 4 key metric cards
   - Sentiment trend chart
   - Issue distribution chart
   - District performance bar chart
   - Interactive map (if Mapbox configured)

### Step 7: Verify React Query Devtools

1. Open browser DevTools
2. Look for React Query panel (bottom-right)
3. Click to expand
4. Should see active queries and cache

### Step 8: Test API Connectivity

Open browser console and run:

```javascript
// Test API connection
fetch('http://127.0.0.1:8000/api/health/')
  .then(r => r.json())
  .then(d => console.log('API Health:', d))
  .catch(e => console.error('API Error:', e));

// Test authentication
const token = localStorage.getItem('access_token');
console.log('Auth token:', token ? 'Present' : 'Missing');
```

### Step 9: Test Export Functionality

1. Go to SuperAdmin Dashboard
2. Click "Export" button
3. Select "Export as CSV"
4. File should download: `platform-users-2025-11-09.csv`

### Step 10: Test Date Filtering

1. Scroll to Date Range Filter
2. Click "Last 7 days"
3. Verify date range updates
4. Click "Custom"
5. Select custom dates
6. Verify charts update (if connected to backend)

## Troubleshooting

### Issue: Module not found '@tanstack/react-query'

**Solution:**
```bash
npm install @tanstack/react-query @tanstack/react-query-devtools
```

### Issue: Charts not rendering

**Possible Causes:**
1. Data format mismatch
2. Missing keys
3. Empty data array

**Solution:**
```tsx
// Check data in console
console.log('Chart data:', data);

// Ensure data has correct structure
const validData = data?.filter(item => item.value != null) || [];
```

### Issue: Infinite loading state

**Cause:** API endpoint not responding

**Solution:**
1. Check Django server is running
2. Verify CORS settings in Django
3. Check network tab in DevTools
4. Verify API URL in `.env`

**Django CORS Settings (`settings.py`):**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]

CORS_ALLOW_CREDENTIALS = True
```

### Issue: 401 Unauthorized errors

**Cause:** Missing or expired JWT token

**Solution:**
1. Login again to get fresh token
2. Check token in localStorage
3. Verify token format in djangoApi.ts

```javascript
// Check token in console
console.log('Token:', localStorage.getItem('access_token'));

// Manual token refresh
const refreshToken = localStorage.getItem('refresh_token');
fetch('http://127.0.0.1:8000/api/auth/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: refreshToken })
})
  .then(r => r.json())
  .then(d => {
    localStorage.setItem('access_token', d.access);
    console.log('Token refreshed');
    window.location.reload();
  });
```

### Issue: Export not working

**Cause:** Missing dependencies

**Solution:**
```bash
npm install xlsx html2canvas
```

### Issue: TypeScript errors

**Cause:** Type definitions missing

**Solution:**
```bash
npm install -D @types/react @types/react-dom
```

Or add to tsconfig.json:
```json
{
  "compilerOptions": {
    "skipLibCheck": true
  }
}
```

## Verification Checklist

- [ ] Dependencies installed
- [ ] QueryProvider added to app
- [ ] Routes updated
- [ ] Environment variables configured
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] SuperAdmin dashboard loads
- [ ] Admin State dashboard loads
- [ ] Charts render correctly
- [ ] Export button works
- [ ] Date filter works
- [ ] React Query Devtools visible
- [ ] No console errors

## Next Steps After Installation

1. **Replace original dashboards:**
   ```bash
   # Backup originals
   mv src/pages/dashboards/SuperAdminDashboard.tsx src/pages/dashboards/SuperAdminDashboard.old.tsx

   # Rename enhanced versions
   mv src/pages/dashboards/SuperAdminDashboardEnhanced.tsx src/pages/dashboards/SuperAdminDashboard.tsx
   ```

2. **Implement remaining dashboards:**
   - Use templates in `DASHBOARD_TEMPLATES.md`
   - Copy patterns from enhanced dashboards
   - Test each dashboard individually

3. **Add backend endpoints:**
   - Organizations CRUD
   - Platform health check
   - Team members list
   - Activity logs

4. **Performance testing:**
   - Measure page load time
   - Check API response times
   - Optimize slow queries
   - Add pagination for large datasets

5. **Production deployment:**
   - Build production bundle: `npm run build`
   - Test with production API
   - Configure caching headers
   - Enable compression

## Support

If you encounter issues:

1. Check browser console for errors
2. Check network tab for failed requests
3. Verify Django server logs
4. Review React Query Devtools
5. Consult documentation:
   - React Query: https://tanstack.com/query/latest
   - Recharts: https://recharts.org/
   - Date-fns: https://date-fns.org/

## Summary

**Installation Time:** ~15 minutes
**Files Modified:** 3-4 files
**Dependencies Added:** 2-3 packages
**New Components Created:** 25+ reusable components
**Dashboards Enhanced:** 2 (SuperAdmin, Admin State)
**Dashboards Remaining:** 5 (templates provided)

The system is now ready for full dashboard integration with real-time data, comprehensive charts, and production-ready features.
