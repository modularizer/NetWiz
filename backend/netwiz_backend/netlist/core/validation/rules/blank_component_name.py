"""
Blank Component Name validation rule.

This rule checks that all component names are not blank or empty.
"""

from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    BLANK_COMPONENT_NAME,
    ValidationError,
)


class BlankComponentNameRule(RuleCheckABC):
    """Rule to check for blank or empty component names."""

    def __init__(self):
        super().__init__(
            error_types=(BLANK_COMPONENT_NAME,),
            description="Component names cannot be blank or empty",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for blank or empty component names."""
        for i, component in enumerate(netlist.components):
            if not component.name or not component.name.strip():
                error = ValidationError(
                    error_type=BLANK_COMPONENT_NAME,
                    message=f"Component names cannot be blank (Component #{i})",
                    component_id=component.name,
                    severity="error",
                    location=get_location(f"$.components.{i}.name")
                    if get_location
                    else None,
                )
                errors.append(error)
