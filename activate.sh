#!/bin/bash
# NetWiz Virtual Environment Activation Script

echo "🐍 Activating NetWiz Python Virtual Environment..."
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📍 Python path: $(which python)"
echo "📦 Pip path: $(which pip)"
echo ""
echo "🚀 To start the FastAPI backend:"
echo "   cd backend && python main.py"
echo ""
echo "🌐 To start the React frontend:"
echo "   cd frontend && npm start"
echo ""
echo "🔧 To run tests:"
echo "   make test-backend    # Backend tests"
echo "   make test-frontend   # Frontend tests"
echo "   make test-all        # All tests"
echo ""
echo "❌ To deactivate: deactivate"
