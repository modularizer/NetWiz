# PCB Netlist Visualizer + Validator

A proof-of-concept application for visualizing and validating PCB netlist data. This tool allows users to upload netlist files, visualize them as interactive graphs, and validate them against basic electrical rules.

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
- **Backend**: Python Flask/FastAPI server
- **Database**: MongoDB for data persistence
- **Deployment**: Docker containerization for cloud deployment

## Requirements

- Client-server architecture
- Local development support
- Cloud deployment ready (AWS, etc.)
- Docker containerization

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB
- Docker (for deployment)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd NetWiz
```

2. Install Python dependencies
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies
```bash
npm install
```

4. Set up MongoDB
```bash
# Start MongoDB locally
mongod
```

5. Run the application
```bash
# Start backend
python app.py

# Start frontend (in separate terminal)
npm start
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Project Structure

```
NetWiz/
├── backend/          # Python backend
├── frontend/         # React frontend
├── docs/            # Documentation
├── docker/          # Docker configuration
├── tests/           # Test files
├── requirements.txt # Python dependencies
├── package.json     # Node.js dependencies
└── README.md        # This file
```

## Development

### Backend Development
- Python Flask/FastAPI server
- MongoDB integration
- RESTful API endpoints
- Netlist validation engine

### Frontend Development
- React components
- SVG/Canvas visualization
- File upload interface
- Validation results display

## API Endpoints

- `POST /api/netlist/upload` - Upload netlist file
- `GET /api/netlist/:id` - Retrieve netlist data
- `POST /api/netlist/:id/validate` - Validate netlist
- `GET /api/submissions` - List user submissions
- `GET /api/validation/:id` - Get validation results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Contact

[Add contact information]