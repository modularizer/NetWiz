"""
Backend test configuration and fixtures
"""
import pytest
from flask import Flask
from pymongo import MongoClient
import tempfile
import os

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['MONGODB_URI'] = 'mongodb://localhost:27017/netwiz_test'
    
    # Initialize app components here
    # app.register_blueprint(api_bp)
    
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def test_db():
    """Create a test database."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client.netwiz_test
    yield db
    client.drop_database('netwiz_test')
    client.close()

@pytest.fixture
def sample_netlist():
    """Sample netlist data for testing."""
    return {
        "components": [
            {
                "id": "U1",
                "type": "IC",
                "pins": ["1", "2", "3", "4"]
            },
            {
                "id": "R1", 
                "type": "RESISTOR",
                "pins": ["1", "2"]
            }
        ],
        "nets": [
            {
                "id": "VCC",
                "connections": [{"component": "U1", "pin": "1"}]
            },
            {
                "id": "GND",
                "connections": [
                    {"component": "U1", "pin": "4"},
                    {"component": "R1", "pin": "2"}
                ]
            }
        ]
    }
