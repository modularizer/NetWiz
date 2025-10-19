"""
Misnamed Nets validation rule.

This rule checks for nets that might be misnamed based on their connectivity patterns.
"""

from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    MISNAMED_NETS,
    ValidationError,
)


class MisnamedNetsRule(RuleCheckABC):
    """Rule to check for potentially misnamed nets."""

    def __init__(self):
        super().__init__(
            error_types=(MISNAMED_NETS,),
            description="Nets may be misnamed",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check that net types are consistent with their names."""
        # Define name patterns for each net type
        type_patterns = {
            "power": {"VCC", "VDD", "VIN", "VOUT", "POWER", "SUPPLY"},
            "ground": {"GND", "GROUND", "VSS", "AGND", "DGND", "PGND"},
            "clock": {"CLK", "CLOCK", "SCLK", "MCLK", "BCLK"},
            "signal": {"DATA", "ADDR", "CTRL", "EN", "RESET", "SIGNAL"},
        }
        name_to_type = {t: k for t, names in type_patterns.items() for k in names}
        for i, net in enumerate(netlist.nets):
            net_type = net.net_type
            net_name = net.name.upper()

            if net_name in name_to_type and net_type != name_to_type[net_name]:
                warnings.append(
                    ValidationError(
                        error_type=MISNAMED_NETS,
                        message=f"Net '{net.name}' has type '{net_type}', are you sure?",
                        net_id=net.name,
                        severity="warning",
                        location=get_location(f"$.nets.{i}.name"),
                    )
                )
