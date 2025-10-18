"""
NetWiz Core Netlist Module

This package contains the fundamental data models and validation logic
for representing and validating PCB netlists in the NetWiz system.

Core Components:
- models: Data structures for netlist representation
- validation: Validation logic and error reporting

Example:
    ```python
    from netwiz_backend.netlist.core import Netlist, Component, Pin, validate_netlist_internal

    # Create a simple circuit
    circuit = Netlist(
        components=[
            Component(
                id="U1",
                type=ComponentType.IC,
                pins=[Pin(number="1", name="VCC")]
            )
        ],
        nets=[
            Net(
                id="VCC",
                connections=[NetConnection(component="U1", pin="1")]
            )
        ]
    )

    # Validate the circuit
    result = validate_netlist_internal(circuit)
    ```
"""

# Import core models
# Import JSON tracker
from netwiz_backend.json_tracker import TrackedJson
from netwiz_backend.json_tracker.types import LocationInfo

from .models import (
    Component,
    ComponentType,
    Net,
    NetConnection,
    Netlist,
    NetType,
    Pin,
    PinType,
)

# Import validation
from .validation import (
    ValidationError,
    ValidationErrorType,
    ValidationResult,
    validate_netlist_internal,
)

__all__ = [
    # Core models
    "Component",
    "ComponentType",
    "Net",
    "NetConnection",
    "Netlist",
    "NetType",
    "Pin",
    "PinType",
    # Validation
    "ValidationError",
    "ValidationErrorType",
    "ValidationResult",
    "validate_netlist_internal",
    # JSON Tracker
    "TrackedJson",
    "LocationInfo",
]
