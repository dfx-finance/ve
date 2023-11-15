#!/usr/bin/env python
from utils.contracts import gauge_controller as _gauge_controller
from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_outputs
from utils.network import connected_network

deployed = load_outputs(INSTANCE_ID)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. GaugeController address\n"
            "\t2. Gauge addresses"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    gauge_controller = _gauge_controller(deployed.read_addr("gaugeController"))
    gauge_controller.add_type("DFX Perpetuals", 0, {"from": DEPLOY_ACCT})
    gauge_controller.add_type("L2 Liquidity Pools", 1e18, {"from": DEPLOY_ACCT})
