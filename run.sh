#!/bin/bash

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: bash project-startup.sh"
    exit 1
fi

# Activate virtual environment
echo "🔓 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Configuration - EDIT THESE IF NEEDED
DB_NAME="${DB_NAME:-invoice_db}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# PostgreSQL superuser credentials (usually 'postgres')
# This is needed to create databases and users
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$DB_PASSWORD}"

# Check Django system
echo "✅ Running Django system checks..."
venv/bin/python3 manage.py check
if [ $? -ne 0 ]; then
    echo "❌ Django system checks failed!"
    exit 1
fi
echo "   ✅ System checks passed"
echo ""

# Setup database permissions
echo "🔐 Setting up database permissions..."
if [ -n "$DB_USER" ] && [ "$DB_USER" != "$POSTGRES_USER" ]; then
    PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
    PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true
    PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "GRANT CREATE ON SCHEMA public TO $DB_USER;" 2>/dev/null || true
    PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;" 2>/dev/null || true
    echo "   ✅ Database permissions configured for user: $DB_USER"
else
    echo "   ⚠️  Using database superuser: $DB_USER"
fi
echo ""

# Create migrations if needed
echo "🔄 Creating migrations..."
venv/bin/python3 manage.py makemigrations
echo "   ✅ Migrations created/up-to-date"
echo ""

# Run migrations
echo "🔄 Running database migrations..."
venv/bin/python3 manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "❌ Migration failed!"
    exit 1
fi
echo "   ✅ Migrations applied"
echo ""

# Collect static files (optional, for production-like setup)
echo "📦 Collecting static files..."
venv/bin/python3 manage.py collectstatic --noinput --clear 2>/dev/null || true
echo "   ✅ Static files collected"
echo ""

# Start development server
venv/bin/python3 manage.py runserver
