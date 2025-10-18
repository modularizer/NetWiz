from fastapi import HTTPException

from netwiz_backend.netlist.core.validation.types import (
    ValidationError,
    ValidationErrorType,
    ValidationResult,
)


class ValidationHTTPError(HTTPException):
    """
    HTTP exception specifically for validation errors.

    This class encapsulates the common pattern of creating ValidationResult
    objects and raising HTTP exceptions with validation error details.

    The validation_errors list is automatically separated into errors and warnings
    based on the severity field of each ValidationError.

    Args:
        validation_errors: List of ValidationError objects (auto-separated by severity)
        validation_rules_applied: Optional list of applied ValidationErrorType rules
        status_code: HTTP status code (default: 422)
    """

    def __init__(
        self,
        validation_errors: list[ValidationError],
        validation_rules_applied: list[ValidationErrorType] | None = None,
        status_code: int = 422,
    ):
        # Auto-separate validation_errors into errors and warnings based on severity
        errors = [ve for ve in validation_errors if ve.severity == "error"]
        warnings = [ve for ve in validation_errors if ve.severity == "warning"]

        error_result = ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_rules_applied=validation_rules_applied or [],
        )

        super().__init__(
            status_code=status_code,
            detail={"validation_result": error_result.model_dump(mode="json")},
        )
