#!/bin/bash

echo "======================================"
echo "Django + React Full Stack Setup"
echo "======================================"
echo ""

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
echo "✓ Backend setup complete"
echo ""

# Frontend setup
echo "Setting up frontend..."
cd ../frontend
npm install
cp .env.example .env
echo "✓ Frontend setup complete"
echo ""

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To start the servers:"
echo "  Backend:  cd backend && source venv/bin/activate && python manage.py runserver"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Or use: make dev"
echo ""
echo "Backend will be at:  http://localhost:8000"
echo "Frontend will be at: http://localhost:5173"
echo ""
