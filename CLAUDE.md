# CLAUDE.md - Pulse of People Platform

## MISSION
Build and ship a production-grade political sentiment analysis platform with Django REST backend, React TypeScript frontend, role-based access control (7 roles), Mapbox interactive maps, and complete admin/superadmin dashboards - all functional, tested, and deployable.

## TECH STACK & TARGETS
- **Backend**: Django 5.2 + Django REST Framework + PostgreSQL + JWT Authentication
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Material-UI Icons
- **Maps**: Mapbox GL JS
- **Deployment**: Vercel (Frontend) + Railway/Render (Backend)
- **Database**: PostgreSQL (production), SQLite (development)

## REPO/ENV
- **Repo Path**: `/Users/murali/Downloads/pulseofpeople` (monorepo)
- **Package Manager**: npm (frontend), pip (backend)
- **OS**: macOS (Darwin 24.2.0)
- **Node**: >=18.0.0
- **Python**: 3.10+

## ARCHITECTURE
- **Monorepo Structure**: Single repository with `frontend/` and `backend/` folders
- **Authentication**: Django JWT with role hierarchy enforcement
- **Roles**: superadmin → admin → manager → analyst → user → viewer → volunteer
- **Permissions**: 67 granular permissions across 5 categories
- **Data Isolation**: Organization-based with RLS-style filtering

## CURRENT STATUS (v1.0)
✅ Backend Django API with JWT auth
✅ Frontend React app with Mapbox maps
✅ Role-based access control (75% complete)
✅ Admin dashboard with layout wrapper
✅ Polling booth upload UI (backend pending)
⚠️ Missing: DRF permission classes, CRUD endpoints, audit logs UI

## DELIVERABLES IN PROGRESS

### Phase 1: Repository Setup ✅
- [x] Monorepo structure with frontend + backend
- [x] Git initialization
- [x] .gitignore for both stacks
- [ ] GitHub repository creation
- [ ] Initial commit and push

### Phase 2: Backend Permission System (20% complete)
- [ ] Create custom DRF permission classes
- [ ] Implement user CRUD endpoints
- [ ] Implement polling booth bulk upload
- [ ] Add audit logging middleware
- [ ] Apply permissions to all endpoints

### Phase 3: Frontend Admin Features (60% complete)
- [x] Admin management UI (create modal)
- [ ] Edit/delete admin functionality
- [ ] Audit log viewer component
- [ ] Permission management UI
- [ ] Organization settings page

### Phase 4: Testing & Documentation (0% complete)
- [ ] Unit tests for permissions
- [ ] Integration tests for API
- [ ] E2E tests for critical flows
- [ ] API documentation
- [ ] User guides

## QUALITY BARS
- ✅ TypeScript strict mode enabled
- ✅ ESLint configured
- ⚠️ Tests coverage: 0% (target: 80%)
- ✅ No secrets in code
- ✅ Material-UI icons only (no emojis)
- ✅ Version footer on all pages

## VERSION TRACKING
- **Current Version**: 1.0
- **Date**: 2025-11-08
- **Increment**: Auto-increment on each git push
- **Display**: Footer of all pages (small gray text)

## RUN COMMANDS
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver  # http://127.0.0.1:8000

# Frontend
cd frontend
npm install
npm run dev  # http://localhost:5173 (or 5174, 5175)

# Build
npm run build

# Lint
npm run lint
npm run lint:fix
```

## ENVIRONMENT VARIABLES

### Backend (.env)
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pulseofpeople
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes

# Optional: Email (use console backend for dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Frontend (.env)
```env
# API
VITE_API_URL=http://127.0.0.1:8000

# Mapbox
VITE_MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token

# App
VITE_APP_NAME=Pulse of People
VITE_APP_VERSION=1.0
```

## TODO LIST (52 tasks)
See active todo list for detailed breakdown. Current priorities:

**Critical (Next 3):**
1. Create DRF permission classes
2. Implement user CRUD endpoints
3. Implement polling booth upload API

## BLOCKED ITEMS (Using Mocks)
1. **Mapbox Token**: Using demo token, replace with production token
2. **Email Service**: Console backend (prints to terminal), configure SMTP later
3. **Production Database**: Using SQLite for dev, PostgreSQL for production

## TESTING STRATEGY
- **Unit Tests**: Permission functions, serializers, views
- **Integration Tests**: API endpoints with authentication
- **E2E Tests**: User flows (login → create admin → upload data)
- **Manual Testing**: Test on http://localhost:5173 (frontend) + http://127.0.0.1:8000 (backend)

## OPERATIONS NOTES
- **Backups**: PostgreSQL automated daily backups
- **Logs**: Django logs to console (dev) / file (production)
- **Monitoring**: Django admin panel + custom analytics dashboard
- **Secrets Rotation**: Update JWT keys monthly

## DEPLOYMENT
- **Frontend**: Deploy to Vercel with auto-deploy on git push
- **Backend**: Deploy to Railway/Render with PostgreSQL addon
- **Database**: Managed PostgreSQL on Railway/Render

---

**Status**: 🟢 ACTIVE DEVELOPMENT - Monorepo Setup Phase
**Last Updated**: 2025-11-08
**Progress**: Repository structure ready, proceeding with git initialization and GitHub push
