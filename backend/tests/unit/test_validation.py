"""
Unit tests for netlist validation logic
"""
import pytest
from backend.services.validation import NetlistValidator
from backend.tests.conftest import sample_netlist

class TestNetlistValidator:
    
    def test_validate_blank_names(self, sample_netlist):
        """Test validation of blank component names."""
        validator = NetlistValidator()
        
        # Test with valid names
        result = validator.validate(sample_netlist)
        assert result.is_valid == True
        
        # Test with blank component name
        invalid_netlist = sample_netlist.copy()
        invalid_netlist["components"][0]["id"] = ""
        
        result = validator.validate(invalid_netlist)
        assert result.is_valid == False
        assert "blank name" in str(result.errors).lower()
    
    def test_validate_gnd_connectivity(self, sample_netlist):
        """Test GND connectivity validation."""
        validator = NetlistValidator()
        
        # Test with proper GND connections
        result = validator.validate(sample_netlist)
        assert result.is_valid == True
        
        # Test with missing GND connections
        invalid_netlist = sample_netlist.copy()
        invalid_netlist["nets"] = [net for net in invalid_netlist["nets"] if net["id"] != "GND"]
        
        result = validator.validate(invalid_netlist)
        assert result.is_valid == False
        assert "gnd" in str(result.errors).lower()
