# NetWiz
**PCB Netlist Visualizer + Validator** _by Torin Halsted_

A proof-of-concept application for visualizing and validating PCB netlist data. This tool allows users to upload netlist files, visualize them as interactive graphs, and validate them against basic electrical rules.

# Architecture
- Frontend: React using Typescript and vite
- Backend: Python using FastAPI
- Database: MongoDB
- Deployment: `docker-compose`, individual `docker` images, or mixed approach with statically hosted frontend at https://modularizer.github.io/NetWiz/ plus locally hosted backend

- [How to Run](#how-to-run-netwiz)
- [Features](#features)
  - [Validation Rules](#validation-rules)

# How to Run NetWiz
There are an abundance of ways to run Netwiz. Here are just a few...
- [Oneliner](#demo-no-source-code-required)
- [Docker](#running-with-docker)
- [From Source](#from-source)


## Oneliner (No Source Code Required)
Want to run NetWiz without cloning the repository? Just download and run the docker-compose, which will pull the appropriate docker images from the GitHub Package Registry

1. make sure you have `docker`, `docker-compose` and `curl` installed and your current user has access to run it
    ```bash
   docker --version
   docker-compose --version
   curl --version
   ```
2. To run with default settings and secrets, use the following
    ```bash
    COMPOSE_PROJECT_NAME=netwiz f=$(mktemp) &&
    curl -fsSL https://raw.githubusercontent.com/modularizer/NetWiz/main/docker-compose.prod.yml -o "$f" &&
    trap 'docker-compose -p netwiz -f "$f" down --rmi all --volumes --remove-orphans; rm -f "$f"' EXIT &&
    docker-compose -p netwiz -f "$f" up
   ```
   then access at http://localhost
3. Optionally, to use extra settings such as `PORT`, `BACKEND_ENV_FILE` or `MONGODB_DATA_PATH` ...
    ```bash
   PORT=8080 \
    MONGODB_DATA_PATH=/home/mod/Code/NetWiz/data \
    BACKEND_ENV_FILE=/home/mod/Code/NetWiz/backend/.env \
    COMPOSE_PROJECT_NAME=netwiz f=$(mktemp) &&
    curl -fsSL https://raw.githubusercontent.com/modularizer/NetWiz/main/docker-compose.prod.yml -o "$f" &&
    trap 'docker-compose -p netwiz -f "$f" down --rmi all --volumes --remove-orphans; rm -f "$f"' EXIT &&
    docker-compose -p netwiz -f "$f" up
    ```

## Running with Docker
Okay with cloning? clone the repo and then locally build and run the docker containers using `docker-compose`

```bash
git clone git@github.com:modularizer/NetWiz.git
cd NetWiz
cp .env.example .env
docker-compose up --build
```

## From Source
Want to get your dev enviroment setup?

1. Install backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Install pre-commit hooks
pre-commit install
```

2. Install frontend
```bash
# Install dependencies
npm install
```

3. Install MongoDb
```bash
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update && sudo apt install -y mongodb-org
sudo systemctl enable mongod
```

4. Start MongoDB
```bash
sudo systemctl start mongod
```

5. Start backend
```bash
netwiz-backend
```

6. Run Frontend
```bash
npm run dev
```



### Troubleshooting

#### **Docker Permission Error?**
If you get "Permission denied" errors when running Docker commands:

1.  **Permanent fix - Add user to docker group:**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker # or logout and login again
   ```

2. **Verify Docker is running:**
   ```bash
   docker --version
   sudo systemctl status docker
   ```
#### **Port in use?**
1. If unintenionally: kill the process serving your backend, frontend, mogodb, etc
2. If the port is intentionally in use by another project, edit `.env` to avoid conflicts



## Features

### Core Functionality
1. **Netlist Upload**: Upload JSON-formatted netlist files with custom schema
2. **Interactive Visualization**: Render netlists as graphs with components as nodes and nets as edges
3. **Data Validation**: Validate netlist data against electrical rules and constraints
4. **Database Storage**: Store submissions in MongoDB for persistence
5. **User Management**: Track submissions per user
6. **Validation Results**: Display detailed validation results with highlighted violations

### Netlist Schema
The application supports netlist files containing:
- **Components**: List of electronic components (ICs, resistors, connectors, etc.) with their pins
- **Nets**: Electrical connection definitions
- **Connections**: Mapping between nets and component pins

### Validation Rules
- `Name` data validation
  - no blank names
  - components must have unique names
  - nets must have unique names
  - warning if a net has the same name as a component
- `GND` connectivity verification
  - there must be atleast one ground net
  - each ground net should have atleast one connection
  - every pin labelled with type ground must be connected to a ground net
- Net validity
  - every net must have at least one connection
- Component validity
  - warnings for pins that are disconnected
- see `/backend/netlist/core/validation/rules/*` for more
- More to come ...



## Project Structure
```
NetWiz/
├── backend/                           # Python backend service
│   ├── netwiz_backend/                # Main backend package
│   │   ├── netlist/                   # Handles network listing and related logic
│   │   │   └── core/                  # Core backend functionality and utilities
│   │   └── main.py                    # Application entrypoint (FastAPI/Flask, etc.)
│   ├── .env                           # Environment variables for local backend dev
│   ├── pyproject.toml                 # Python project config and package metadata
│   ├── requirements.txt               # List of Python dependencies
│   └── Dockerfile                     # Docker build instructions for backend image
│
├── frontend/                          # React frontend application
│   ├── package.json                   # Node.js dependencies and scripts
│   ├── index.html                     # Main HTML entry file
│   ├── main.tsx                       # React app root (TypeScript)
│   └── Dockerfile                     # Docker build instructions for frontend image
│
└── README.md                          # Project overview, setup, and usage guide
```

## Code Styles

### Backend Development
- `pydantic` + `FastAPI` + `openapi.json` + `SwaggerUI`
  - allows us to keep code organized and typehinted, reducing devloper errors
  - procudes a swagger API documentation page  (http://locahost:5000/docs) built for us thanks to pydantic and fastapi
  - aids in enforcing the Netlist schema we have defined
- `pyproject.toml` and absolute imports
  - doing a local `pip install -e .` of our pyproject.toml enables using absolute imports throughout the repo, outside of `__init__.py` files
    - this makes it easier to run any file from any working directory during testing
  - `pyproject.toml` provides an easy way to install CLI tools which we define in it, like `netwiz-backend`
  - `sync_metadata.py` keeps our requirements.txt in sync with our pyproject.toml
- `ruff` + `pre-commit`
  - `ruff` enforces a style-guide every time we try to commit
    - lots of checks are purely aesthetic or for readability
    - some checks such as for unused variables or for variables getting redefined before they are used, can be indicators of likely bugs
    - some checks notify of recommended best practices
  - `pre-commit` can honestly be kindof annoying, but helps prevent pushing bugs
- `pytest` + `GitHub workflows`
  - we have some unit tests we just run manually and other unit tests and integration tests run in workflows
- `.env` loading from a .env helps protect secrets and also helps reduce hardcoding
- `Docker` and `docker-compose` keep our code easily deployable
- modularization and separation of generic vs api vs business logic

```bash
backend/
├── netwiz_backend/           # Main package directory
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management, loading from .env
│   ├── system/                 # System endpoints (health, root, info)
│   ├── auth/                   # Auth/JWT endpoints and middleware
│   ├── json_tracker/           # Standalone utility package for parsing json, entirely independent of our other logic
│   ├── netlist/                # 🎯 Core business logic package, including the core logic and the API endpoints
│   │   ├── core/                 # core business logic, unrelated to the actual API endpoints
│   │   │   ├── validation/           # where we do all of our validation checks
│   │   │   │   ├── rules/            # where we actually define our individual validation rules
│   └── scripts/                # 🛠️ Command-line utilities
│       ├── generate_openapi.py   # OpenAPI schema generation
│       ├── sync_metadata.py      # Metadata synchronization
│       ├── check_metadata.py     # Metadata validation wrapper
│       ├── health_check.py       # API health monitoring
│       └── test_api.py           # API testing suite
├── pyproject.toml            # Package configuration (auto-synced from __init__.py)
├── requirements.txt          # All dependencies (production + development)
├── .env.example              # Environment template
├── tests/                    # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Test fixtures
```

### Frontend Development

Our frontend is built with modern React and TypeScript, focusing on developer experience, maintainability, and performance.

#### **Core Technologies**
- **React 18** with TypeScript for type-safe component development
- **Vite** for fast development builds and optimized production bundles
- **Tailwind CSS** with custom design system for consistent, responsive UI
- **React Query** for efficient API state management and caching
- **React Router** with dynamic base path support for flexible deployment

#### **Architecture & Design Patterns**
- **Custom Hooks** for API operations (`useNetlistUpload`, etc.) with automatic loading states and error handling
- **Context Providers** for global state management (`AuthContext`, `BasePathContext`)
- **Component Composition** with reusable UI components and clear separation of concerns
- **Type-Safe API Client** with custom TypeScript interfaces matching backend models
- **Monaco Editor** integration for advanced JSON editing with syntax highlighting and error navigation

#### **Development Workflow**
- **ESLint** with comprehensive React, TypeScript, and React Hooks rules for code quality
- **TypeScript** strict mode for compile-time error prevention
- **Custom Tailwind Configuration** with project-specific color palette and design tokens
- **PostCSS** integration for CSS processing and optimization
- **Hot Module Replacement** for instant development feedback

#### **Key Features**
- **Split-Pane Layout** with resizable panels for JSON editor, validation results, and graph visualization
- **Real-Time Validation** with error highlighting and navigation
- **Interactive Graph Visualization** using D3.js for component and net relationships
- **File Upload Interface** with drag-and-drop support and progress indicators
- **Responsive Design** that works across desktop and mobile devices
- **Dynamic Base Path Detection** for flexible deployment scenarios

#### **Code Organization**
```
frontend/src/
├── components/           # Reusable UI components
│   ├── auth/            # Authentication components
│   ├── netlist/         # Netlist-specific components
│   └── layout/           # Layout and navigation components
├── contexts/            # React Context providers
├── hooks/               # Custom React hooks
├── pages/               # Page-level components
├── services/            # API client and external services
├── types/               # TypeScript type definitions
└── utils/               # Utility functions and helpers
```

#### **Performance Optimizations**
- **Code Splitting** with dynamic imports for route-based chunks
- **Tree Shaking** to eliminate unused code from production bundles
- **CSS Optimization** with Tailwind's purging for minimal bundle size
- **API Caching** with React Query for efficient data fetching
- **Lazy Loading** for heavy components like the Monaco editor

#### **Deployment Flexibility**
- **Static Hosting** support for GitHub Pages and CDN deployment
- **Docker Containerization** for containerized deployments
- **Environment-Aware** configuration for different deployment targets
- **Base Path Detection** for subdirectory deployments



## License
We use the Unlicense, meaning you are free to use this code as you wish

## Contact
modularizer@gmail.com
