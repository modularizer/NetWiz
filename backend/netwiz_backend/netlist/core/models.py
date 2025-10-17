from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class ComponentType(str, Enum):
    """Types of electronic components"""

    IC = "IC"
    RESISTOR = "RESISTOR"
    CAPACITOR = "CAPACITOR"
    INDUCTOR = "INDUCTOR"
    DIODE = "DIODE"
    TRANSISTOR = "TRANSISTOR"
    CONNECTOR = "CONNECTOR"
    OTHER = "OTHER"


class Pin(BaseModel):
    """Represents a pin on an electronic component"""

    number: str = Field(..., description="Pin number or identifier")
    name: str | None = Field(None, description="Optional pin name")
    type: str | None = Field(None, description="Pin type (e.g., input, output, power)")


class Component(BaseModel):
    """Represents an electronic component in the netlist"""

    id: str = Field(..., description="Unique component identifier", min_length=1)
    type: ComponentType = Field(..., description="Type of electronic component")
    pins: list[Pin] = Field(
        ..., description="List of pins on this component", min_items=1
    )
    value: str | None = Field(
        None, description="Component value (e.g., '10kΩ', '100nF')"
    )
    package: str | None = Field(None, description="Component package type")
    manufacturer: str | None = Field(None, description="Component manufacturer")
    part_number: str | None = Field(None, description="Manufacturer part number")

    @validator("id")
    def validate_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Component ID cannot be blank")
        return v.strip()


class NetConnection(BaseModel):
    """Represents a connection between a net and a component pin"""

    component: str = Field(..., description="Component ID this connection belongs to")
    pin: str = Field(..., description="Pin number on the component")

    @validator("component", "pin")
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Component and pin identifiers cannot be blank")
        return v.strip()


class Net(BaseModel):
    """Represents an electrical net (connection) in the netlist"""

    id: str = Field(..., description="Unique net identifier", min_length=1)
    connections: list[NetConnection] = Field(
        ..., description="List of component pins connected to this net", min_items=1
    )
    net_type: str | None = Field(
        None, description="Type of net (e.g., 'power', 'signal', 'ground')"
    )

    @validator("id")
    def validate_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Net ID cannot be blank")
        return v.strip()


class Netlist(BaseModel):
    """Complete netlist data structure"""

    components: list[Component] = Field(
        ..., description="List of components in the netlist", min_items=1
    )
    nets: list[Net] = Field(
        ..., description="List of nets (connections) in the netlist", min_items=1
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata about the netlist"
    )

    @validator("components")
    def validate_unique_component_ids(cls, v):
        ids = [comp.id for comp in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Component IDs must be unique")
        return v

    @validator("nets")
    def validate_unique_net_ids(cls, v):
        ids = [net.id for net in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Net IDs must be unique")
        return v
