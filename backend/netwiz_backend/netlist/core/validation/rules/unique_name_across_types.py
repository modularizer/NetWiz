"""
Unique Name Across Types validation rule.

This rule checks that component names and net names don't conflict with each other.
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


class UniqueNameAcrossTypesRule(RuleCheckABC):
    """Rule to check for names shared between components and nets."""

    def __init__(self):
        super().__init__(
            error_types=(ValidationErrorType.DUPLICATE_NAME,),
            description="Component and net names should not conflict",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for names shared between components and nets."""
        component_names = [comp.name for comp in netlist.components]
        net_names = [net.name for net in netlist.nets]
        all_names = net_names + component_names
        dup_names = [name for name, count in Counter(all_names).items() if count > 1]

        for name in dup_names:
            net_location = None
            for i, net in enumerate(netlist.nets):
                if net.name == name:
                    net_location = get_location(f"$.nets.{i}.name")
                    break

            warning = ValidationError(
                error_type=ValidationErrorType.DUPLICATE_NAME,
                message=f"Component and Net share a name ('{name}')",
                severity="warning",
                location=net_location,
            )
            warnings.append(warning)
