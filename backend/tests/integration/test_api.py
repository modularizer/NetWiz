"""
Integration tests for API endpoints
"""

import requests


class TestSystemAPI:
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = requests.get("http://localhost:5000/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = requests.get("http://localhost:5000/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "git" in data

    def test_info_endpoint(self):
        """Test API info endpoint."""
        response = requests.get("http://localhost:5000/info")
        assert response.status_code == 200
        data = response.json()
        assert "api" in data
        assert "service" in data
        assert "endpoints" in data


class TestNetlistAPI:
    def test_validate_netlist(self, sample_netlist):
        """Test netlist validation endpoint."""
        # Upload netlist first
        validation_response = requests.post(
            "http://localhost:5000/netlist/validate",
            json=sample_netlist,
            headers={"Content-Type": "application/json"},
        )
        assert validation_response.status_code == 200
        data = validation_response.json()["validation_result"]
        assert "is_valid" in data
        assert "errors" in data
