#!/bin/bash
# Script to fix duplicate model issues

echo "🔧 Fixing duplicate model definitions..."

# Remove the duplicate political_models.py file
if [ -f "api/political_models.py" ]; then
    echo "📦 Removing duplicate political_models.py..."
    rm api/political_models.py
    echo "✅ Deleted api/political_models.py"
else
    echo "ℹ️  political_models.py not found (already deleted)"
fi

# Check if any .pyc cache files exist and remove them
echo "🧹 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "Now run:"
echo "  source venv/bin/activate"
echo "  python manage.py seed_political_data"
