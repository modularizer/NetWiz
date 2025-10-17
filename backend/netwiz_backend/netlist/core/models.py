"""
Core data models for PCB netlist representation.

This module defines the fundamental data structures used to represent electronic
circuits in netlist format. These models form the foundation of the NetWiz
validation system and are designed to be:

- **Type-safe**: Using Pydantic for runtime validation
- **Extensible**: Easy to add new component types and properties
- **Validated**: Built-in constraints ensure data integrity
- **Serializable**: JSON-compatible for API communication

The models follow a hierarchical structure:
- Netlist (top-level container)
  - Components (electronic parts)
    - Pins (connection points)
  - Nets (electrical connections)
    - NetConnections (component-to-net links)

Example:
    ```python
    from netwiz_backend.netlist.core.models import Netlist, Component, Pin, Net, NetConnection, ComponentType, PinDirection

    # Create a simple circuit
    netlist = Netlist(
        components=[
            Component(
                name="U1",
                type=ComponentType.IC,
                pins=[Pin(number="1", name="VCC", direction=PinDirection.POWER), Pin(number="2", name="GND", direction=PinDirection.GROUND)]
            )
        ],
        nets=[
            Net(
                name="VCC",
                connections=[NetConnection(component="U1", pin="1")]
            )
        ]
    )
    ```
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, conlist, constr, field_validator


class PinDirection(str, Enum):
    """
    Enumeration of pin electrical directions and functions.

    This enum defines the electrical characteristics and signal flow direction
    for component pins. Each direction represents a different electrical
    function and usage pattern.

    Attributes:
        INPUT: Pin receives signals from external sources
        OUTPUT: Pin drives signals to external loads
        BIDIRECTIONAL: Pin can both receive and drive signals
        POWER: Pin provides power supply voltage
        GROUND: Pin provides ground reference
        PASSIVE: Pin for passive components (resistors, capacitors, etc.)
    """

    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    POWER = "power"
    GROUND = "ground"
    PASSIVE = "passive"


class ComponentType(str, Enum):
    """
    Enumeration of electronic component types.

    This enum defines the standard component categories used in PCB netlists.
    Each type represents a different class of electronic components with
    distinct electrical characteristics and usage patterns.

    Attributes:
        IC: Integrated circuits (microcontrollers, processors, etc.)
        RESISTOR: Passive components that resist electrical current
        CAPACITOR: Passive components that store electrical energy
        INDUCTOR: Passive components that store energy in magnetic fields
        DIODE: Semiconductor devices that allow current flow in one direction
        TRANSISTOR: Semiconductor devices for amplification/switching
        CONNECTOR: Mechanical interfaces for electrical connections
        OTHER: Components that don't fit standard categories
    """

    IC = "IC"
    RESISTOR = "RESISTOR"
    CAPACITOR = "CAPACITOR"
    INDUCTOR = "INDUCTOR"
    DIODE = "DIODE"
    TRANSISTOR = "TRANSISTOR"
    CONNECTOR = "CONNECTOR"
    OTHER = "OTHER"


class Pin(BaseModel):
    """
    Represents a pin on an electronic component.

    A pin is a physical connection point on a component that can be connected
    to nets in the circuit.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"number": "1", "name": "VCC", "type": "power", "direction": "power"},
                {"number": "2", "name": "GND", "type": "ground", "direction": "ground"},
                {"number": "3", "name": "CLK", "type": "input", "direction": "input"},
                {
                    "number": "4",
                    "name": "DATA",
                    "type": "output",
                    "direction": "output",
                },
                {"number": "5", "direction": "passive"},
            ]
        }
    }

    number: constr(min_length=1, strip_whitespace=True) = Field(
        ...,
        description="Pin number or identifier (e.g., '1', 'A1', 'VCC')",
        examples=["1", "A1", "VCC", "GND", "CLK"],
    )
    name: constr(strip_whitespace=True) | None = Field(
        default=None,
        description="Optional pin name (e.g., 'VCC', 'GND', 'CLK')",
        examples=["VCC", "GND", "CLK", "RESET", "DATA"],
    )
    type: constr(strip_whitespace=True) | None = Field(
        default=None,
        description="Pin type classification (e.g., 'power', 'input', 'output')",
        examples=["power", "ground", "input", "output", "bidirectional"],
    )
    direction: PinDirection | None = Field(
        default=None,
        description="Electrical direction and function of the pin",
        examples=["input", "output", "bidirectional", "power", "ground", "passive"],
    )


class Component(BaseModel):
    """
    Represents an electronic component in the netlist.

    A component is a discrete electronic part (resistor, capacitor, IC, etc.)
    that can be placed on a PCB. Each component has a unique identifier,
    a type classification, and a list of pins that define its connection points.

    Attributes:
        id: Unique identifier for the component (e.g., "U1", "R5", "C10")
        type: Component type from ComponentType enum
        pins: List of pins on this component (minimum 1 required)
        value: Optional component value (e.g., "10kΩ", "100nF", "3.3V")
        package: Optional physical package type (e.g., "SOIC-8", "0603")
        manufacturer: Optional manufacturer name (e.g., "Texas Instruments")
        part_number: Optional manufacturer part number (e.g., "LM358")

    Validation:
        - Component ID must be non-empty and unique within the netlist
        - At least one pin is required
        - All pin numbers must be unique within the component

    Example:
        ```python
        # Microcontroller
        mcu = Component(
            name="U1",
            type=ComponentType.IC,
            pins=[
                Pin(number="1", name="VCC", type="power", direction=PinDirection.POWER),
                Pin(number="2", name="GND", type="power", direction=PinDirection.GROUND),
                Pin(number="3", name="CLK", type="input", direction=PinDirection.INPUT)
            ],
            value="3.3V",
            package="QFP-32",
            manufacturer="STMicroelectronics",
            part_number="STM32F103C8T6"
        )

        # Resistor
        resistor = Component(
            name="R1",
            type=ComponentType.RESISTOR,
            pins=[Pin(number="1", direction=PinDirection.PASSIVE), Pin(number="2", direction=PinDirection.PASSIVE)],
            value="10kΩ",
        )
        ```
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "U1",
                    "type": "IC",
                    "pins": [
                        {
                            "number": "1",
                            "name": "VCC",
                            "type": "power",
                            "direction": "power",
                        },
                        {
                            "number": "2",
                            "name": "GND",
                            "type": "ground",
                            "direction": "ground",
                        },
                        {
                            "number": "3",
                            "name": "CLK",
                            "type": "input",
                            "direction": "input",
                        },
                    ],
                    "value": "3.3V",
                    "package": "QFP-32",
                    "manufacturer": "STMicroelectronics",
                    "part_number": "STM32F103C8T6",
                },
                {
                    "name": "R1",
                    "type": "RESISTOR",
                    "pins": [{"number": "1"}, {"number": "2"}],
                    "value": "10kΩ",
                    "package": "0603",
                },
            ]
        }
    }

    name: constr(min_length=1, strip_whitespace=True) = Field(
        ...,
        description="Unique component name",
        examples=["U1", "R5", "C10", "IC1", "CONN1"],
    )
    type: ComponentType = Field(..., description="Type of electronic component")
    pins: conlist(Pin, min_length=1) = Field(
        ...,
        description="List of pins on this component",
        examples=[[{"number": "1", "name": "VCC"}, {"number": "2", "name": "GND"}]],
    )
    value: constr(strip_whitespace=True) | None = Field(
        default=None,
        description="Component value (e.g., '10kΩ', '100nF')",
        examples=["10kΩ", "100nF", "3.3V", "1MHz", "0.1µF"],
    )
    package: constr(strip_whitespace=True) | None = Field(
        default=None,
        description="Component package type",
        examples=["SOIC-8", "QFP-32", "0603", "DIP-14", "BGA-256"],
    )
    manufacturer: constr(strip_whitespace=True) | None = Field(
        default=None,
        description="Component manufacturer",
        examples=["Texas Instruments", "STMicroelectronics", "Analog Devices"],
    )
    part_number: constr(strip_whitespace=True) | None = Field(
        default=None,
        description="Manufacturer part number",
        examples=["LM358", "STM32F103C8T6", "AD620"],
    )


class NetConnection(BaseModel):
    """
    Represents a connection between a net and a component pin.

    A NetConnection defines how a specific pin on a component is connected
    to a net. This creates the electrical connectivity in the circuit.
    Each connection must reference a valid component ID and pin number.

    Attributes:
        component: ID of the component this connection belongs to
        pin: Pin number/identifier on the component

    Validation:
        - Both component and pin identifiers must be non-empty
        - Component ID must exist in the netlist's components
        - Pin number must exist on the specified component

    Example:
        ```python
        # Connect pin 1 of component U1 to net VCC
        connection = NetConnection(component="U1", pin="1")

        # Connect pin A1 of component R5 to net SIGNAL
        connection = NetConnection(component="R5", pin="A1")
        ```
    """

    component: constr(min_length=1, strip_whitespace=True) = Field(
        ...,
        description="Component ID this connection belongs to",
        examples=["U1", "R5", "C10", "IC1"],
    )
    pin: constr(min_length=1, strip_whitespace=True) = Field(
        ...,
        description="Pin number on the component",
        examples=["1", "A1", "VCC", "GND"],
    )


class Net(BaseModel):
    """
    Represents an electrical net (connection) in the netlist.

    A net is an electrical connection that links multiple component pins together.
    All pins connected to the same net are electrically equivalent and share
    the same voltage. Nets form the wiring topology of the circuit.

    Attributes:
        id: Unique identifier for the net (e.g., "VCC", "GND", "CLK", "DATA")
        connections: List of component pins connected to this net
        net_type: Optional classification of net purpose (e.g., "power", "signal", "ground")

    Validation:
        - Net ID must be non-empty and unique within the netlist
        - At least one connection is required
        - All referenced components and pins must exist in the netlist

    Example:
        ```python
        # Power supply net
        vcc_net = Net(
            name="VCC",
            connections=[
                NetConnection(component="U1", pin="1"),
                NetConnection(component="U2", pin="1")
            ],
            net_type="power"
        )

        # Signal net
        clock_net = Net(
            name="CLK",
            connections=[
                NetConnection(component="U1", pin="3"),
                NetConnection(component="U2", pin="2")
            ],
            net_type="signal"
        )
        ```
    """

    name: constr(min_length=1, strip_whitespace=True) = Field(
        ...,
        description="Unique net name",
        examples=["VCC", "GND", "CLK", "DATA", "RESET", "SIGNAL"],
    )
    connections: conlist(NetConnection, min_length=1) = Field(
        ...,
        description="List of component pins connected to this net",
        examples=[[{"component": "U1", "pin": "1"}, {"component": "R1", "pin": "1"}]],
    )
    net_type: constr(strip_whitespace=True) | None = Field(
        default=None,
        description="Type of net (e.g., 'power', 'signal', 'ground')",
        examples=["power", "ground", "signal", "clock", "analog"],
    )


class Netlist(BaseModel):
    """
    Complete netlist data structure representing an electronic circuit.

    Contains components and their electrical connections for circuit analysis.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Simple MCU Circuit",
                    "description": "A basic microcontroller circuit with power and ground",
                    "value": {
                        "components": [
                            {
                                "name": "U1",
                                "type": "IC",
                                "pins": [
                                    {
                                        "number": "1",
                                        "name": "VCC",
                                        "type": "power",
                                        "direction": "power",
                                    },
                                    {
                                        "number": "2",
                                        "name": "GND",
                                        "type": "ground",
                                        "direction": "ground",
                                    },
                                    {
                                        "number": "3",
                                        "name": "CLK",
                                        "type": "input",
                                        "direction": "input",
                                    },
                                ],
                                "value": "3.3V",
                                "package": "QFP-32",
                                "manufacturer": "STMicroelectronics",
                                "part_number": "STM32F103C8T6",
                            },
                            {
                                "name": "R1",
                                "type": "RESISTOR",
                                "pins": [{"number": "1"}, {"number": "2"}],
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
                            "designer": "John Doe",
                            "version": "1.0",
                            "description": "Simple MCU circuit with pull-up resistor",
                        },
                    },
                },
                {
                    "summary": "Power Supply Circuit",
                    "description": "A power supply circuit with voltage regulation",
                    "value": {
                        "components": [
                            {
                                "name": "U1",
                                "type": "IC",
                                "pins": [
                                    {
                                        "number": "1",
                                        "name": "VIN",
                                        "type": "input",
                                        "direction": "input",
                                    },
                                    {
                                        "number": "2",
                                        "name": "VOUT",
                                        "type": "output",
                                        "direction": "output",
                                    },
                                    {
                                        "number": "3",
                                        "name": "GND",
                                        "type": "ground",
                                        "direction": "ground",
                                    },
                                ],
                                "value": "5V",
                                "package": "TO-220",
                                "manufacturer": "Linear Technology",
                                "part_number": "LM7805",
                            },
                            {
                                "name": "C1",
                                "type": "CAPACITOR",
                                "pins": [{"number": "1"}, {"number": "2"}],
                                "value": "100µF",
                                "package": "0805",
                            },
                        ],
                        "nets": [
                            {
                                "name": "VIN",
                                "connections": [
                                    {"component": "U1", "pin": "1"},
                                    {"component": "C1", "pin": "1"},
                                ],
                                "net_type": "power",
                            },
                            {
                                "name": "VOUT",
                                "connections": [{"component": "U1", "pin": "2"}],
                                "net_type": "power",
                            },
                            {
                                "name": "GND",
                                "connections": [
                                    {"component": "U1", "pin": "3"},
                                    {"component": "C1", "pin": "2"},
                                ],
                                "net_type": "ground",
                            },
                        ],
                    },
                },
            ]
        }
    }

    components: conlist(Component, min_length=1) = Field(
        ..., description="List of electronic components in the circuit"
    )
    nets: conlist(Net, min_length=1) = Field(
        ..., description="List of electrical nets (connections) between components"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional additional information about the netlist"
    )

    @field_validator("components")
    @classmethod
    def validate_unique_component_names(cls, v):
        names = [comp.name for comp in v]
        if len(names) != len(set(names)):
            raise ValueError("Component names must be unique")
        return v

    @field_validator("nets")
    @classmethod
    def validate_unique_net_names(cls, v):
        names = [net.name for net in v]
        if len(names) != len(set(names)):
            raise ValueError("Net names must be unique")
        return v
