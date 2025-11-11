#!/bin/bash

# TVK Political Platform - Automated Setup Script
# This script will set up your Django backend environment

echo "======================================"
echo "TVK Political Platform - Setup Script"
echo "======================================"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

echo "✓ Current directory: $(pwd)"
echo ""

# Check if venv exists and is broken
if [ -d "venv" ]; then
    echo "⚠️  Old virtual environment found. Removing..."
    rm -rf venv
    echo "✓ Removed old venv"
    echo ""
fi

# Create new virtual environment
echo "📦 Creating new virtual environment..."
if command -v python3 &> /dev/null; then
    python3 -m venv venv
    PYTHON_CMD="python"
elif command -v python &> /dev/null; then
    python -m venv venv
    PYTHON_CMD="python"
else
    echo "❌ ERROR: Python not found. Please install Python 3.8 or higher."
    exit 1
fi
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ Pip upgraded"
echo ""

# Install requirements
echo "📦 Installing dependencies (this may take 2-3 minutes)..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ ERROR installing dependencies. Try running manually:"
    echo "   pip install -r requirements.txt"
    exit 1
fi
echo "✓ All dependencies installed"
echo ""

# Create migrations
echo "🗄️  Creating database migrations..."
$PYTHON_CMD manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "❌ ERROR creating migrations"
    exit 1
fi
echo "✓ Migrations created"
echo ""

# Apply migrations
echo "🗄️  Applying migrations to database..."
$PYTHON_CMD manage.py migrate
if [ $? -ne 0 ]; then
    echo "❌ ERROR applying migrations"
    exit 1
fi
echo "✓ Migrations applied"
echo ""

# Ask if user wants to create superuser
echo "👤 Would you like to create a superuser account? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo "Creating superuser..."
    $PYTHON_CMD manage.py createsuperuser
fi
echo ""

echo "======================================"
echo "✅ SETUP COMPLETE!"
echo "======================================"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then open your browser to:"
echo "  http://127.0.0.1:8000/api/health/"
echo ""
echo "Admin panel:"
echo "  http://127.0.0.1:8000/admin/"
echo ""
