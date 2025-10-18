"""
Ground Connectivity validation rule.

This rule checks for ground nets and their connectivity requirements.
"""
from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    ValidationError,
    ValidationErrorType,
)


class GroundConnectivityRule(RuleCheckABC):
    """Rule to check for ground nets and their connectivity."""

    def __init__(self):
        super().__init__(
            error_types=(
                ValidationErrorType.MISSING_GROUND,
                ValidationErrorType.INSUFFICIENT_GND_CONNECTIONS,
            ),
            description="Ground nets should exist and have proper connectivity",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[ValidationError],
        warnings: list[ValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for ground nets and their connectivity."""
        # Find ground nets by net_type first, then fall back to name-based detection
        gnd_nets_by_type = [n for n in netlist.nets if n.net_type == "ground"]
        ground_names = {"GND", "GROUND", "VSS", "AGND", "DGND", "PGND"}
        gnd_nets_by_name = [n for n in netlist.nets if n.name.upper() in ground_names]

        # Combine both methods, prioritizing net_type (use names to avoid hash issues)
        gnd_net_names = set()
        for net in gnd_nets_by_type:
            gnd_net_names.add(net.name)
        for net in gnd_nets_by_name:
            gnd_net_names.add(net.name)

        all_gnd_nets = [
            (i, n) for i, n in enumerate(netlist.nets) if n.name in gnd_net_names
        ]

        if not all_gnd_nets:
            errors.append(
                ValidationError(
                    error_type=ValidationErrorType.MISSING_GROUND,
                    message="No ground nets found",
                    severity="error",
                    location=get_location("$.nets"),
                )
            )

        for i, net in all_gnd_nets:
            if len(net.connections) < 2:
                warnings.append(
                    ValidationError(
                        error_type=ValidationErrorType.INSUFFICIENT_GND_CONNECTIONS,
                        message=f"Ground net '{net.name}' has only {len(net.connections)} connection(s)",
                        net_id=net.name,
                        severity="warning",
                        location=get_location(f"$.nets.{i}.connections"),
                    )
                )
