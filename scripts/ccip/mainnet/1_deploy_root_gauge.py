#!/usr/bin/env python
import json
import time

from brownie import DfxUpgradeableProxy, RootGaugeCcip

from utils.constants_addresses import Mumbai
from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT, PROXY_ADMIN_ACCT, MUMBAI_CHAIN_SELECTOR

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

GAUGE_NAME = "Polygon ETH/BTC Root Gauge"
DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18
DESTINATION_CHAIN_SELECTOR = MUMBAI_CHAIN_SELECTOR
DESTINATION_ADDRESS = Mumbai.CCIP_RECEIVER


output_data = {"gauges": {"rootGauge": {}}}


def deploy():
    print(f"--- Deploying Root Gauge CCIP contract to {connected_network} ---")
    gauge_implementation = RootGaugeCcip.deploy(
        addresses.CCIP_DFX,  # source chain reward token
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )

    print(f"--- Deploying Root Gauge CCIP proxy contract to {connected_network} ---")
    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_implementation.initialize.encode_input(
        GAUGE_NAME,
        DEPLOY_ACCT,  # source chain distributor address
        addresses.CCIP_ROUTER,  # source chain ccip router address
        MUMBAI_CHAIN_SELECTOR,  # target chain selector
        DESTINATION_ADDRESS,  # child chain receiver address (l2 address)
        "0x0000000000000000000000000000000000000000",  # fee token address (zero address for native)
        DEPLOY_ACCT,
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
        PROXY_ADMIN_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )

    output_data["gauges"]["rootGauge"] = {
        "logic": gauge_implementation.address,
        "calldata": gauge_initializer_calldata,
        "proxy": proxy.address,
    }

    with open(
        f"./scripts/deployed_root_gauge_ccip_{int(time.time())}.json", "w"
    ) as output_f:
        json.dump(output_data, output_f, indent=4)


def main():
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
    deploy()
