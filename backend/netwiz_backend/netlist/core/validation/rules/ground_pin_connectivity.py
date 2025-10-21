"""
Ground Pin Connectivity validation rule.

This rule checks that ground pins are connected to ground nets.
"""

from collections.abc import Callable

from netwiz_backend.json_tracker.types import LocationInfo
from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation.rules.rule_check_abc import RuleCheckABC
from netwiz_backend.netlist.core.validation.types import (
    GROUND_PIN_NOT_CONNECTED_TO_GROUND,
    NetlistValidationError,
)


class GroundPinConnectivityRule(RuleCheckABC):
    """Rule to check that ground pins are connected to ground nets."""

    def __init__(self):
        super().__init__(
            error_types=(GROUND_PIN_NOT_CONNECTED_TO_GROUND,),
            description="Ground pins must be connected to ground nets",
        )

    def _check(
        self,
        netlist: Netlist,
        errors: list[NetlistValidationError],
        warnings: list[NetlistValidationError],
        get_location: Callable[[str], LocationInfo | None],
    ) -> None:
        """Check that ground pins are connected to ground nets."""
        # Find ground nets
        gnd_nets_by_type = [n for n in netlist.nets if n.net_type == "ground"]
        ground_names = {"GND", "GROUND", "VSS", "AGND", "DGND", "PGND"}
        gnd_nets_by_name = [n for n in netlist.nets if n.name.upper() in ground_names]

        gnd_net_names = set()
        for net in gnd_nets_by_type:
            gnd_net_names.add(net.name)
        for net in gnd_nets_by_name:
            gnd_net_names.add(net.name)

        all_gnd_nets = [
            (i, n) for i, n in enumerate(netlist.nets) if n.name in gnd_net_names
        ]
        first_ground_net_ind = sorted(all_gnd_nets)[0][0] if all_gnd_nets else None
        ground_net_location = (
            get_location(f"$.nets.{first_ground_net_ind}.connections")
            if first_ground_net_ind
            else None
        )

        # Find all ground pins
        ground_pins = []
        for i, component in enumerate(netlist.components):
            for pi, pin in enumerate(component.pins):
                if pin.type == "ground":
                    ground_pins.append((i, pi, component.name, pin.number))

        # Check if each ground pin is connected to a ground net
        for _, _, component_name, pin_number in ground_pins:
            connected_to_ground = False
            for _, net in all_gnd_nets:
                for connection in net.connections:
                    if (
                        connection.component == component_name
                        and connection.pin == pin_number
                    ):
                        connected_to_ground = True
                        break
                if connected_to_ground:
                    break

            if not connected_to_ground:
                errors.append(
                    NetlistValidationError(
                        error_type=GROUND_PIN_NOT_CONNECTED_TO_GROUND,
                        message=f"Ground pin {component_name}.{pin_number} is not connected to a ground net",
                        component_id=component_name,
                        severity="error",
                        location=ground_net_location,
                    )
                )
