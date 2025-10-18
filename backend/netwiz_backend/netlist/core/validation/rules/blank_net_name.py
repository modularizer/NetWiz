"""
Blank Net Name validation rule.

This rule checks that all net names are not blank or empty.
"""

from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    BLANK_NET_NAME,
    ValidationError,
)


class BlankNetNameRule(RuleCheckABC):
    """Rule to check for blank or empty net names."""

    def __init__(self):
        super().__init__(
            error_types=(BLANK_NET_NAME,),
            description="Net names cannot be blank or empty",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for blank or empty net names."""
        for i, net in enumerate(netlist.nets):
            if not net.name or not net.name.strip():
                error = ValidationError(
                    error_type=BLANK_NET_NAME,
                    message=f"Net names cannot be blank (Net #{i})",
                    net_id=net.name,
                    severity="error",
                    location=get_location(f"$.nets.{i}.name") if get_location else None,
                )
                errors.append(error)
