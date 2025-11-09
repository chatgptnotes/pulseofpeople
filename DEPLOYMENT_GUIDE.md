# Deployment Guide - Pulse of People Platform

## Production Deployment Status

**Deployment Date**: November 9, 2025
**Status**: ✅ Live and Operational
**Platform**: Vercel (Frontend) + Railway (Backend) + Supabase (Database)

---

## Production URLs

### Frontend Application
- **Primary URL**: https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app
- **Alias URL**: https://frontend-kappa-tan-62.vercel.app
- **Framework**: React 18 + TypeScript + Vite
- **Region**: Mumbai (bom1)
- **Build Status**: ✅ Ready

### Backend API
- **API Base URL**: https://pulseofpeople-backend.railway.app/api
- **Admin Dashboard**: https://pulseofpeople-backend.railway.app/admin
- **Framework**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL on Railway

### Database
- **Provider**: Supabase Cloud
- **URL**: https://iwtgbseaoztjbnvworyq.supabase.co
- **Dashboard**: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
- **Region**: Asia Pacific (ap-south-1)

---

## Environment Configuration

### Production Environment Variables

All environment variables are configured in Vercel dashboard and `.env.production` file:

```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
VITE_SUPABASE_ANON_KEY=[configured in Vercel]

# Backend API URLs
VITE_DJANGO_API_URL=https://pulseofpeople-backend.railway.app/api
VITE_API_URL=https://pulseofpeople-backend.railway.app/api
VITE_BACKEND_URL=https://pulseofpeople-backend.railway.app

# Application Configuration
VITE_APP_NAME=Pulse of People
VITE_ENVIRONMENT=production
VITE_MULTI_TENANT=false

# Feature Flags
VITE_ENABLE_SOCIAL_MEDIA=true
VITE_ENABLE_INFLUENCER_TRACKING=true
VITE_ENABLE_FIELD_REPORTS=true
VITE_ENABLE_SURVEYS=true
VITE_ENABLE_AI_INSIGHTS=true
```

### Setting Environment Variables in Vercel

**Option 1: Vercel Dashboard** (Recommended)
1. Go to https://vercel.com/dashboard
2. Select project: `frontend`
3. Navigate to Settings → Environment Variables
4. Add each variable from `.env.production`
5. Select "Production" environment
6. Save and redeploy

**Option 2: Vercel CLI**
```bash
cd frontend
vercel env add VARIABLE_NAME production
# Enter value when prompted
```

**Option 3: Pull from Vercel**
```bash
cd frontend
vercel env pull .env.production
```

---

## Deployment Process

### Initial Deployment (Completed)

```bash
# 1. Navigate to frontend directory
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/frontend

# 2. Build production bundle
npm run build

# 3. Deploy to Vercel
vercel --prod --yes

# 4. Deployment successful!
# URL: https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app
```

### Redeployment

**For code changes:**
```bash
cd frontend
npm run build
vercel --prod --yes
```

**For environment variable changes only:**
```bash
# Update variables in Vercel Dashboard, then:
vercel --prod --force
```

**Automatic deployment via Git:**
```bash
# Push to main branch triggers auto-deployment
git add .
git commit -m "Update: description"
git push origin main
```

---

## Build Configuration

### Vercel Configuration (`vercel.json`)

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ],
  "regions": ["bom1"]
}
```

### Build Output

```
dist/
├── index.html (0.83 kB)
├── assets/
│   ├── index-DtHarV3P.css (114.16 kB)
│   └── index-Cq4HaI7O.js (5,147.40 kB)
```

**Build Performance:**
- Build Time: ~24-48 seconds
- Bundle Size: 5.1 MB (1.4 MB gzipped)
- Modules Transformed: 14,120

---

## Monitoring & Analytics

### Vercel Analytics

**Access Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select project: `frontend`
3. Navigate to "Analytics" tab

**Metrics Tracked:**
- Page views and unique visitors
- Performance metrics (TTFB, FCP, LCP)
- Geographic distribution
- Device and browser breakdown
- Error tracking

**Enable Vercel Analytics:**
```bash
# Install analytics package
npm install @vercel/analytics

# Add to your app (in src/main.tsx)
import { Analytics } from '@vercel/analytics/react';

<Analytics />
```

### Monitoring Setup

**1. Deployment Monitoring**
```bash
# Check deployment status
vercel ls

# View deployment logs
vercel logs [deployment-url]

# Inspect specific deployment
vercel inspect [deployment-url] --logs
```

**2. Uptime Monitoring**

Recommended tools:
- **UptimeRobot** (https://uptimerobot.com)
  - Monitor: https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app
  - Interval: 5 minutes
  - Alert: Email/SMS on downtime

- **Vercel Built-in Monitoring**
  - Automatic health checks
  - Email notifications for failed deployments
  - Dashboard: https://vercel.com/dashboard

**3. Error Tracking**

Recommended: **Sentry**
```bash
npm install @sentry/react

# Initialize in src/main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: "production",
});
```

**4. Performance Monitoring**

Built-in Vercel Speed Insights:
- Enable in Vercel Dashboard → Settings → Speed Insights
- Tracks Core Web Vitals:
  - Largest Contentful Paint (LCP)
  - First Input Delay (FID)
  - Cumulative Layout Shift (CLS)
  - Time to First Byte (TTFB)

---

## Database Monitoring

### Supabase Dashboard

**Access**: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq

**Monitoring Features:**
- Database health and connections
- Query performance statistics
- Storage usage
- API request logs
- Real-time active connections

**Automated Backups:**
- **Frequency**: Daily automatic backups
- **Retention**: 7 days on free tier, 30 days on Pro
- **Manual Backup**: Database → Backups → Download

**Backup Restoration:**
```bash
# Download backup from Supabase Dashboard
# Restore using psql
psql $DATABASE_URL < backup.sql
```

### Railway Database Monitoring

**Access**: https://railway.app/dashboard

**Monitoring:**
- PostgreSQL metrics
- Connection pool status
- Disk usage alerts
- Query performance

---

## Security & SSL

### SSL Certificates
- **Provider**: Vercel (Automatic SSL)
- **Certificate**: Let's Encrypt (Auto-renewed)
- **Status**: ✅ Active
- **Protocol**: TLS 1.3

### Security Headers

Configured in `vercel.json`:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

### CORS Configuration

Backend (Django) settings:
```python
CORS_ALLOWED_ORIGINS = [
    "https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app",
    "https://frontend-kappa-tan-62.vercel.app",
]
```

---

## Custom Domain Setup (Optional)

### Adding Custom Domain to Vercel

1. **Purchase Domain** (e.g., pulseofpeople.com)

2. **Add to Vercel Project:**
```bash
vercel domains add pulseofpeople.com
```

Or via Dashboard:
- Go to Project Settings → Domains
- Add domain: pulseofpeople.com
- Add www subdomain: www.pulseofpeople.com

3. **Configure DNS:**

**Option A: Vercel Nameservers (Recommended)**
```
ns1.vercel-dns.com
ns2.vercel-dns.com
```

**Option B: DNS Records (Cloudflare, etc.)**
```
Type: CNAME
Name: @
Value: cname.vercel-dns.com

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

4. **Update Environment Variables:**
```bash
VITE_APP_URL=https://pulseofpeople.com
```

5. **Redeploy:**
```bash
vercel --prod
```

---

## Troubleshooting

### Common Issues

**1. Build Failures**

```bash
# View build logs
vercel logs [deployment-url]

# Common fixes:
- Check Node.js version (should be >=22.0.0)
- Clear build cache: vercel --force
- Verify all dependencies: npm install
```

**2. Environment Variables Not Loading**

```bash
# Pull latest variables
vercel env pull

# Verify in build logs
vercel logs [deployment-url] | grep VITE_

# Redeploy with fresh env
vercel --prod --force
```

**3. API Connection Issues**

```bash
# Check CORS settings in backend
# Verify API URL in .env.production
# Test API endpoint:
curl https://pulseofpeople-backend.railway.app/api/health
```

**4. Database Connection Errors**

```bash
# Check Supabase status
# Verify SUPABASE_URL and SUPABASE_ANON_KEY
# Test connection in browser console:
console.log(import.meta.env.VITE_SUPABASE_URL)
```

**5. Large Bundle Size Warning**

Current bundle: 5.1 MB (warning threshold: 500 kB)

**Solutions:**
- Implement code splitting with dynamic imports
- Lazy load routes and components
- Use build.rollupOptions.output.manualChunks
- Remove unused dependencies

```typescript
// Example: Lazy load routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analytics = lazy(() => import('./pages/Analytics'));
```

---

## Performance Optimization

### Current Metrics

- Build Time: 24-48 seconds
- Bundle Size: 5.1 MB (1.4 MB gzipped)
- Deploy Time: ~50 seconds total

### Optimization Recommendations

**1. Code Splitting**
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          mui: ['@mui/material', '@mui/icons-material'],
          maps: ['mapbox-gl', 'react-leaflet'],
          supabase: ['@supabase/supabase-js']
        }
      }
    }
  }
});
```

**2. Image Optimization**
- Use WebP format
- Lazy load images
- Implement responsive images with srcset

**3. CDN Caching**
- Static assets cached for 1 year
- Configured in vercel.json headers

**4. Compression**
- Gzip enabled by default (1.4 MB from 5.1 MB)
- Consider Brotli for better compression

---

## Rollback Procedure

### Quick Rollback

**Option 1: Vercel Dashboard**
1. Go to Deployments tab
2. Find previous working deployment
3. Click "Promote to Production"

**Option 2: Vercel CLI**
```bash
# List deployments
vercel ls

# Promote specific deployment
vercel promote [deployment-url]
```

**Option 3: Git Revert**
```bash
# Revert to previous commit
git revert HEAD
git push origin main
# Auto-deploys previous version
```

---

## Backup Strategy

### Database Backups

**Supabase Automated Backups:**
- Daily automatic backups
- 7-day retention (free tier)
- Manual download available

**Manual Backup:**
```bash
# Export current database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore backup
psql $DATABASE_URL < backup_20251109.sql
```

### Application Backups

**Git Repository:**
- All code versioned in Git
- Push regularly to remote
- Tag production releases

**Configuration Backups:**
```bash
# Export environment variables
vercel env pull .env.production.backup

# Backup vercel.json
cp vercel.json vercel.json.backup
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (`npm test`)
- [ ] Linting clean (`npm run lint`)
- [ ] Build succeeds locally (`npm run build`)
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] API endpoints tested
- [ ] Security headers configured

### Deployment

- [ ] Build production bundle
- [ ] Deploy to Vercel
- [ ] Verify deployment URL
- [ ] Check build logs for errors
- [ ] Test critical user flows
- [ ] Verify API connectivity
- [ ] Check analytics tracking

### Post-Deployment

- [ ] Monitor error logs (first 24 hours)
- [ ] Check performance metrics
- [ ] Verify database connections
- [ ] Test from multiple devices/browsers
- [ ] Update documentation
- [ ] Notify team of deployment

---

## Support & Contact

### Vercel Support
- Dashboard: https://vercel.com/dashboard
- Documentation: https://vercel.com/docs
- Support: https://vercel.com/support

### Supabase Support
- Dashboard: https://supabase.com/dashboard
- Documentation: https://supabase.com/docs
- Support: https://supabase.com/support

### Railway Support
- Dashboard: https://railway.app/dashboard
- Documentation: https://docs.railway.app
- Support: https://railway.app/help

---

## Version History

| Version | Date | Changes | Deployment URL |
|---------|------|---------|----------------|
| 1.0.0 | 2025-11-09 | Initial production deployment | https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app |

---

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [React Production Optimization](https://react.dev/learn/optimizing-performance)
- [Supabase Best Practices](https://supabase.com/docs/guides/platform/going-into-prod)

---

**Last Updated**: November 9, 2025
**Maintained By**: Deployment Team
**Status**: ✅ Production Ready
