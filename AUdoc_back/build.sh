#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════
#  AUdoc — Render Build Script
#  Runs automatically on every deploy (free-tier compatible)
# ══════════════════════════════════════════════════════════════
set -o errexit  # Exit on any error

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Ensuring superuser exists..."
python manage.py create_superuser_if_none

echo "✅ Build complete!"
