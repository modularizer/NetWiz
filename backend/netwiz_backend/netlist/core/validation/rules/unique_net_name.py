"""
Unique Net Name validation rule.

This rule checks that all net names are unique within the netlist.
"""

from collections import Counter
from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    DUPLICATE_NET_NAME,
    NetlistValidationError,
)


class UniqueNetNameRule(RuleCheckABC):
    """Rule to check for duplicate net names."""

    def __init__(self):
        super().__init__(
            error_types=(DUPLICATE_NET_NAME,),
            description="Net names must be unique within the netlist",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[NetlistValidationError],
        warnings: list[NetlistValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for duplicate net names."""
        net_names = [net.name for net in netlist.nets]
        dup_net_names = [
            name for name, count in Counter(net_names).items() if count > 1
        ]

        for name in dup_net_names:
            # Find the first occurrence of this net name for location
            net_location = None
            for i, net in enumerate(netlist.nets):
                if net.name == name:
                    net_location = get_location(f"$.nets.{i}.name")
                    break

            error = NetlistValidationError(
                error_type=DUPLICATE_NET_NAME,
                message=f"Net names must be unique ('{name}')",
                net_id=name,
                severity="error",
                location=net_location,
            )
            errors.append(error)
