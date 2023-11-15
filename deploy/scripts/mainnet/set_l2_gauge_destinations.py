#!/usr/bin/env python
from brownie import CcipSender

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


def set_sender_destination(root_gauge: str, receiver: str, chain_selector: int):
    sender = CcipSender.at(deployed.read_addr("ccipSender"))
    sender.setL2Destination(root_gauge, receiver, chain_selector, {"from": DEPLOY_ACCT})


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

    # Arbitrum
    set_sender_destination(
        deployed.read_addr("arbitrumCadcUsdcRootGauge"),
        existing.read_addr("arbitrumCadcUsdcReceiver"),
        ARBITRUM_CHAIN_SELECTOR,
    )
    set_sender_destination(
        deployed.read_addr("arbitrumGyenUsdcRootGauge"),
        existing.read_addr("arbitrumGyenUsdcReceiver"),
        ARBITRUM_CHAIN_SELECTOR,
    )
    set_sender_destination(
        deployed.read_addr("arbitrumUsdceUsdcRootGauge"),
        existing.read_addr("arbitrumUsdceUsdcReceiver"),
        ARBITRUM_CHAIN_SELECTOR,
    )

    # Polygon
    set_sender_destination(
        deployed.read_addr("polygonCadcUsdcRootGauge"),
        existing.read_addr("polygonCadcUsdcReceiver"),
        POLYGON_CHAIN_SELECTOR,
    )
    set_sender_destination(
        deployed.read_addr("polygonNgncUsdcRootGauge"),
        existing.read_addr("polygonNgncUsdcReceiver"),
        POLYGON_CHAIN_SELECTOR,
    )
    set_sender_destination(
        deployed.read_addr("polygonTrybUsdcRootGauge"),
        existing.read_addr("polygonTrybUsdcReceiver"),
        POLYGON_CHAIN_SELECTOR,
    )
    set_sender_destination(
        deployed.read_addr("polygonXsgdUsdcRootGauge"),
        existing.read_addr("polygonXsgdUsdcReceiver"),
        POLYGON_CHAIN_SELECTOR,
    )
    set_sender_destination(
        deployed.read_addr("polygonUsdceUsdcRootGauge"),
        existing.read_addr("polygonUsdceUsdcReceiver"),
        POLYGON_CHAIN_SELECTOR,
    )
