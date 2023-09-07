#!/usr/bin/env python
import json
import time

from brownie import RootGaugeCctp

from utils.constants_addresses import Mumbai
from utils.network import get_network_addresses, network_info
from .utils_ccip import DEPLOY_ACCT, MUMBAI_CHAIN_SELECTOR

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

GAUGE_NAME = "Polygon ETH/BTC Root Gauge"
DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18

output_data = {"gauges": {"rootGauge": {}}}


def deploy():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. ccDFX Mainnet address\n"
            "\t2. DfxDistributor address\n"
            "\t3. Chainlink selector for L2 chain\n"
            "\t4. CCIP receiver address on L2 chain\n"
            "\t5. Fee token address or zero address for native\n"
        )
    )

    print(f"--- Deploying Root Gauge CCTP contract to {connected_network} ---")
    gauge = RootGaugeCctp.deploy(
        GAUGE_NAME,
        addresses.DFX_CCIP,
        DEPLOY_ACCT,  # distributor address
        addresses.CCIP_ROUTER,  # ccip router address
        MUMBAI_CHAIN_SELECTOR,  # target chain selector
        Mumbai.CCIP_RECEIVER,  # child chain receiver address (l2 address)
        "0x0000000000000000000000000000000000000000",  # fee token address
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )

    output_data["gauges"]["rootGauge"] = {
        "logic": gauge.address,
    }

    with open(
        f"./scripts/deployed_root_gauge_ccip_{int(time.time())}.json", "w"
    ) as output_f:
        json.dump(output_data, output_f, indent=4)


def main():
    gauge = deploy()
