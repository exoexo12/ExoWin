#!/bin/bash

# ExoWin 👑 - Unified Startup Script
# This script sets up the database, launches the web app, and starts the Telegram bot

set -e  # Exit on any error

echo "🎰 Starting ExoWin 👑 System..."
echo "=" * 50

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
required_vars=("BOT_TOKEN" "MONGODB_URI" "WEBAPP_URL")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please check your .env file and ensure all required variables are set."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup database
echo "🗄️ Setting up database..."
python scripts/database_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Database setup failed!"
    exit 1
fi

echo "✅ Database setup completed successfully"

# Start the system
echo "🚀 Starting ExoWin 👑 System..."
echo "🌐 Web App will be available at: $WEBAPP_URL"
echo "🤖 Telegram Bot will start shortly..."
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start the unified system (bot + webapp)
python start.py