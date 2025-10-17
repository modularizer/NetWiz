from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """Represents a validation error"""

    error_type: str = Field(..., description="Type of validation error")
    message: str = Field(..., description="Human-readable error message")
    component_id: str | None = Field(
        default=None, description="Component ID if error is component-specific"
    )
    net_id: str | None = Field(
        default=None, description="Net ID if error is net-specific"
    )
    severity: str = Field(default="error", description="Error severity level")


class ValidationResult(BaseModel):
    """Result of netlist validation"""

    is_valid: bool = Field(..., description="Whether the netlist passed validation")
    errors: list[ValidationError] = Field(
        default_factory=list, description="List of validation errors"
    )
    warnings: list[ValidationError] = Field(
        default_factory=list, description="List of validation warnings"
    )
    validation_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When validation was performed",
    )
    validation_rules_applied: list[str] = Field(
        default_factory=list, description="List of validation rules that were applied"
    )


def validate_netlist_internal(netlist) -> ValidationResult:
    """
    Internal validation function

    Performs comprehensive validation of a netlist according to business rules.
    This function is used by both the upload and validate endpoints.
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
