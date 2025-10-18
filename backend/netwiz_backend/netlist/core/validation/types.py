from datetime import datetime, timezone

from pydantic import BaseModel, Field, conlist, constr

from netwiz_backend.json_tracker.types import LocationInfo


class ValidationErrorType(BaseModel):
    """
    Represents a validation error type with name and description.

    This class defines validation error types that can occur during netlist validation.
    Each error type includes both a unique identifier and a human-readable description.
    """

    model_config = {"frozen": True}  # Make the model immutable and hashable

    name: str = Field(..., description="Unique identifier for the error type")
    description: str = Field(
        ..., description="Human-readable description of what this rule checks"
    )

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, ValidationErrorType):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)


# Define all validation error types
INVALID_JSON = ValidationErrorType(
    name="invalid_json", description="JSON syntax is invalid or malformed"
)
MISSING_FIELD = ValidationErrorType(
    name="missing_field", description="Required field is missing from the netlist"
)
INVALID_FORMAT = ValidationErrorType(
    name="invalid_format", description="Netlist format is invalid or unexpected"
)
BLANK_COMPONENT_NAME = ValidationErrorType(
    name="blank_component_name", description="Component names cannot be blank or empty"
)
BLANK_NET_NAME = ValidationErrorType(
    name="blank_net_name", description="Net names cannot be blank or empty"
)
DUPLICATE_COMPONENT_NAME = ValidationErrorType(
    name="duplicate_component_name",
    description="Component names must be unique within the netlist",
)
DUPLICATE_NAME = ValidationErrorType(
    name="duplicate_name", description="Names must be unique across components and nets"
)
DUPLICATE_NET_NAME = ValidationErrorType(
    name="duplicate_net_name", description="Net names must be unique within the netlist"
)
MISSING_GROUND = ValidationErrorType(
    name="missing_ground", description="No ground nets found in the netlist"
)
INSUFFICIENT_GND_CONNECTIONS = ValidationErrorType(
    name="insufficient_gnd_connections",
    description="Ground nets should have multiple connections",
)
GROUND_PIN_NOT_CONNECTED_TO_GROUND = ValidationErrorType(
    name="ground_pin_not_connected_to_ground",
    description="Pins marked as ground type should be connected to ground nets",
)
POWER_PIN_NOT_CONNECTED_TO_POWER = ValidationErrorType(
    name="power_pin_not_connected_to_power",
    description="Pins marked as power type should be connected to power nets",
)
CLOCK_NET_SINGLE_CONNECTION = ValidationErrorType(
    name="clock_net_single_connection",
    description="Clock nets typically should have multiple connections",
)
NET_TYPE_NAME_MISMATCH = ValidationErrorType(
    name="net_type_name_mismatch",
    description="Net type doesn't match net name convention",
)
MISNAMED_NETS = ValidationErrorType(
    name="misnamed_nets",
    description="Nets may be misnamed based on their connectivity patterns",
)
ORPHANED_NET = ValidationErrorType(
    name="orphaned_net", description="Nets must have at least one connection"
)
UNCONNECTED_COMPONENT = ValidationErrorType(
    name="unconnected_component", description="Components should be connected to nets"
)


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
    validation_rules_applied: list[ValidationErrorType] = Field(
        default_factory=list,
        description="List of validation rules that were applied",
    )
