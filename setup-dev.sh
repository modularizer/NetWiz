#!/bin/bash
# Development setup script for NetWiz

set -e  # Exit on any error

echo "🚀 Setting up NetWiz development environment..."

# Check if we're in the right directory
if [ ! -f "backend/pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the NetWiz project root"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install in development mode
echo "Installing backend dependencies..."
pip install -e .[dev]

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

echo "✅ Backend setup complete!"

# Frontend setup (if it exists)
cd ..
if [ -d "frontend" ]; then
    echo "📦 Setting up frontend..."
    cd frontend

    if [ -f "package.json" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi

    echo "✅ Frontend setup complete!"
    cd ..
fi

echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source backend/venv/bin/activate"
echo "2. Start the backend: netwiz-backend"
echo "3. Happy coding! 🚀"
