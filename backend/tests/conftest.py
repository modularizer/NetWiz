"""
Backend test configuration and fixtures
"""

import pytest


@pytest.fixture
def sample_netlist():
    """Sample netlist data for testing."""
    return {
        "components": [
            {
                "name": "U1",
                "type": "IC",
                "pins": [
                    {"number": "1", "name": "VCC", "type": "power"},
                    {"number": "2", "name": "GND", "type": "ground"},
                    {"number": "3", "name": "CLK", "type": "clock"},
                    {"number": "4", "name": "DATA", "type": "bidirectional"},
                ],
                "value": "3.3V",
                "package": "QFP-32",
                "manufacturer": "STMicroelectronics",
                "part_number": "STM32F103C8T6",
            },
            {
                "name": "R1",
                "type": "RESISTOR",
                "pins": [
                    {"number": "1", "type": "passive"},
                    {"number": "2", "type": "passive"},
                ],
                "value": "10kΩ",
                "package": "0603",
            },
        ],
        "nets": [
            {
                "name": "VCC",
                "connections": [
                    {"component": "U1", "pin": "1"},
                    {"component": "R1", "pin": "1"},
                ],
                "net_type": "power",
            },
            {
                "name": "GND",
                "connections": [
                    {"component": "U1", "pin": "2"},
                    {"component": "R1", "pin": "2"},
                ],
                "net_type": "ground",
            },
        ],
        "metadata": {
            "designer": "Test User",
            "version": "1.0",
            "description": "Test circuit for integration testing",
        },
    }
