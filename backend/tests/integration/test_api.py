"""
Integration tests for API endpoints
"""
import pytest
import json
from backend.tests.conftest import app, client, sample_netlist

class TestNetlistAPI:
    
    def test_upload_netlist(self, client, sample_netlist):
        """Test netlist upload endpoint."""
        response = client.post('/api/netlist/upload', 
                             data=json.dumps(sample_netlist),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'id' in data
    
    def test_get_netlist(self, client, sample_netlist):
        """Test retrieving netlist by ID."""
        # First upload a netlist
        upload_response = client.post('/api/netlist/upload',
                                   data=json.dumps(sample_netlist),
                                   content_type='application/json')
        netlist_id = json.loads(upload_response.data)['id']
        
        # Then retrieve it
        response = client.get(f'/api/netlist/{netlist_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['components'] == sample_netlist['components']
    
    def test_validate_netlist(self, client, sample_netlist):
        """Test netlist validation endpoint."""
        # Upload netlist first
        upload_response = client.post('/api/netlist/upload',
                                   data=json.dumps(sample_netlist),
                                   content_type='application/json')
        netlist_id = json.loads(upload_response.data)['id']
        
        # Validate it
        response = client.post(f'/api/netlist/{netlist_id}/validate')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'is_valid' in data
        assert 'errors' in data
