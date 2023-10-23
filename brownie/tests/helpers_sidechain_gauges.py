#!/usr/bin/env python
from utils.constants import (
    # DEFAULT_TYPE_WEIGHT,
    # DEFAULT_GAUGE_TYPE,
    DEFAULT_GAUGE_WEIGHT,
)


def add_to_gauge_controller(gauge_controller, gauge, multisig_0, add_placeholder=False):
    if add_placeholder:
        # add placeholder gauge type `1` to keep consistent with Angle distributor contract
        gauge_controller.add_type(
            "DFX Perpetuals",
            0,
            {"from": multisig_0},
        )

    # add new l2 gauge type to gauge controller
    gauge_controller.add_type(
        "L2 Liquidity Pools",
        1e18,
        {"from": multisig_0},
    )
    # add l2 gauge to gauge controller
    gauge_controller.add_gauge(
        gauge,
        2,
        DEFAULT_GAUGE_WEIGHT,
        {"from": multisig_0},
    )
