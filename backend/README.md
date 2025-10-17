# NetWiz Backend

> **PCB Netlist Visualizer + Validator Backend API**
> A FastAPI-based backend service for uploading, visualizing, and validating PCB netlist data.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.2-green.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.4.2-red.svg)](https://pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Source Code Overview
- `backend/netwiz_backend/netlist` - Core functionality, business logic of the server
- `backend/netwiz_backend` - Python package with generic tools for hosting the FastAPI server, connecting to mongodb, generating openapi spec etc
- `backend/scripts` - one-off scripts for development workflows
- `backend/tests` - our tests
- `backend` - general project structure boilerplate for install and setup

**NOTE:** for info about the actual business logic, see `NetWiz/backend/netwiz_backend/netlist/README.md`


# Backend Developer Guide
### Prerequisites

- **Python 3.10+** (recommended: Python 3.12)
- **MongoDB** (local or cloud instance)
- **Git** (for version control)

### 1. Clone
```bash
# Clone the repository
git clone https://github.com/modularizer/netwiz.git
cd NetWiz/backend
```

### 2. Install Python netwiz_backend
The following will install `netwiz_backend` as a locally installed editable python package and use a venv, allowing:
1. importing from `netwiz_backend` using absolute paths, making it easy to test individual files and components from any working directory with no relative import issues
2. install scripts using pyproject.toml making it trivial to setup python files as command-line tools with nice names (see `[project.scripts]` in pyproject.toml)

```bash
# From inside NetWiz/backend...

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```
**Note**: If your IDE shows import warnings for `from netwiz_backend import ...`, set the `backend` folder as the content root/project root/sources

### 3. Install MongoDB
We will have a way to run in docker, but if you wish to run locally during developement...
```bash
# 1. Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# 2. Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# 3. Update package lists
sudo apt update

# 4. Install MongoDB
sudo apt install -y mongodb-org

# 5. Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# 6. Check status
sudo systemctl status mongod
```

### 4. Dev Tools Setup
1. I like to use Ruff to enforce silly Python styles so the code looks clean and I don't have to worry about some of the silly rules like using double quotes instead of single quotes for string literals
 - If using PyCharm, you can install the `Ruff` plugin and it should see the pyproject.toml and automatically use the inspection profile, see also File → Settings → Editor → Inspections → Ruff Inspection
2. We have some pre-commit hooks setup to enforce standards before commiting, see `NetWiz/.pre-commit-config.yaml`


### 5. Environment Configuration

```bash
# Copy environment template
cp ..env.example .env

# Edit configuration (optional)
nano .env
```


### 6. Start Development Server

```bash
# Option 1: Using the installed command
netwiz-backend

# Option 2: Direct Python execution
python -m netwiz_backend.main

# Option 3: Using uvicorn directly
uvicorn netwiz_backend.main:app --host 0.0.0.0 --port 5000 --reload
```

### 7. Available Command-Line Tools

The package includes several command-line utilities for development and maintenance:

```bash
# API Management
netwiz-backend              # Start the FastAPI server
netwiz-dev                  # Start development server

# Development Tools
netwiz-generate-openapi     # Generate and enhance OpenAPI schema
netwiz-sync-metadata        # Sync metadata from __init__.py and requirements.txt to pyproject.toml
netwiz-check-metadata       # Check if metadata is in sync

# API Utilities
netwiz-health               # Check API health and status
netwiz-test-api             # Comprehensive API testing

# Examples
netwiz-generate-openapi --pretty
netwiz-health --verbose --openapi
netwiz-test-api --endpoint health
```

### 8. Verify Installation

Visit the API documentation:
- **Interactive Docs**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **Health Check**: http://localhost:5000/health

## 🛠️ Development Workflow

### Project Structure

```
backend/
├── netwiz_backend/           # Main package directory
│   ├── __init__.py          # Package metadata (source of truth)
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management with Pydantic
│   ├── system.py            # System endpoints (health, root, info)
│   ├── netlist/             # 🎯 Core business logic package
│   │   ├── __init__.py      # Netlist package exports
│   │   ├──... and all the rest of the actual logic
│   └── scripts/             # 🛠️ Command-line utilities
│       ├── __init__.py      # Scripts package
│       ├── generate_openapi.py  # OpenAPI schema generation
│       ├── sync_metadata.py     # Metadata synchronization
│       ├── check_metadata.py    # Metadata validation wrapper
│       ├── health_check.py      # API health monitoring
│       └── test_api.py          # API testing suite
├── pyproject.toml            # Package configuration (auto-synced from __init__.py)
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── .env.example              # Environment template
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Test fixtures
└── README.md                # This file
```


### Import Structure

The project uses absolute imports throughout for consistency:

```python
# ✅ Correct imports
from netwiz_backend.config import settings
from netwiz_backend.netlist import netlist_router
from netwiz_backend.system import router as system_router
from netwiz_backend.netlist.models import ErrorResponse

# ❌ Avoid relative imports (except in __init__.py files)
from .models import SomeModel  # Only in __init__.py files
```

### Code Quality Tools

The project includes pre-configured tools for maintaining code quality:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .

# Run all quality checks
make lint
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only

# Run tests in parallel
pytest -n auto
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 🧪 Testing Strategy

### Test Categories

- **Unit Tests** (`tests/unit/`): Test individual functions and classes
- **Integration Tests** (`tests/integration/`): Test API endpoints and database interactions
- **End-to-End Tests** (`tests/e2e/`): Full workflow testing with browser automation

### Test Data

Test fixtures and sample data are provided in `tests/conftest.py`:

```python
# Sample netlist for testing
sample_netlist = {
    "components": [...],
    "nets": [...]
}
```

## 🆘 Troubleshooting

### Common Issues

**Port already in use:**
When in development mode only, you can use the /kill endpoint to shutdown the server, e.g. http://localhost:5000/kill
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
```

**MongoDB connection issues:**
```bash
# Check if MongoDB is running
sudo systemctl status mongod
# Start MongoDB
sudo systemctl start mongod
```

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
# Reinstall in development mode
pip install -e .[dev]
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/modularizer/netwiz/issues)
- **Discussions**: [GitHub Discussions](https://github.com/modularizer/netwiz/discussions)
- **Email**: modularizer@gmail.com

---

**Happy Coding! 🎉**
