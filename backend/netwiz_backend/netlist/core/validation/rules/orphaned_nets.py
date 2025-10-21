"""
Orphaned Nets validation rule.

This rule checks for nets that are not connected to any components.
"""

from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    ORPHANED_NET,
    NetlistValidationError,
)


class OrphanedNetsRule(RuleCheckABC):
    """Rule to check for orphaned nets (not connected to any components)."""

    def __init__(self):
        super().__init__(
            error_types=(ORPHANED_NET,),
            description="Nets should be connected to at least one component",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[NetlistValidationError],
        warnings: list[NetlistValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for orphaned nets."""
        for i, net in enumerate(netlist.nets):
            if len(net.connections) == 0:
                errors.append(
                    NetlistValidationError(
                        error_type=ORPHANED_NET,
                        message=f"Net '{net.name}' is not connected to any components",
                        net_id=net.name,
                        severity="error",
                        location=get_location(f"$.nets.{i}.connections"),
                    )
                )
