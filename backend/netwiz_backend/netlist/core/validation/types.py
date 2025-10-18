from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, conlist, constr

from netwiz_backend.json_tracker.types import LocationInfo


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
        MISNAMED_NETS: Net name appears unintentional
        ORPHANED_NET: Net has no connections
        UNCONNECTED_COMPONENT: Component is not connected to any net
    """

    INVALID_JSON = "invalid_json"
    MISSING_FIELD = "missing_field"
    INVALID_FORMAT = "invalid_format"
    BLANK_COMPONENT_NAME = "blank_component_name"
    BLANK_NET_NAME = "blank_net_name"
    DUPLICATE_COMPONENT_NAME = "duplicate_component_name"
    DUPLICATE_NAME = "duplicate_name"
    DUPLICATE_NET_NAME = "duplicate_net_name"
    MISSING_GROUND = "missing_ground"
    INSUFFICIENT_GND_CONNECTIONS = "insufficient_gnd_connections"
    GROUND_PIN_NOT_CONNECTED_TO_GROUND = "ground_pin_not_connected_to_ground"
    POWER_PIN_NOT_CONNECTED_TO_POWER = "power_pin_not_connected_to_power"
    CLOCK_NET_SINGLE_CONNECTION = "clock_net_single_connection"
    NET_TYPE_NAME_MISMATCH = "net_type_name_mismatch"
    MISNAMED_NETS = "misnamed_nets"
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
        location: Optional LocationInfo object with detailed position information

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
    location: LocationInfo | None = Field(
        default=None,
        description="Location information for the error in the source JSON",
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
    applied_rules: list[ValidationErrorType] = Field(
        default_factory=list,
        description="List of validation rules that were applied",
    )
