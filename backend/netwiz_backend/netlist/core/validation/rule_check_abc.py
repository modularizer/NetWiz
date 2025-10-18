"""
Abstract base class for validation rule checks.

This module defines the RuleCheckABC abstract base class that provides
a consistent interface for all validation rule checks. Each validation
rule implements this interface, making the system highly modular and
extensible.

Key Features:
- **Consistent Interface**: All rule checks follow the same signature
- **Type Safety**: Abstract base class ensures proper implementation
- **Extensibility**: Easy to add new validation rules
- **Composability**: Rules can be easily combined and configured
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from datetime import datetime, timezone

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.types import (
    ValidationError,
    ValidationErrorType,
    ValidationResult,
)


class RuleCheckABC(ABC):
    """
    Abstract base class for validation rule checks.

    All validation rules must implement this interface to ensure consistency
    and type safety across the validation system.

    Attributes:
        error_type: The ValidationErrorType associated with this rule
        description: Human-readable description of what this rule checks
    """

    def __init__(self, error_types: Iterable[ValidationErrorType], description: str):
        """
        Initialize the rule check.

        Args:
            error_type: The ValidationErrorType for this rule
            description: Human-readable description of the rule
        """
        self.error_types = error_types
        self.description = description

    def check(
        self,
        netlist: Netlist,
        applied_rules: list[ValidationErrorType] | None = None,
        errors: list[ValidationError] | None = None,
        warnings: list[ValidationError] | None = None,
        get_location: Callable[[str], LocationInfo | None] | None = None,
    ) -> ValidationResult:
        """
        Perform the validation check.

        This method can be called in two ways:
        1. With all parameters (legacy mode): Mutates the provided lists and returns a ValidationResult
        2. With only netlist: Returns a complete ValidationResult with errors/warnings

        Args:
            netlist: The netlist to validate
            applied_rules: Optional list to append this rule's error_type to (for legacy compatibility)
            errors: Optional list to append error ValidationError objects to (for legacy compatibility)
            warnings: Optional list to append warning ValidationError objects to (for legacy compatibility)
            get_location: Optional function to get location info for error positioning

        Returns:
            ValidationResult: Complete validation result for this rule
        """
        applied_rules = applied_rules or []
        errors = errors or []
        warnings = warnings or []
        get_location = get_location or (lambda x: None)

        # mark the rule as applied
        applied_rules.extend([t for t in self.error_types if applied_rules not in t])

        # we are taking advantage of the mutability of the lists
        self._check(netlist, errors, warnings, get_location)

        return ValidationResult(
            is_valid=len(applied_rules) == 0,
            errors=errors,
            warnings=warnings,
            validation_timestamp=datetime.now(timezone.utc),
            applied_rules=applied_rules,
        )

    @abstractmethod
    def _check(
        self,
        netlist: Netlist,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        pass

    def __str__(self) -> str:
        """Return string representation of the rule."""
        error_types_str = ", ".join([et.value for et in self.error_types])
        return f"{self.__class__.__name__}({error_types_str}): {self.description}"

    def __repr__(self) -> str:
        """Return detailed string representation of the rule."""
        error_types_str = ", ".join([et.value for et in self.error_types])
        return f"{self.__class__.__name__}(error_types=({error_types_str}), description='{self.description}')"
