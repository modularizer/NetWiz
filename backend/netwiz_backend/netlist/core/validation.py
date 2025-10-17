"""
Core validation logic for PCB netlists.

This module provides comprehensive validation capabilities for netlist data,
ensuring circuit integrity and adherence to electrical design rules. The
validation system is designed to catch common design errors and provide
actionable feedback to designers.

Key Features:
- **Rule-based validation**: Configurable validation rules for different design requirements
- **Comprehensive checks**: Covers connectivity, naming, and electrical constraints
- **Detailed reporting**: Provides specific error locations and suggestions
- **Extensible**: Easy to add new validation rules for specific applications

Validation Rules:
1. **Naming Rules**: Component and net IDs must be non-empty and unique
2. **Connectivity Rules**: All nets must have connections, components should be connected
3. **Electrical Rules**: Power/ground nets should have proper connectivity
4. **Design Rules**: Custom rules for specific design requirements

Example:
    ```python
    from netwiz_backend.netlist.core.validation import validate_netlist_internal
    from netwiz_backend.netlist.core.models import Netlist, Component, Net

    # Validate a netlist
    result = validate_netlist_internal(my_netlist)

    if result.is_valid:
        print("✅ Netlist is valid!")
    else:
        print("❌ Validation errors found:")
        for error in result.errors:
            print(f"  - {error.message}")
    ```
"""
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, conlist, constr

if TYPE_CHECKING:
    from .json_parser import LocationInfo


class ValidationErrorType(str, Enum):
    """
    Enumeration of validation error types.

    This enum defines all possible validation error types that can occur
    during netlist validation. Each error type represents a specific
    validation rule that was violated.

    Attributes:
        BLANK_COMPONENT_NAME: Component name is empty or whitespace-only
        BLANK_NET_NAME: Net name is empty or whitespace-only
        DUPLICATE_COMPONENT_NAME: Multiple components have the same name
        DUPLICATE_NET_NAME: Multiple nets have the same name
        MISSING_GROUND: No ground nets found in the netlist
        INSUFFICIENT_GND_CONNECTIONS: Ground net has fewer than 2 connections
        GROUND_PIN_NOT_CONNECTED_TO_GROUND: Pin marked as ground type is not connected to a ground net
        POWER_PIN_NOT_CONNECTED_TO_POWER: Pin marked as power type is not connected to a power net
        CLOCK_NET_SINGLE_CONNECTION: Clock net has only one connection (should typically have multiple)
        NET_TYPE_NAME_MISMATCH: Net type doesn't match net name convention
        MISNAMED_GROUND_NET: Net named like ground but typed as something else
        MISNAMED_POWER_NET: Net named like power but typed as something else
        MISNAMED_CLOCK_NET: Net named like clock but typed as something else
        ORPHANED_NET: Net has no connections
        UNCONNECTED_COMPONENT: Component is not connected to any net
    """

    BLANK_COMPONENT_NAME = "blank_component_name"
    BLANK_NET_NAME = "blank_net_name"
    DUPLICATE_COMPONENT_NAME = "duplicate_component_name"
    DUPLICATE_NET_NAME = "duplicate_net_name"
    MISSING_GROUND = "missing_ground"
    INSUFFICIENT_GND_CONNECTIONS = "insufficient_gnd_connections"
    GROUND_PIN_NOT_CONNECTED_TO_GROUND = "ground_pin_not_connected_to_ground"
    POWER_PIN_NOT_CONNECTED_TO_POWER = "power_pin_not_connected_to_power"
    CLOCK_NET_SINGLE_CONNECTION = "clock_net_single_connection"
    NET_TYPE_NAME_MISMATCH = "net_type_name_mismatch"
    MISNAMED_GROUND_NET = "misnamed_ground_net"
    MISNAMED_POWER_NET = "misnamed_power_net"
    MISNAMED_CLOCK_NET = "misnamed_clock_net"
    ORPHANED_NET = "orphaned_net"
    UNCONNECTED_COMPONENT = "unconnected_component"


class ValidationError(BaseModel):
    """
    Represents a validation error or warning.

    ValidationError captures detailed information about issues found during
    netlist validation. Each error includes the type, message, location,
    and severity level to help designers understand and fix problems.

    Attributes:
        error_type: Category of validation error (e.g., "blank_component_name")
        message: Human-readable description of the problem
        component_id: Optional component ID if error is component-specific
        net_id: Optional net ID if error is net-specific
        severity: Error severity level ("error" or "warning")

    Example:
        ```python
        error = ValidationError(
            error_type="duplicate_component_id",
            message="Component IDs must be unique",
            component_id="U1",
            severity="error"
        )
        ```
    """

    error_type: ValidationErrorType = Field(..., description="Type of validation error")
    message: constr(strip_whitespace=True) = Field(
        ..., description="Human-readable error message"
    )
    component_id: constr(strip_whitespace=True) | None = Field(
        default=None, description="Component ID if error is component-specific"
    )
    net_id: constr(strip_whitespace=True) | None = Field(
        default=None, description="Net ID if error is net-specific"
    )
    severity: constr(strip_whitespace=True) = Field(
        default="error", description="Error severity level"
    )
    line_number: int | None = Field(
        default=None, description="Line number in the original JSON file"
    )
    character_position: int | None = Field(
        default=None, description="Character position in the line"
    )


class ValidationResult(BaseModel):
    """
    Result of netlist validation containing errors, warnings, and metadata.

    ValidationResult provides a comprehensive summary of the validation process,
    including all issues found, the validation timestamp, and which rules were
    applied. This allows for detailed reporting and audit trails.

    Attributes:
        is_valid: True if no errors were found (warnings are allowed)
        errors: List of validation errors that must be fixed
        warnings: List of validation warnings that should be reviewed
        validation_timestamp: When the validation was performed
        validation_rules_applied: List of validation rules that were checked

    Example:
        ```python
        result = ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    error_type="duplicate_component_id",
                    message="Component IDs must be unique",
                    severity="error"
                )
            ],
            warnings=[
                ValidationError(
                    error_type="unconnected_component",
                    message="Component is not connected to any net",
                    component_id="R5",
                    severity="warning"
                )
            ],
            validation_rules_applied=["unique_component_ids", "connectivity_check"]
        )
        ```
    """

    is_valid: bool = Field(..., description="Whether the netlist passed validation")
    errors: conlist(ValidationError) = Field(
        default_factory=list, description="List of validation errors"
    )
    warnings: conlist(ValidationError) = Field(
        default_factory=list, description="List of validation warnings"
    )
    validation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When validation was performed",
    )
    validation_rules_applied: conlist(ValidationErrorType) = Field(
        default_factory=list, description="List of validation rules that were applied"
    )
    auto_fill_suggestions: list[dict[str, str]] = Field(
        default_factory=list,
        description="Suggestions for auto-filling missing net types based on names",
    )


def validate_netlist_internal(
    netlist, locations: dict[str, "LocationInfo"] | None = None
) -> ValidationResult:
    """
    Perform comprehensive validation of a netlist according to design rules.

    This function implements the core validation logic for netlist data,
    checking for common design errors and electrical constraints. It applies
    a comprehensive set of validation rules and returns detailed results.

    Validation Rules Applied:
    1. **Blank Names**: Component and net IDs cannot be empty or whitespace-only
    2. **Unique IDs**: All component IDs must be unique within the netlist
    3. **Unique Nets**: All net IDs must be unique within the netlist
    4. **GND Connectivity**: Ground nets should have multiple connections
    5. **Orphaned Nets**: All nets must have at least one connection
    6. **Unconnected Components**: Components should be connected to nets

    Args:
        netlist: The Netlist object to validate

    Returns:
        ValidationResult: Comprehensive validation results including errors,
                         warnings, and metadata about the validation process

    Example:
        ```python
        from netwiz_backend.netlist.core.models import Netlist
        from netwiz_backend.netlist.core.validation import validate_netlist_internal

        # Validate a netlist
        result = validate_netlist_internal(my_netlist)

        if not result.is_valid:
            print(f"Found {len(result.errors)} errors:")
            for error in result.errors:
                print(f"  - {error.message}")

        if result.warnings:
            print(f"Found {len(result.warnings)} warnings:")
            for warning in result.warnings:
                print(f"  - {warning.message}")
        ```
    """
    errors = []
    warnings = []
    applied_rules = []

    # Rule 1: Check for blank component names
    applied_rules.append(ValidationErrorType.BLANK_COMPONENT_NAME)
    for i, component in enumerate(netlist.components):
        if not component.name or not component.name.strip():
            # Get location information if available
            location = None
            if locations:
                location = locations.get(f"components.{i}.name")

            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.BLANK_COMPONENT_NAME,
                    message=f"Component names cannot be blank (Component #{i})",
                    component_id=component.name,
                    severity="error",
                    line_number=location.line_number if location else None,
                    character_position=location.character_position
                    if location
                    else None,
                )
            )

    # Rule 2: Check for blank net names
    applied_rules.append(ValidationErrorType.BLANK_NET_NAME)
    for i, net in enumerate(netlist.nets):
        if not net.name or not net.name.strip():
            # Get location information if available
            location = None
            if locations:
                location = locations.get(f"nets.{i}.name")

            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.BLANK_NET_NAME,
                    message=f"Net names cannot be blank (Net #{i})",
                    net_id=net.name,
                    severity="error",
                    line_number=location.line_number if location else None,
                    character_position=location.character_position
                    if location
                    else None,
                )
            )

    # Rule 3: Check for unique component names
    applied_rules.append(ValidationErrorType.DUPLICATE_COMPONENT_NAME)
    component_names = [comp.name for comp in netlist.components]
    dup_component_names = [
        name for name, count in Counter(component_names).items() if count > 1
    ]
    for name in dup_component_names:
        # Find the first occurrence of this component name for location
        component_location = None
        if locations:
            for i, component in enumerate(netlist.components):
                if component.name == name:
                    component_location = locations.get(f"components.{i}.name")
                    break

        errors.append(
            ValidationError(
                error_type=ValidationErrorType.DUPLICATE_COMPONENT_NAME,
                message=f"Component names must be unique ('{name}')",
                component_id=name,
                severity="error",
                line_number=component_location.line_number
                if component_location
                else None,
                character_position=component_location.character_position
                if component_location
                else None,
            )
        )

    # Rule 4: Check for unique net IDs
    applied_rules.append(ValidationErrorType.DUPLICATE_NET_NAME)
    net_names = [net.name for net in netlist.nets]
    dup_net_names = [name for name, count in Counter(net_names).items() if count > 1]
    for name in dup_net_names:
        # Find the first occurrence of this net name for location
        net_location = None
        if locations:
            for i, net in enumerate(netlist.nets):
                if net.name == name:
                    net_location = locations.get(f"nets.{i}.name")
                    break

        errors.append(
            ValidationError(
                error_type=ValidationErrorType.DUPLICATE_NET_NAME,
                message=f"Net names must be unique ('{name}')",
                net_id=name,
                severity="error",
                line_number=net_location.line_number if net_location else None,
                character_position=net_location.character_position
                if net_location
                else None,
            )
        )

    # Add warnings if any components have the same names as nets
    # (This uses DUPLICATE_NET_NAME as the error type)
    all_names = net_names + component_names
    dup_names = [name for name, count in Counter(all_names).items() if count > 1]
    for name in dup_names:
        warnings.append(
            ValidationError(
                error_type=ValidationErrorType.DUPLICATE_NET_NAME,
                message=f"Component and Net share a name ('{name}')",
                severity="warning",
            )
        )

    # Rule 5: Check GND connectivity using net_type
    applied_rules.append(ValidationErrorType.MISSING_GROUND)
    applied_rules.append(ValidationErrorType.INSUFFICIENT_GND_CONNECTIONS)

    # Find ground nets by net_type first, then fall back to name-based detection
    gnd_nets_by_type = [n for n in netlist.nets if n.net_type == "ground"]
    ground_names = {"GND", "GROUND", "VSS", "AGND", "DGND", "PGND"}
    gnd_nets_by_name = [n for n in netlist.nets if n.name.upper() in ground_names]

    # Combine both methods, prioritizing net_type (use names to avoid hash issues)
    gnd_net_names = set()
    for net in gnd_nets_by_type:
        gnd_net_names.add(net.name)
    for net in gnd_nets_by_name:
        gnd_net_names.add(net.name)

    all_gnd_nets = [n for n in netlist.nets if n.name in gnd_net_names]

    if not all_gnd_nets:
        errors.append(
            ValidationError(
                error_type=ValidationErrorType.MISSING_GROUND,
                message="No ground nets found",
                severity="error",
            )
        )

    for net in all_gnd_nets:
        if len(net.connections) < 2:
            warnings.append(
                ValidationError(
                    error_type=ValidationErrorType.INSUFFICIENT_GND_CONNECTIONS,
                    message=f"Ground net '{net.name}' has only {len(net.connections)} connection(s)",
                    net_id=net.name,
                    severity="warning",
                )
            )

    # Rule 5.5: Check that ground pins are connected to ground nets
    applied_rules.append(ValidationErrorType.GROUND_PIN_NOT_CONNECTED_TO_GROUND)

    # Find all ground pins
    ground_pins = []
    for component in netlist.components:
        for pin in component.pins:
            if pin.type == "ground":
                ground_pins.append((component.name, pin.number))

    # Check if each ground pin is connected to a ground net (using enhanced detection)
    for component_name, pin_number in ground_pins:
        connected_to_ground = False
        for net in all_gnd_nets:  # Use the enhanced ground net list
            for connection in net.connections:
                if (
                    connection.component == component_name
                    and connection.pin == pin_number
                ):
                    connected_to_ground = True
                    break
            if connected_to_ground:
                break

        if not connected_to_ground:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.GROUND_PIN_NOT_CONNECTED_TO_GROUND,
                    message=f"Ground pin {component_name}.{pin_number} is not connected to a ground net",
                    component_id=component_name,
                    severity="error",
                )
            )

    # Rule 5.6: Check that power pins are connected to power nets
    applied_rules.append(ValidationErrorType.POWER_PIN_NOT_CONNECTED_TO_POWER)

    # Find power nets by net_type first, then fall back to name-based detection
    power_nets_by_type = [n for n in netlist.nets if n.net_type == "power"]
    power_names = {"VCC", "VDD", "VIN", "VOUT", "+3V3", "+5V", "+12V"}
    power_nets_by_name = [n for n in netlist.nets if n.name.upper() in power_names]

    # Combine both methods (use names to avoid hash issues)
    power_net_names = set()
    for net in power_nets_by_type:
        power_net_names.add(net.name)
    for net in power_nets_by_name:
        power_net_names.add(net.name)

    all_power_nets = [n for n in netlist.nets if n.name in power_net_names]

    # Find all power pins
    power_pins = []
    for component in netlist.components:
        for pin in component.pins:
            if pin.type == "power":
                power_pins.append((component.name, pin.number))

    # Check if each power pin is connected to a power net
    for component_name, pin_number in power_pins:
        connected_to_power = False
        for net in all_power_nets:
            for connection in net.connections:
                if (
                    connection.component == component_name
                    and connection.pin == pin_number
                ):
                    connected_to_power = True
                    break
            if connected_to_power:
                break

        if not connected_to_power:
            warnings.append(
                ValidationError(
                    error_type=ValidationErrorType.POWER_PIN_NOT_CONNECTED_TO_POWER,
                    message=f"Power pin {component_name}.{pin_number} is not connected to a power net",
                    component_id=component_name,
                    severity="warning",
                )
            )

    # Rule 5.7: Check clock nets for proper connectivity
    applied_rules.append(ValidationErrorType.CLOCK_NET_SINGLE_CONNECTION)
    clock_nets = [n for n in netlist.nets if n.net_type == "clock"]

    for net in clock_nets:
        if len(net.connections) == 1:
            warnings.append(
                ValidationError(
                    error_type=ValidationErrorType.CLOCK_NET_SINGLE_CONNECTION,
                    message=f"Clock net '{net.name}' has only one connection - consider if this is intentional",
                    net_id=net.name,
                    severity="warning",
                )
            )

    # Rule 5.8: Check for net type and name consistency
    applied_rules.append(ValidationErrorType.NET_TYPE_NAME_MISMATCH)

    for net in netlist.nets:
        if net.net_type and net.name:
            net_name_upper = net.name.upper()

            # Check for mismatches
            if net.net_type == "ground" and net_name_upper not in {
                "GND",
                "GROUND",
                "VSS",
                "AGND",
                "DGND",
                "PGND",
            }:
                warnings.append(
                    ValidationError(
                        error_type=ValidationErrorType.NET_TYPE_NAME_MISMATCH,
                        message=f"Net '{net.name}' is typed as 'ground' but name doesn't follow ground naming convention",
                        net_id=net.name,
                        severity="warning",
                    )
                )
            elif net.net_type == "power" and not any(
                power_name in net_name_upper
                for power_name in {"VCC", "VDD", "VIN", "VOUT", "+3V3", "+5V", "+12V"}
            ):
                warnings.append(
                    ValidationError(
                        error_type=ValidationErrorType.NET_TYPE_NAME_MISMATCH,
                        message=f"Net '{net.name}' is typed as 'power' but name doesn't follow power naming convention",
                        net_id=net.name,
                        severity="warning",
                    )
                )

    # Rule 5.9: Check for misnamed nets (name suggests one type but net_type is different)
    applied_rules.append(ValidationErrorType.MISNAMED_GROUND_NET)
    applied_rules.append(ValidationErrorType.MISNAMED_POWER_NET)
    applied_rules.append(ValidationErrorType.MISNAMED_CLOCK_NET)

    for net in netlist.nets:
        if net.net_type and net.name:
            net_name_upper = net.name.upper()

            # Check for ground naming but wrong type
            if (
                net_name_upper in {"GND", "GROUND", "VSS", "AGND", "DGND", "PGND"}
                and net.net_type != "ground"
            ):
                warnings.append(
                    ValidationError(
                        error_type=ValidationErrorType.MISNAMED_GROUND_NET,
                        message=f"Net '{net.name}' is named like a ground net but typed as '{net.net_type}' - consider changing type to 'ground'",
                        net_id=net.name,
                        severity="warning",
                    )
                )

            # Check for power naming but wrong type
            elif (
                any(
                    power_name in net_name_upper
                    for power_name in {
                        "VCC",
                        "VDD",
                        "VIN",
                        "VOUT",
                        "+3V3",
                        "+5V",
                        "+12V",
                    }
                )
                and net.net_type != "power"
            ):
                warnings.append(
                    ValidationError(
                        error_type=ValidationErrorType.MISNAMED_POWER_NET,
                        message=f"Net '{net.name}' is named like a power net but typed as '{net.net_type}' - consider changing type to 'power'",
                        net_id=net.name,
                        severity="warning",
                    )
                )

            # Check for clock naming but wrong type
            elif (
                any(
                    clock_name in net_name_upper
                    for clock_name in {"CLK", "CLOCK", "SCK", "SCLK", "MCLK", "BCLK"}
                )
                and net.net_type != "clock"
            ):
                warnings.append(
                    ValidationError(
                        error_type=ValidationErrorType.MISNAMED_CLOCK_NET,
                        message=f"Net '{net.name}' is named like a clock net but typed as '{net.net_type}' - consider changing type to 'clock'",
                        net_id=net.name,
                        severity="warning",
                    )
                )

    # Rule 5.10: Auto-suggest net_type for nets with recognizable names but empty type
    # This is informational - we'll add suggestions to the validation result
    auto_fill_suggestions = []
    for net in netlist.nets:
        if not net.net_type and net.name:
            net_name_upper = net.name.upper()
            suggested_type = None

            # Check for ground naming
            if net_name_upper in {"GND", "GROUND", "VSS", "AGND", "DGND", "PGND"}:
                suggested_type = "ground"
            # Check for power naming
            elif any(
                power_name in net_name_upper
                for power_name in {"VCC", "VDD", "VIN", "VOUT", "+3V3", "+5V", "+12V"}
            ):
                suggested_type = "power"
            # Check for clock naming
            elif any(
                clock_name in net_name_upper
                for clock_name in {"CLK", "CLOCK", "SCK", "SCLK", "MCLK", "BCLK"}
            ):
                suggested_type = "clock"
            # Check for data naming
            elif any(
                data_name in net_name_upper
                for data_name in {
                    "DATA",
                    "D0",
                    "D1",
                    "D2",
                    "D3",
                    "D4",
                    "D5",
                    "D6",
                    "D7",
                    "MOSI",
                    "MISO",
                    "SDA",
                }
            ):
                suggested_type = "data"
            # Check for control naming
            elif any(
                control_name in net_name_upper
                for control_name in {
                    "CS",
                    "CE",
                    "EN",
                    "ENABLE",
                    "RESET",
                    "RST",
                    "INT",
                    "IRQ",
                }
            ):
                suggested_type = "control"

            if suggested_type:
                auto_fill_suggestions.append(
                    {
                        "net_name": net.name,
                        "suggested_type": suggested_type,
                        "reason": f"Name '{net.name}' follows {suggested_type} naming convention",
                    }
                )

    # Rule 6: Check for orphaned nets (nets with no connections)
    applied_rules.append(ValidationErrorType.ORPHANED_NET)
    for net in netlist.nets:
        if not net.connections:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.ORPHANED_NET,
                    message="Net must have at least one connection",
                    net_id=net.name,
                    severity="error",
                )
            )

    # Rule 7: Check for components with no connections
    applied_rules.append(ValidationErrorType.UNCONNECTED_COMPONENT)
    connected_components = set()
    for net in netlist.nets:
        for connection in net.connections:
            connected_components.add(connection.component)

    for component in netlist.components:
        if component.name not in connected_components:
            warnings.append(
                ValidationError(
                    error_type=ValidationErrorType.UNCONNECTED_COMPONENT,
                    message="Component is not connected to any net",
                    component_id=component.name,
                    severity="warning",
                )
            )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        validation_timestamp=datetime.utcnow(),
        validation_rules_applied=applied_rules,
        auto_fill_suggestions=auto_fill_suggestions,
    )
