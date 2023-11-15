#!/usr/bin/env python
from brownie import Contract, CcipRootGauge

from utils.ccip import ARBITRUM_CHAIN_SELECTOR, POLYGON_CHAIN_SELECTOR
from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def set_distributor(gauge_addr: str):
    gauge = Contract.from_abi("CcipRootGauge", gauge_addr, CcipRootGauge.abi)
    if gauge.distributor() != deployed.read_addr("dfxDistributor"):
        gauge.setDistributor(
            deployed.read_addr("dfxDistributor"), {"from": DEPLOY_ACCT}
        )


def set_admin(gauge_addr: str):
    gauge = Contract.from_abi("CcipRootGauge", gauge_addr, CcipRootGauge.abi)
    if gauge.admin() != existing.read_addr("multisig0"):
        gauge.updateAdmin(existing.read_addr("multisig0"), {"from": DEPLOY_ACCT})


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. Root gauge addresses\n"
            "\t2. Distributor address"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    arbitrum_gauges = [
        "arbitrumCadcUsdcRootGauge",
        "arbitrumGyenUsdcRootGauge",
        "arbitrumUsdceUsdcRootGauge",
    ]
    polygon_gauges = [
        "polygonCadcUsdcRootGauge",
        "polygonNgncUsdcRootGauge",
        "polygonTrybUsdcRootGauge",
        "polygonXsgdUsdcRootGauge",
        "polygonUsdceUsdcRootGauge",
    ]

    # ## Set distributor
    # for key in [*arbitrum_gauges, *polygon_gauges]:
    #     set_distributor(deployed.read_addr(key))

    ## Set admin
    for key in [*arbitrum_gauges, *polygon_gauges]:
        set_admin(deployed.read_addr(key))
