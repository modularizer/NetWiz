# Netlist JSON Structure

This document explains the structure of a netlist JSON file used by the NetWiz API. A netlist represents an electronic circuit as a collection of components and their electrical connections.

## 📋 Basic Structure

A netlist JSON has this top-level structure:

```json
{
  "components": [...],
  "nets": [...],
  "metadata": {...}
}
```

## 🔧 Components

Each component represents an electronic part (resistor, capacitor, IC, etc.):

```json
{
  "id": "U1",
  "type": "IC",
  "pins": [
    {
      "number": "1",
      "name": "VCC",
      "type": "power"
    },
    {
      "number": "2",
      "name": "GND",
      "type": "ground"
    }
  ],
  "value": "3.3V",
  "package": "QFP-32",
  "manufacturer": "STMicroelectronics",
  "part_number": "STM32F103C8T6"
}
```

### Component Fields

- **`id`** (required): Unique identifier (e.g., "U1", "R5", "C10")
- **`type`** (required): Component type - one of: `IC`, `RESISTOR`, `CAPACITOR`, `INDUCTOR`, `DIODE`, `TRANSISTOR`, `CONNECTOR`, `OTHER`
- **`pins`** (required): Array of pin objects (minimum 1)
- **`value`** (optional): Component value (e.g., "10kΩ", "100nF", "3.3V")
- **`package`** (optional): Physical package type (e.g., "SOIC-8", "0603")
- **`manufacturer`** (optional): Manufacturer name (e.g., "Texas Instruments")
- **`part_number`** (optional): Manufacturer part number (e.g., "LM358")

### Pin Fields

- **`number`** (required): Pin number or identifier (e.g., "1", "A1", "VCC")
- **`name`** (optional): Pin name (e.g., "VCC", "GND", "CLK")
- **`type`** (optional): Pin type (e.g., "power", "input", "output")

## 🔌 Nets

Each net represents an electrical connection between component pins:

```json
{
  "id": "VCC",
  "connections": [
    {
      "component": "U1",
      "pin": "1"
    },
    {
      "component": "R1",
      "pin": "1"
    }
  ],
  "net_type": "power"
}
```

### Net Fields

- **`id`** (required): Unique net identifier (e.g., "VCC", "GND", "CLK")
- **`connections`** (required): Array of connections (minimum 1)
- **`net_type`** (optional): Net type (e.g., "power", "ground", "signal")

### Connection Fields

- **`component`** (required): Component ID this connection belongs to
- **`pin`** (required): Pin number/identifier on the component

## 📊 Metadata

Optional additional information about the netlist:

```json
{
  "metadata": {
    "designer": "John Doe",
    "version": "1.0",
    "description": "Simple MCU circuit with pull-up resistor",
    "project": "IoT Sensor"
  }
}
```

## 🎯 Complete Example

Here's a complete netlist JSON for a simple microcontroller circuit:

```json
{
  "components": [
    {
      "id": "U1",
      "type": "IC",
      "pins": [
        {"number": "1", "name": "VCC", "type": "power"},
        {"number": "2", "name": "GND", "type": "ground"},
        {"number": "3", "name": "CLK", "type": "input"}
      ],
      "value": "3.3V",
      "package": "QFP-32",
      "manufacturer": "STMicroelectronics",
      "part_number": "STM32F103C8T6"
    },
    {
      "id": "R1",
      "type": "RESISTOR",
      "pins": [
        {"number": "1"},
        {"number": "2"}
      ],
      "value": "10kΩ",
      "package": "0603"
    }
  ],
  "nets": [
    {
      "id": "VCC",
      "connections": [
        {"component": "U1", "pin": "1"},
        {"component": "R1", "pin": "1"}
      ],
      "net_type": "power"
    },
    {
      "id": "GND",
      "connections": [
        {"component": "U1", "pin": "2"},
        {"component": "R1", "pin": "2"}
      ],
      "net_type": "ground"
    }
  ],
  "metadata": {
    "designer": "John Doe",
    "version": "1.0",
    "description": "Simple MCU circuit with pull-up resistor"
  }
}
```

## ✅ Validation Rules

The API validates netlists against these rules:

1. **Non-empty IDs**: Component and net IDs cannot be blank
2. **Unique IDs**: All component IDs must be unique, all net IDs must be unique
3. **Valid Connections**: All net connections must reference existing components and pins
4. **Minimum Requirements**: At least one component and one net required
5. **Connected Components**: Components should be connected to nets (warnings for unconnected)

## 🚀 Component Types

| Type | Description | Example |
|------|-------------|---------|
| `IC` | Integrated circuits | Microcontrollers, processors |
| `RESISTOR` | Passive resistors | Pull-up resistors, current limiting |
| `CAPACITOR` | Passive capacitors | Decoupling, filtering |
| `INDUCTOR` | Passive inductors | Power filtering, RF circuits |
| `DIODE` | Semiconductor diodes | Protection, rectification |
| `TRANSISTOR` | Semiconductor transistors | Amplification, switching |
| `CONNECTOR` | Mechanical connectors | Headers, jacks, sockets |
| `OTHER` | Components that don't fit standard categories | Custom parts |

## 📝 Field Constraints

### Required Fields
- `components[].id` - Must be non-empty string
- `components[].type` - Must be valid ComponentType
- `components[].pins` - Must have at least 1 pin
- `components[].pins[].number` - Must be non-empty string
- `nets[].id` - Must be non-empty string
- `nets[].connections` - Must have at least 1 connection
- `nets[].connections[].component` - Must be non-empty string
- `nets[].connections[].pin` - Must be non-empty string

### Optional Fields
- All other fields are optional and can be omitted
- String fields are automatically trimmed of whitespace
- Empty strings are treated as missing values

## 🔍 Common Patterns

### Power Distribution
```json
{
  "id": "VCC",
  "connections": [
    {"component": "U1", "pin": "1"},
    {"component": "U2", "pin": "1"},
    {"component": "C1", "pin": "1"}
  ],
  "net_type": "power"
}
```

### Ground Plane
```json
{
  "id": "GND",
  "connections": [
    {"component": "U1", "pin": "2"},
    {"component": "U2", "pin": "2"},
    {"component": "C1", "pin": "2"},
    {"component": "C2", "pin": "2"}
  ],
  "net_type": "ground"
}
```

### Signal Nets
```json
{
  "id": "CLK",
  "connections": [
    {"component": "U1", "pin": "3"},
    {"component": "U2", "pin": "5"}
  ],
  "net_type": "signal"
}
```

## ⚠️ Common Mistakes

1. **Missing pin numbers**: Always include pin numbers in connections
2. **Inconsistent naming**: Use consistent naming conventions for components and nets
3. **Orphaned components**: Make sure all components are connected to nets
4. **Duplicate IDs**: Ensure all component and net IDs are unique
5. **Empty connections**: Nets must have at least one connection

## 🎯 Best Practices

1. **Use descriptive IDs**: "U1", "R5", "C10" are better than generic names
2. **Include pin names**: Add names for important pins (VCC, GND, CLK)
3. **Group related nets**: Use consistent naming for power, ground, and signal nets
4. **Add metadata**: Include designer, version, and description information
5. **Validate early**: Check your netlist against validation rules before submitting
