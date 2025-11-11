# Production Quick Reference Card

## Essential URLs

### Production Application
```
Frontend: https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app
Backend:  https://pulseofpeople-backend.railway.app/api
Database: https://iwtgbseaoztjbnvworyq.supabase.co
```

### Dashboards
```
Vercel:   https://vercel.com/dashboard
Railway:  https://railway.app/dashboard
Supabase: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
```

---

## Quick Commands

### Deployment
```bash
# Deploy to production
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/frontend
npm run build
vercel --prod

# View deployments
vercel ls

# View logs
vercel logs

# Rollback
vercel promote [previous-url]
```

### Monitoring
```bash
# Check deployment status
vercel inspect [deployment-url]

# View error logs
vercel logs --type=error

# Check backend health
curl https://pulseofpeople-backend.railway.app/api/health

# Check frontend
curl -I https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app
```

---

## Environment Variables

### Required in Vercel Dashboard
```bash
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
VITE_SUPABASE_ANON_KEY=[from .env]
VITE_API_URL=https://pulseofpeople-backend.railway.app/api
VITE_DJANGO_API_URL=https://pulseofpeople-backend.railway.app/api
VITE_BACKEND_URL=https://pulseofpeople-backend.railway.app
VITE_APP_NAME=Pulse of People
VITE_ENVIRONMENT=production
VITE_MULTI_TENANT=false
```

### Set in Dashboard
1. Go to https://vercel.com/dashboard
2. Select project: `frontend`
3. Settings → Environment Variables
4. Add each variable for Production environment

---

## Emergency Contacts

### Platform Support
- Vercel Support: https://vercel.com/support
- Railway Support: https://railway.app/help
- Supabase Support: https://supabase.com/support

### Project Locations
- Repo: `/Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople`
- Frontend: `/Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/frontend`
- Docs: See DEPLOYMENT_GUIDE.md and MONITORING_SETUP.md

---

## Incident Response

### If Site is Down
```bash
# 1. Check deployment status
vercel ls

# 2. Check logs
vercel logs --type=error

# 3. Rollback if needed
vercel promote [last-working-deployment]

# 4. Check backend
curl https://pulseofpeople-backend.railway.app/api/health
```

### If API Errors
```bash
# Check Railway logs
# Go to: https://railway.app/dashboard

# Check Supabase
# Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
```

---

## Documentation

- **Full Deployment Guide**: `/DEPLOYMENT_GUIDE.md`
- **Monitoring Setup**: `/MONITORING_SETUP.md`
- **Deployment Summary**: `/DEPLOYMENT_COMPLETE.md`
- **This Reference**: `/PRODUCTION_QUICK_REFERENCE.md`

---

**Last Updated**: November 9, 2025
**Status**: Production Ready ✅
