#!/usr/bin/env python
from utils.contracts import gauge as _gauge, gauge_controller as _gauge_controller
from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    SIDECHAIN_GAUGE_TYPE,
    DEFAULT_GAUGE_WEIGHT,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def add_to_gauge_controller(gaugeAddr: str, admin: str):
    gauge_controller = _gauge_controller(deployed.read_addr("gaugeController"))
    gauge = _gauge(gaugeAddr)

    print(f"--- Add {gauge.name()} gauge to GaugeController ---")
    gauge_controller.add_gauge(
        gauge.address,
        SIDECHAIN_GAUGE_TYPE,
        DEFAULT_GAUGE_WEIGHT,
        {"from": admin},
    )


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

    add_to_gauge_controller(
        deployed.read_addr("arbitrumCadcUsdcRootGauge"), DEPLOY_ACCT
    )
    add_to_gauge_controller(
        deployed.read_addr("arbitrumGyenUsdcRootGauge"), DEPLOY_ACCT
    )
    add_to_gauge_controller(
        deployed.read_addr("arbitrumUsdceUsdcRootGauge"), DEPLOY_ACCT
    )
