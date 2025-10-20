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
    result = validate_netlist(my_netlist)

    if result.is_valid:
        print("✅ Netlist is valid!")
    else:
        print("❌ Validation errors found:")
        for error in result.errors:
            print(f"  - {error.message}")
    ```
"""
import json

from netwiz_backend.netlist.core.models import Netlist, TrackedNetlist
from netwiz_backend.netlist.core.validation.prevalidation import (
    preapplied_rules,
    validate_basic_format,
)
from netwiz_backend.netlist.core.validation.rules import (
    BlankComponentNameRule,
    BlankNetNameRule,
    GroundConnectivityRule,
    GroundPinConnectivityRule,
    MisnamedNetsRule,
    OrphanedNetsRule,
    UnconnectedComponentsRule,
    UniqueComponentNameRule,
    UniqueNameAcrossTypesRule,
    UniqueNetNameRule,
)
from netwiz_backend.netlist.core.validation.types import (
    INVALID_JSON,
    ValidationResult,
)


def validate_netlist(
    netlist: str | dict | Netlist | TrackedNetlist,
) -> tuple[dict | Netlist | TrackedNetlist | None, ValidationResult]:
    if isinstance(netlist, str):
        return _validate_netlist_text(netlist)
    elif isinstance(netlist, dict):
        try:
            s = json.dumps(netlist)
            return _validate_netlist_text(s)
        except json.JSONDecodeError:
            return netlist, ValidationResult(
                is_valid=False,
                errors=[INVALID_JSON],
                warnings=[],
                applied_rules=[INVALID_JSON],
            )
    return _validate_netlist(netlist)


def _validate_netlist_text(
    json_text: str
) -> tuple[dict | Netlist | TrackedNetlist | None, ValidationResult]:
    tracked_netlist, validation_result = validate_basic_format(json_text)
    if validation_result is not None:
        return tracked_netlist, validation_result
    if tracked_netlist is None:
        return tracked_netlist, ValidationResult(
            is_valid=False,
            errors=[],
            warnings=[],
            applied_rules=[],
        )

    return _validate_netlist(tracked_netlist)


def _validate_netlist(
    netlist: Netlist | TrackedNetlist,
) -> tuple[Netlist | TrackedNetlist | None, ValidationResult]:
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
    tracked_json = netlist.tracked_json if isinstance(netlist, TrackedNetlist) else None

    def get_location(key):
        if tracked_json and key in tracked_json:
            return tracked_json[key].location
        return None

    errors = []
    warnings = []
    validation_rules_applied = [*preapplied_rules]

    # Initialize all validation rules
    validation_rules = [
        BlankComponentNameRule(),
        BlankNetNameRule(),
        UniqueComponentNameRule(),
        UniqueNetNameRule(),
        UniqueNameAcrossTypesRule(),
        GroundConnectivityRule(),
        GroundPinConnectivityRule(),
        MisnamedNetsRule(),
        OrphanedNetsRule(),
        UnconnectedComponentsRule(),
    ]

    # Run all validation rules
    for rule in validation_rules:
        rule.check(netlist, validation_rules_applied, errors, warnings, get_location)

    return netlist, ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        validation_rules_applied=validation_rules_applied,
    )
