# NetWiz Core Netlist Module

> **Core data models and validation logic for PCB netlist representation**

This directory contains the fundamental building blocks of the NetWiz system - the core data models that represent electronic circuits and the validation logic that ensures circuit integrity.

## 📁 Directory Structure

```
core/
├── __init__.py          # Package initialization
├── models.py            # Core data models (Netlist, Component, Pin, Net, etc.)
├── validation.py        # Validation logic and rules
└── README.md           # This file
```

## 🏗️ Architecture Overview

The core module follows a hierarchical data model that mirrors the structure of electronic circuits:

```
Netlist (Top-level container)
├── Components (Electronic parts)
│   └── Pins (Connection points)
└── Nets (Electrical connections)
    └── NetConnections (Component-to-net links)
```

## 📋 Core Models (`models.py`)

### ComponentType Enum
Defines standard electronic component categories:
- `IC` - Integrated circuits
- `RESISTOR` - Passive resistive components
- `CAPACITOR` - Passive capacitive components
- `INDUCTOR` - Passive inductive components
- `DIODE` - Semiconductor diodes
- `TRANSISTOR` - Semiconductor transistors
- `CONNECTOR` - Mechanical connectors
- `OTHER` - Miscellaneous components

### Pin Model
Represents a connection point on a component:
```python
Pin(
    number="1",           # Required: Unique pin identifier
    name="VCC",           # Optional: Human-readable name
    type="power"          # Optional: Pin type classification
)
```

### Component Model
Represents an electronic component:
```python
Component(
    id="U1",              # Required: Unique component ID
    type=ComponentType.IC, # Required: Component type
    pins=[...],           # Required: List of pins (min 1)
    value="3.3V",        # Optional: Component value
    package="QFP-32",     # Optional: Physical package
    manufacturer="ST",   # Optional: Manufacturer
    part_number="STM32"   # Optional: Part number
)
```

### NetConnection Model
Links a component pin to a net:
```python
NetConnection(
    component="U1",       # Required: Component ID
    pin="1"               # Required: Pin number
)
```

### Net Model
Represents an electrical connection:
```python
Net(
    id="VCC",             # Required: Unique net identifier
    connections=[...],    # Required: List of connections (min 1)
    net_type="power"     # Optional: Net classification
)
```

### Netlist Model
Top-level container for the complete circuit:
```python
Netlist(
    components=[...],    # Required: List of components (min 1)
    nets=[...],          # Required: List of nets (min 1)
    metadata={...}       # Optional: Additional information
)
```

## ✅ Validation System (`validation.py`)

### ValidationError Model
Captures detailed error information:
```python
ValidationError(
    error_type="duplicate_component_id",
    message="Component IDs must be unique",
    component_id="U1",    # Optional: Specific component
    net_id=None,          # Optional: Specific net
    severity="error"      # "error" or "warning"
)
```

### ValidationResult Model
Comprehensive validation results:
```python
ValidationResult(
    is_valid=False,       # True if no errors found
    errors=[...],         # List of errors
    warnings=[...],       # List of warnings
    validation_timestamp=datetime.now(),
    validation_rules_applied=["rule1", "rule2"]
)
```

### Validation Rules

The system applies comprehensive validation rules:

1. **Naming Rules**
   - Component IDs must be non-empty and unique
   - Net IDs must be non-empty and unique
   - All identifiers are automatically trimmed of whitespace

2. **Connectivity Rules**
   - All nets must have at least one connection
   - Components should be connected to nets (warning if not)

3. **Electrical Rules**
   - Ground nets (GND, GROUND, VSS) should have multiple connections
   - Power nets should be properly distributed

4. **Design Rules**
   - Extensible system for custom validation rules

## 🚀 Usage Examples

### Creating a Simple Circuit

```python
from netwiz_backend.netlist.core.models import (
    Netlist, Component, Pin, Net, NetConnection, ComponentType
)

# Create components
mcu = Component(
    id="U1",
    type=ComponentType.IC,
    pins=[
        Pin(number="1", name="VCC", type="power"),
        Pin(number="2", name="GND", type="power"),
        Pin(number="3", name="CLK", type="input")
    ],
    value="3.3V",
    package="QFP-32",
    manufacturer="STMicroelectronics",
    part_number="STM32F103C8T6"
)

resistor = Component(
    id="R1",
    type=ComponentType.RESISTOR,
    pins=[Pin(number="1"), Pin(number="2")],
    value="10kΩ",
    package="0603"
)

# Create nets
vcc_net = Net(
    id="VCC",
    connections=[
        NetConnection(component="U1", pin="1"),
        NetConnection(component="R1", pin="1")
    ],
    net_type="power"
)

gnd_net = Net(
    id="GND",
    connections=[
        NetConnection(component="U1", pin="2"),
        NetConnection(component="R1", pin="2")
    ],
    net_type="ground"
)

# Create netlist
circuit = Netlist(
    components=[mcu, resistor],
    nets=[vcc_net, gnd_net],
    metadata={
        "designer": "John Doe",
        "version": "1.0",
        "description": "Simple MCU circuit with pull-up resistor"
    }
)
```

### Validating a Netlist

```python
from netwiz_backend.netlist.core.validation import validate_netlist_internal

# Validate the circuit
result = validate_netlist_internal(circuit)

if result.is_valid:
    print("✅ Circuit is valid!")
else:
    print("❌ Validation errors found:")
    for error in result.errors:
        print(f"  - {error.message}")
        if error.component_id:
            print(f"    Component: {error.component_id}")
        if error.net_id:
            print(f"    Net: {error.net_id}")

if result.warnings:
    print("⚠️ Warnings:")
    for warning in result.warnings:
        print(f"  - {warning.message}")
```

## 🔧 Data Validation Features

### Automatic Validation
- **Type Safety**: Pydantic ensures all data types are correct
- **Constraint Validation**: Built-in constraints prevent invalid data
- **Whitespace Handling**: Automatic trimming of string fields
- **Required Fields**: Enforced minimum requirements

### Custom Validation
- **Field Validators**: Custom validation logic for complex rules
- **Cross-Field Validation**: Validation that spans multiple fields
- **Business Rules**: Domain-specific validation logic

### Error Reporting
- **Detailed Messages**: Clear, actionable error descriptions
- **Location Information**: Specific component/net identification
- **Severity Levels**: Distinction between errors and warnings
- **Rule Tracking**: Audit trail of applied validation rules

## 🎯 Design Principles

### 1. **Type Safety First**
All models use Pydantic for runtime type checking and validation, ensuring data integrity at every level.

### 2. **Hierarchical Structure**
The data model mirrors the physical structure of electronic circuits, making it intuitive for engineers.

### 3. **Extensibility**
The system is designed to be easily extended with new component types, validation rules, and metadata fields.

### 4. **Validation-Driven**
Comprehensive validation ensures circuit integrity and catches common design errors early.

### 5. **API-Ready**
All models are JSON-serializable and designed for seamless API integration.

## 🔍 Best Practices

### Component Naming
- Use consistent naming conventions (U1, U2 for ICs; R1, R2 for resistors)
- Include meaningful prefixes for different component types
- Keep IDs short but descriptive

### Net Naming
- Use standard net names (VCC, GND, CLK, DATA)
- Group related signals with consistent naming patterns
- Use descriptive names for custom signals

### Pin Definitions
- Always include pin numbers
- Add pin names for important signals (power, clock, reset)
- Use pin types to categorize functionality

### Validation
- Always validate netlists before processing
- Review warnings even if validation passes
- Use metadata to track design information

## 🚧 Future Enhancements

### Planned Features
- **Advanced Validation Rules**: More sophisticated electrical rule checking
- **Component Libraries**: Standard component definitions
- **Netlist Comparison**: Diff functionality for design changes
- **Export Formats**: Support for additional netlist formats
- **Performance Optimization**: Faster validation for large circuits

### Extension Points
- **Custom Component Types**: Add domain-specific component categories
- **Validation Plugins**: Plugin system for custom validation rules
- **Metadata Schemas**: Structured metadata validation
- **Import/Export**: Additional format support

## 📚 Related Documentation

- [NetWiz Backend README](../../README.md) - Overall backend documentation
- [API Documentation](../../../README.md) - API endpoint documentation
- [Validation Rules](./validation.py) - Detailed validation rule documentation
- [Data Models](./models.py) - Complete model reference

## 🤝 Contributing

When contributing to the core module:

1. **Follow Type Safety**: Always use proper type hints
2. **Add Validation**: Include appropriate validation rules
3. **Update Documentation**: Keep docstrings and examples current
4. **Test Thoroughly**: Ensure all validation rules work correctly
5. **Maintain Compatibility**: Don't break existing API contracts

---

*This core module forms the foundation of the NetWiz system. It's designed to be robust, extensible, and easy to use for electronic circuit representation and validation.*
