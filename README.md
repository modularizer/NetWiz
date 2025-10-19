# PCB Netlist Visualizer + Validator

A proof-of-concept application for visualizing and validating PCB netlist data. This tool allows users to upload netlist files, visualize them as interactive graphs, and validate them against basic electrical rules.


## Demo (No Source Code Required)
Want to run NetWiz without cloning the repository? Just use the GitHub Pages static frontend and download and run the Docker containers as the backend:

1. Go to frontend at https://modularizer.github.io/NetWiz/
2. Launch backend with the following oneliner
```bash
f=$(mktemp) && curl -s https://raw.githubusercontent.com/modularizer/NetWiz/main/docker-compose.prod.yml -o $f && trap "docker-compose -f $f down --rmi all --volumes --remove-orphans; rm $f" EXIT && docker-compose -f $f up
```


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
- Name data validation (no blank names)
- Ground (GND) connectivity verification
- Additional electrical rule validation (extensible)

## Architecture

- **Frontend**: React-based web interface
- **Backend**: Python FastAPI server
- **Database**: MongoDB for data persistence
- **Deployment**: Docker containerization for cloud deployment

## Requirements

- Client-server architecture
- Local development support
- Cloud deployment ready (AWS, etc.)
- Docker containerization


## Quick Start (Standard)
### Prerequisites
- Python 3.10+
- Node.js 16+
- MongoDB
- Docker (for deployment)

### From Docker
```bash
git clone git@github.com:modularizer/NetWiz.git
cd NetWiz
cp .env.example .env
docker-compose up --build
```

### From Source
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

# Generate TypeScript types from OpenAPI schema
npm run generate-api-types
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

## Development

### Backend Development
- Python FastAPI server
- MongoDB integration
- Netlist validation engine

### Frontend Development
- React components
- SVG/Canvas visualization
- File upload interface
- Validation results display

## API Endpoints
see `backend/openapi.json`, also hosted by the api at `/docs`, e.g. http://locahost:5000/docs

## License
We use the Unlicense, meaning you are free to use this code as you wish

## Contact
modularizer@gmail.com
