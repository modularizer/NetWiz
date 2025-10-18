"""
Unique Component Name validation rule.

This rule checks that all component names are unique within the netlist.
"""
from collections import Counter
from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    ValidationError,
    ValidationErrorType,
)


class UniqueComponentNameRule(RuleCheckABC):
    """Rule to check for duplicate component names."""

    def __init__(self):
        super().__init__(
            error_types=(ValidationErrorType.DUPLICATE_COMPONENT_NAME,),
            description="Component names must be unique within the netlist",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for duplicate component names."""
        component_names = [comp.name for comp in netlist.components]
        dup_component_names = [
            name for name, count in Counter(component_names).items() if count > 1
        ]

        for name in dup_component_names:
            # Find the first occurrence of this component name for location
            component_location = None
            for i, component in enumerate(netlist.components):
                if component.name == name:
                    component_location = get_location(f"$.components.{i}.name")
                    break

            error = ValidationError(
                error_type=ValidationErrorType.DUPLICATE_COMPONENT_NAME,
                message=f"Component names must be unique ('{name}')",
                component_id=name,
                severity="error",
                location=component_location,
            )
            errors.append(error)
