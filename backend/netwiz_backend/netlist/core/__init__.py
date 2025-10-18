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

# Import validation
