import pydantic_core

from netwiz_backend.json_tracker import TrackedJson, TrackedJSONDecodeError
from netwiz_backend.netlist.core.models import TrackedNetlist
from netwiz_backend.netlist.core.validation.types import (
    INVALID_FORMAT,
    INVALID_JSON,
    MISSING_FIELD,
    ValidationError,
    ValidationResult,
)

preapplied_rules = [
    INVALID_JSON,
    INVALID_FORMAT,
    MISSING_FIELD,
]


def validate_basic_format(
    json_text: str,
) -> tuple[TrackedNetlist | None, ValidationResult | None]:
    """Get ValidationRequest with custom pre-validation"""
    validation_rules_applied = []

    # step 1: check if valid json
    tracked_json, vr = check_is_valid_json(json_text, validation_rules_applied)
    if vr is not None:
        return None, vr

    # step 2: check basic structure
    tracked_netlist, vr = check_basic_format(tracked_json, validation_rules_applied)
    if vr is not None:
        return None, vr

    # Create ValidationRequest without validation
    return tracked_netlist, None


def check_is_valid_json(
    json_text: str, validation_rules_applied: list
) -> tuple[TrackedJson | None, ValidationResult | None]:
    """Get ValidationRequest with custom pre-validation"""
    # Step 1: Parse JSON using TrackedJson (primary and only JSON parser)
    try:
        validation_rules_applied.append(INVALID_JSON)
        tracked_json = TrackedJson.loads(json_text, raise_on_error=True)
    except TrackedJSONDecodeError as e:
        # JSON syntax error - TrackedJson provides detailed location info
        return None, ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    message=f"JSON syntax error: {e.msg}",
                    error_type=INVALID_JSON,
                    location=e.error_loc,
                )
            ],
            validation_rules_applied=validation_rules_applied,
        )
    except Exception as e:
        # Unexpected error during JSON parsing
        return None, ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    message=f"Unexpected error parsing JSON: {e!s}",
                    error_type=INVALID_JSON,
                    location=None,
                )
            ],
            validation_rules_applied=validation_rules_applied,
        )

    # Step 2: Check if data is a dict
    if not isinstance(tracked_json.data, dict):
        return None, ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    message="Request data must be an object",
                    error_type=INVALID_JSON,
                    location=None,
                )
            ],
            validation_rules_applied=validation_rules_applied,
        )
    return tracked_json, None


def check_basic_format(
    tracked_json: TrackedJson, validation_rules_applied: list
) -> tuple[TrackedNetlist | None, ValidationResult | None]:
    validation_rules_applied.append(INVALID_FORMAT)
    validation_rules_applied.append(MISSING_FIELD)
    missing_field_validation_errors = []
    for f in ["components", "nets"]:
        if f not in tracked_json:
            missing_field_validation_errors.append(
                ValidationError(
                    message=f"Missing required field: {f}",
                    error_type=MISSING_FIELD,
                    location=tracked_json.location,
                )
            )

    if missing_field_validation_errors:
        return None, ValidationResult(
            is_valid=False,
            errors=missing_field_validation_errors,
            validation_rules_applied=validation_rules_applied,
        )

    try:
        netlist = TrackedNetlist(**tracked_json.data, tracked_json=tracked_json)
    except pydantic_core.ValidationError as e:
        validation_errors = localize_pydantic_error(e, tracked_json)

        return None, ValidationResult(
            is_valid=False,
            errors=validation_errors,
            validation_rules_applied=validation_rules_applied,
        )
    return netlist, None


def localize_pydantic_error(
    e: pydantic_core.ValidationError, tracked_json: TrackedJson | None
) -> list[ValidationError]:
    validation_errors = []
    for pydantic_error in e.errors():
        msg = pydantic_error["msg"]
        path: list[str | int] = list(pydantic_error["loc"])

        # Convert Pydantic path to TrackedJson path format
        # Pydantic paths are like ['components', 0, 'name']
        # TrackedJson paths are like "$.components.0.name"
        location_info = None
        if tracked_json:
            try:
                # Try progressively removing the last part of the path
                for i in range(len(path), 0, -1):
                    partial_path = path[:i]
                    location_key = "$." + ".".join(str(p) for p in partial_path)

                    if location_key in tracked_json.locations:
                        loc = tracked_json.locations[location_key]
                        location_info = loc
                        break
            except Exception as e:
                print(f"Error finding location for path {path}: {e}")

        if not location_info:
            print(f"No location found for path {path}")

        validation_errors.append(
            ValidationError(
                message=msg,
                error_type=INVALID_FORMAT,
                location=location_info,
            )
        )
    return validation_errors
