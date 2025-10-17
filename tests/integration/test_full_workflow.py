"""
End-to-end integration tests for the complete workflow
"""
import pytest
import requests
import json
import time

class TestFullWorkflow:
    """Test complete user workflows from frontend to backend."""
    
    @pytest.fixture
    def api_base_url(self):
        return "http://localhost:5000/api"
    
    @pytest.fixture
    def frontend_url(self):
        return "http://localhost:3000"
    
    def test_upload_and_validate_workflow(self, api_base_url):
        """Test complete upload -> validate -> retrieve workflow."""
        sample_netlist = {
            "components": [
                {"id": "U1", "type": "IC", "pins": ["1", "2", "3", "4"]},
                {"id": "R1", "type": "RESISTOR", "pins": ["1", "2"]}
            ],
            "nets": [
                {"id": "VCC", "connections": [{"component": "U1", "pin": "1"}]},
                {"id": "GND", "connections": [
                    {"component": "U1", "pin": "4"},
                    {"component": "R1", "pin": "2"}
                ]}
            ]
        }
        
        # Upload netlist
        upload_response = requests.post(
            f"{api_base_url}/netlist/upload",
            json=sample_netlist,
            headers={"Content-Type": "application/json"}
        )
        assert upload_response.status_code == 201
        netlist_id = upload_response.json()["id"]
        
        # Validate netlist
        validate_response = requests.post(
            f"{api_base_url}/netlist/{netlist_id}/validate"
        )
        assert validate_response.status_code == 200
        validation_result = validate_response.json()
        assert "is_valid" in validation_result
        
        # Retrieve netlist
        get_response = requests.get(f"{api_base_url}/netlist/{netlist_id}")
        assert get_response.status_code == 200
        retrieved_netlist = get_response.json()
        assert retrieved_netlist["components"] == sample_netlist["components"]
    
    def test_invalid_netlist_validation(self, api_base_url):
        """Test validation of invalid netlist data."""
        invalid_netlist = {
            "components": [
                {"id": "", "type": "IC", "pins": ["1", "2"]}  # Blank name
            ],
            "nets": []
        }
        
        upload_response = requests.post(
            f"{api_base_url}/netlist/upload",
            json=invalid_netlist,
            headers={"Content-Type": "application/json"}
        )
        assert upload_response.status_code == 201
        netlist_id = upload_response.json()["id"]
        
        validate_response = requests.post(
            f"{api_base_url}/netlist/{netlist_id}/validate"
        )
        assert validate_response.status_code == 200
        validation_result = validate_response.json()
        assert validation_result["is_valid"] == False
        assert len(validation_result["errors"]) > 0
