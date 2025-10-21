"""
Unconnected Components validation rule.

This rule checks for components that have pins not connected to any nets.
"""

from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    UNCONNECTED_COMPONENT,
    NetlistValidationError,
)


class UnconnectedComponentsRule(RuleCheckABC):
    """Rule to check for components with unconnected pins."""

    def __init__(self):
        super().__init__(
            error_types=(UNCONNECTED_COMPONENT,),
            description="All component pins should be connected to nets",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[NetlistValidationError],
        warnings: list[NetlistValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check for components with unconnected pins."""
        # Create a set of all connected pins for quick lookup
        connected_pins = set()
        for net in netlist.nets:
            for connection in net.connections:
                connected_pins.add((connection.component, connection.pin))

        # Check each component's pins
        for i, component in enumerate(netlist.components):
            unconnected_pins = []
            for pin in component.pins:
                if (component.name, pin.number) not in connected_pins:
                    unconnected_pins.append(pin.number)

            if unconnected_pins:
                warnings.append(
                    NetlistValidationError(
                        error_type=UNCONNECTED_COMPONENT,
                        message=f"Component '{component.name}' has unconnected pins: {', '.join(unconnected_pins)}",
                        component_id=component.name,
                        severity="warning",
                        location=get_location(f"$.components.{i}.pins"),
                    )
                )
