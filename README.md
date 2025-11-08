# Pulse of People

Political sentiment analysis platform with voter feedback, field reports, AI insights, and interactive maps for Tamil Nadu + Puducherry.

## Features

- **Role-Based Access Control**: 7 roles with 67 granular permissions
- **Interactive Maps**: Mapbox GL JS with state → districts → constituencies → booths drill-down
- **Voter Feedback**: Public feedback submission with AI sentiment analysis
- **Field Reports**: Ground-level reports from party workers
- **Analytics Dashboard**: Real-time sentiment tracking and competitor analysis
- **Admin Management**: Complete superadmin and admin dashboards
- **Polling Booth Management**: CSV bulk upload with validation

## Tech Stack

### Backend
- Django 5.2 + Django REST Framework
- JWT Authentication (SimpleJWT)
- PostgreSQL (production) / SQLite (development)
- Python 3.10+

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS + Material-UI Icons
- Mapbox GL JS for interactive maps
- React Router v6

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL (for production)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Backend will be available at: `http://127.0.0.1:8000`

###Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env with your API URL and Mapbox token

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173` (or 5174, 5175)

## Environment Variables

### Backend (.env)
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql  # or django.db.backends.sqlite3
DB_NAME=pulseofpeople
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes

# Email (optional)
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

## User Roles & Permissions

| Role | Level | Description |
|------|-------|-------------|
| **Superadmin** | 1 | Platform owner, manages all organizations and admins |
| **Admin** | 2 | Organization owner, manages users and data |
| **Manager** | 3 | Manages field workers and reports |
| **Analyst** | 4 | Views analytics and generates reports |
| **Ward Coordinator** | 4 | Manages specific wards and booths |
| **User** | 5 | Standard access to dashboard and reports |
| **Viewer** | 6 | Read-only access |
| **Volunteer** | 7 | Submit field reports only |

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login with email or username
- `POST /api/auth/signup/` - Register new user (requires auth)
- `GET /api/auth/profile/` - Get current user profile
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - Logout and blacklist token

### Master Data (Public)
- `GET /api/states/` - List all states
- `GET /api/districts/?state=TN` - List districts
- `GET /api/constituencies/?state=TN&type=assembly` - List constituencies
- `GET /api/polling-booths/` - List polling booths
- `GET /api/issue-categories/` - TVK's 9 priorities
- `GET /api/political-parties/` - Political parties

### Feedback & Reports (Auth Required)
- `POST /api/feedback/` - Submit feedback (public)
- `GET /api/feedback/` - List feedback (role-filtered)
- `POST /api/field-reports/` - Submit field report
- `GET /api/field-reports/` - List field reports

### Analytics (Auth Required)
- `GET /api/analytics/overview/` - Dashboard overview
- `GET /api/analytics/state/{code}/` - State analytics
- `GET /api/analytics/district/{id}/` - District analytics
- `GET /api/analytics/constituency/{code}/` - Constituency analytics

## Project Structure

```
pulseofpeople/
├── backend/                    # Django REST API
│   ├── api/                    # Main app
│   │   ├── models.py           # Database models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views/              # API views
│   │   ├── urls/               # URL routing
│   │   └── management/         # Custom commands
│   ├── config/                 # Django settings
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   # React TypeScript app
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   ├── pages/              # Page components
│   │   ├── contexts/           # React contexts
│   │   ├── hooks/              # Custom hooks
│   │   ├── services/           # API services
│   │   ├── utils/              # Utility functions
│   │   └── App.tsx             # Main app component
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── .gitignore
├── README.md
├── CLAUDE.md                   # Development mission file
└── CHANGELOG.md
```

## Development

### Backend Commands
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create superadmin with role
python manage.py createsuperadmin

# Run tests
python manage.py test

# Collect static files (production)
python manage.py collectstatic

# Shell
python manage.py shell
```

### Frontend Commands
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Type check
npm run type-check
```

## Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Deployment

### Option 1: Railway (Monorepo - RECOMMENDED)

Railway can deploy both frontend and backend from the same repository:

1. **Create Railway Project**
   - Connect GitHub repository
   - Railway auto-detects both services

2. **Backend Service**
   - Root Directory: `backend`
   - Start Command: `gunicorn config.wsgi:application`
   - Add PostgreSQL plugin
   - Environment variables: SECRET_KEY, DEBUG=False, ALLOWED_HOSTS

3. **Frontend Service**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Start Command: `npm run preview` (or use static site deployment)
   - Environment variables: VITE_API_URL

**Cost**: ~$10-20/month (backend + frontend + PostgreSQL)

### Option 2: Vercel (Frontend) + Railway (Backend)

- **Frontend**: Deploy to Vercel (auto-deploy on git push)
- **Backend**: Deploy to Railway with PostgreSQL

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/pulseofpeople/issues
- Email: support@pulseofpeople.com

---

**Version**: 1.0 | **Last Updated**: 2025-11-08 | **Status**: Active Development
