#!/bin/bash

# Portfolio Website - Quick Setup Script
# This script helps you set up the project quickly

echo "🚀 Portfolio Website Setup"
echo "=========================="
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
else
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your passwords!"
    echo ""
fi

# Create virtual environment if it doesn't exist
if [ -d "venv" ]; then
    echo "✅ Virtual environment already exists"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your passwords"
echo "2. Run: python manage.py createsuperuser (optional)"
echo "3. Run: python manage.py runserver"
echo "4. Visit: http://localhost:8000"
echo ""
echo "Admin Panel: http://localhost:8000/admin-panel/login/"
echo "Password: Check .env file (ADMIN_PANEL_PASSWORD)"