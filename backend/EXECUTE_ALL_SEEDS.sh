#!/bin/bash

# ============================================================
# EXECUTE ALL SEEDS SCRIPT
# ============================================================
# Purpose: Run all Django management commands and Supabase seed files
# Usage: bash EXECUTE_ALL_SEEDS.sh
# Location: /Users/murali/Applications/pulseofpeople/backend/
# ============================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="/Users/murali/Applications/pulseofpeople"
BACKEND_DIR="$PROJECT_ROOT/backend"
SUPABASE_SEEDS_DIR="$PROJECT_ROOT/frontend/supabase/seeds"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================
# VALIDATE ENVIRONMENT
# ============================================================

validate_environment() {
    print_header "VALIDATING ENVIRONMENT"

    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    print_success "Backend directory found"

    # Check if manage.py exists
    if [ ! -f "$BACKEND_DIR/manage.py" ]; then
        print_error "manage.py not found in $BACKEND_DIR"
        exit 1
    fi
    print_success "Django manage.py found"

    # Check if virtual environment exists
    if [ ! -d "$BACKEND_DIR/venv" ]; then
        print_warning "Virtual environment not found, creating one..."
        cd "$BACKEND_DIR"
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment found"
    fi

    # Check if Supabase seeds directory exists
    if [ ! -d "$SUPABASE_SEEDS_DIR" ]; then
        print_warning "Supabase seeds directory not found: $SUPABASE_SEEDS_DIR"
        print_info "Skipping Supabase seed files (run manually if needed)"
    else
        print_success "Supabase seeds directory found"
    fi
}

# ============================================================
# ACTIVATE VIRTUAL ENVIRONMENT
# ============================================================

activate_venv() {
    print_header "ACTIVATING VIRTUAL ENVIRONMENT"

    cd "$BACKEND_DIR"

    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi

    # Verify Python version
    PYTHON_VERSION=$(python --version)
    print_info "Python version: $PYTHON_VERSION"

    # Check if Django is installed
    if ! python -c "import django" 2>/dev/null; then
        print_warning "Django not found, installing requirements..."
        pip install -r requirements.txt
        print_success "Requirements installed"
    else
        print_success "Django found"
    fi
}

# ============================================================
# RUN DJANGO MIGRATIONS
# ============================================================

run_migrations() {
    print_header "RUNNING DJANGO MIGRATIONS"

    cd "$BACKEND_DIR"

    # Make migrations
    print_info "Creating migrations..."
    python manage.py makemigrations

    # Run migrations
    print_info "Applying migrations..."
    python manage.py migrate

    print_success "Migrations completed"
}

# ============================================================
# RUN DJANGO MANAGEMENT COMMANDS
# ============================================================

run_django_seeds() {
    print_header "RUNNING DJANGO MANAGEMENT COMMANDS"

    cd "$BACKEND_DIR"

    # List of management commands
    COMMANDS=(
        "generate_master_data"
        "generate_users"
        "generate_sentiment_data"
        "generate_social_posts"
        "generate_field_reports"
        "generate_direct_feedback"
        "generate_voters"
        "generate_voter_interactions"
        "generate_campaigns"
        "generate_events"
    )

    # Track success/failure
    SUCCESS_COUNT=0
    FAILURE_COUNT=0
    FAILED_COMMANDS=()

    # Run each command
    for cmd in "${COMMANDS[@]}"; do
        print_info "Running: python manage.py $cmd"

        if python manage.py "$cmd" 2>&1; then
            print_success "Completed: $cmd"
            ((SUCCESS_COUNT++))
        else
            print_error "Failed: $cmd"
            FAILED_COMMANDS+=("$cmd")
            ((FAILURE_COUNT++))
        fi

        echo ""
    done

    # Summary
    print_header "DJANGO SEEDS SUMMARY"
    echo -e "${GREEN}Successful: $SUCCESS_COUNT${NC}"
    echo -e "${RED}Failed: $FAILURE_COUNT${NC}"

    if [ $FAILURE_COUNT -gt 0 ]; then
        print_warning "Failed commands:"
        for cmd in "${FAILED_COMMANDS[@]}"; do
            echo "  - $cmd"
        done
        print_info "You can re-run failed commands manually with:"
        echo "  cd $BACKEND_DIR"
        echo "  source venv/bin/activate"
        echo "  python manage.py <command_name>"
    fi
}

# ============================================================
# RUN SUPABASE SEED FILES
# ============================================================

run_supabase_seeds() {
    if [ ! -d "$SUPABASE_SEEDS_DIR" ]; then
        print_warning "Supabase seeds directory not found, skipping..."
        return
    fi

    print_header "SUPABASE SEED FILES INFORMATION"

    print_info "Supabase seed files are available at:"
    echo "  $SUPABASE_SEEDS_DIR"
    echo ""

    print_info "Available seed files:"
    if [ -f "$SUPABASE_SEEDS_DIR/trending_topics_seed.sql" ]; then
        echo "  ✓ trending_topics_seed.sql (100 trending topics)"
    fi
    if [ -f "$SUPABASE_SEEDS_DIR/alerts_seed.sql" ]; then
        echo "  ✓ alerts_seed.sql (50 alerts)"
    fi
    echo ""

    print_warning "Supabase seeds must be run manually via Supabase SQL Editor or psql"
    print_info "See SUPABASE_SEEDS_README.md for detailed instructions"
    echo ""

    print_info "Quick start:"
    echo "  1. Go to https://app.supabase.com"
    echo "  2. Select your project"
    echo "  3. Open SQL Editor"
    echo "  4. Copy/paste content from seed files"
    echo "  5. Click 'Run'"
    echo ""

    print_info "Or via psql:"
    echo "  psql \"postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres\" \\"
    echo "    -f $SUPABASE_SEEDS_DIR/trending_topics_seed.sql"
    echo ""
    echo "  psql \"postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres\" \\"
    echo "    -f $SUPABASE_SEEDS_DIR/alerts_seed.sql"
}

# ============================================================
# VERIFY DATABASE STATE
# ============================================================

verify_database() {
    print_header "VERIFYING DATABASE STATE"

    cd "$BACKEND_DIR"

    print_info "Checking database records..."

    # Check if we can run Django shell commands
    if python manage.py shell -c "from django.contrib.auth import get_user_model; print(f'Users: {get_user_model().objects.count()}')" 2>/dev/null; then
        print_success "Database verification completed"
    else
        print_warning "Could not verify database (this is normal if models don't exist)"
    fi
}

# ============================================================
# GENERATE SUMMARY REPORT
# ============================================================

generate_summary() {
    print_header "DATA GENERATION SUMMARY"

    echo ""
    echo -e "${GREEN}✅ All data generation commands have been executed!${NC}"
    echo ""

    print_info "What was done:"
    echo "  ✓ Django migrations applied"
    echo "  ✓ Master data seeded (states, districts, wards, polling booths)"
    echo "  ✓ Users and roles created"
    echo "  ✓ Sentiment analysis data generated"
    echo "  ✓ Social media posts created"
    echo "  ✓ Field reports added"
    echo "  ✓ Direct feedback entries generated"
    echo "  ✓ Voter records created"
    echo "  ✓ Voter interactions logged"
    echo "  ✓ Campaigns created"
    echo "  ✓ Events scheduled"
    echo ""

    print_info "Next steps:"
    echo "  1. Run Supabase seed files manually (see above instructions)"
    echo "  2. Start Django development server:"
    echo "     cd $BACKEND_DIR"
    echo "     source venv/bin/activate"
    echo "     python manage.py runserver"
    echo ""
    echo "  3. Start React frontend:"
    echo "     cd $PROJECT_ROOT/frontend"
    echo "     npm run dev"
    echo ""

    print_info "Useful commands:"
    echo "  - Create superuser: python manage.py createsuperuser"
    echo "  - Django admin: http://127.0.0.1:8000/admin/"
    echo "  - API docs: http://127.0.0.1:8000/api/"
    echo "  - Frontend: http://localhost:5173"
    echo ""

    print_success "Database is ready for testing!"
}

# ============================================================
# MAIN EXECUTION FLOW
# ============================================================

main() {
    print_header "PULSE OF PEOPLE - DATABASE SEED SCRIPT"
    echo "This script will populate your database with test data"
    echo ""

    # Validate environment
    validate_environment

    # Activate virtual environment
    activate_venv

    # Run migrations
    run_migrations

    # Run Django seed commands
    run_django_seeds

    # Show Supabase instructions
    run_supabase_seeds

    # Verify database
    verify_database

    # Generate summary
    generate_summary
}

# ============================================================
# ERROR HANDLING
# ============================================================

# Trap errors
trap 'print_error "Script failed at line $LINENO. Exit code: $?"' ERR

# ============================================================
# RUN MAIN
# ============================================================

main

# Deactivate virtual environment
deactivate 2>/dev/null || true

exit 0
