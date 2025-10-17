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

from datetime import datetime, timezone

from pydantic import BaseModel, Field, conlist, constr


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

    error_type: constr(strip_whitespace=True) = Field(
        ..., description="Type of validation error"
    )
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
    validation_rules_applied: conlist(constr(strip_whitespace=True)) = Field(
        default_factory=list, description="List of validation rules that were applied"
    )


def validate_netlist_internal(netlist) -> ValidationResult:
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
    applied_rules.append("blank_component_names")
    for component in netlist.components:
        if not component.id or not component.id.strip():
            errors.append(
                ValidationError(
                    error_type="blank_component_name",
                    message="Component names cannot be blank",
                    component_id=component.id,
                    severity="error",
                )
            )

    # Rule 2: Check for blank net names
    applied_rules.append("blank_net_names")
    for net in netlist.nets:
        if not net.id or not net.id.strip():
            errors.append(
                ValidationError(
                    error_type="blank_net_name",
                    message="Net names cannot be blank",
                    net_id=net.id,
                    severity="error",
                )
            )

    # Rule 3: Check for unique component IDs
    applied_rules.append("unique_component_ids")
    component_ids = [comp.id for comp in netlist.components]
    if len(component_ids) != len(set(component_ids)):
        errors.append(
            ValidationError(
                error_type="duplicate_component_id",
                message="Component IDs must be unique",
                severity="error",
            )
        )

    # Rule 4: Check for unique net IDs
    applied_rules.append("unique_net_ids")
    net_ids = [net.id for net in netlist.nets]
    if len(net_ids) != len(set(net_ids)):
        errors.append(
            ValidationError(
                error_type="duplicate_net_id",
                message="Net IDs must be unique",
                severity="error",
            )
        )

    # Rule 5: Check GND connectivity
    applied_rules.append("gnd_connectivity")
    gnd_nets = [
        net for net in netlist.nets if net.id.upper() in ["GND", "GROUND", "VSS"]
    ]
    if gnd_nets:
        gnd_net = gnd_nets[0]
        if len(gnd_net.connections) < 2:
            warnings.append(
                ValidationError(
                    error_type="insufficient_gnd_connections",
                    message="GND net should be connected to multiple components",
                    net_id=gnd_net.id,
                    severity="warning",
                )
            )

    # Rule 6: Check for orphaned nets (nets with no connections)
    applied_rules.append("orphaned_nets")
    for net in netlist.nets:
        if not net.connections:
            errors.append(
                ValidationError(
                    error_type="orphaned_net",
                    message="Net must have at least one connection",
                    net_id=net.id,
                    severity="error",
                )
            )

    # Rule 7: Check for components with no connections
    applied_rules.append("unconnected_components")
    connected_components = set()
    for net in netlist.nets:
        for connection in net.connections:
            connected_components.add(connection.component)

    for component in netlist.components:
        if component.id not in connected_components:
            warnings.append(
                ValidationError(
                    error_type="unconnected_component",
                    message="Component is not connected to any net",
                    component_id=component.id,
                    severity="warning",
                )
            )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        validation_timestamp=datetime.utcnow(),
        validation_rules_applied=applied_rules,
    )
