#!/usr/bin/env python
import json
import time

from brownie import RootGaugeCctpBasic
from brownie import accounts

from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18
DEPLOY_ACCT = accounts.add(
    "0x0ac7fa86be251919f466d1313c31ecb341cbc09d55fcc2ffa18977619e9097fb"
)
PROXY_ADMIN_ACCT = accounts.add(
    "0xbdb5dd6948238006f64878060165682ed53067e602d15b07372ba276b8f06eef"
)

output_data = {"gauges": {"rootGaugeTest": {}}}


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. root_gauge_cctp address\n"
            "\t2. DfxDistributor address\n"
        )
    )

    print(f"--- Deploying Root Gauge CCTP contract to {connected_network} ---")
    gauge_implementation = RootGaugeCctpBasic.deploy(
        "L1 ETH/BTC Root Gauge",
        addresses.DFX_CCIP,
        DEPLOY_ACCT,
        addresses.CCIP_ROUTER,  # mock ccip router address
        12532609583862916517,  # mock target chain selector (polygon mumbai)
        "0x33Af579F8faFADa29d98922A825CFC0228D7ce39",  # mock destination address
        "0x0000000000000000000000000000000000000000",  # mock fee token address
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )

    output_data["gauges"]["rootGaugeTest"] = {
        "logic": gauge_implementation.address,
    }

    with open(
        f"./scripts/deployed_root_gauge_ccip_{int(time.time())}.json", "w"
    ) as output_f:
        json.dump(output_data, output_f, indent=4)
