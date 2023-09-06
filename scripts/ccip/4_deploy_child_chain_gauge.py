#!/usr/bin/env python
import json
import time

from brownie import ZERO_ADDRESS, DfxDistributor, DfxUpgradeableProxy

from fork.utils.account import DEPLOY_ACCT
from utils import contracts
from utils.gas import gas_strategy, verify_gas_strategy
from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

output_data = {"l2Gauge": {"receiver": None, "streamer": None, "gauge": None}}


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Reward token address\n"
        )
    )
    if not is_local_network:
        verify_gas_strategy()
    should_verify = not is_local_network
    # should_verify = False

    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    print(f"--- Deploying Distributor contract to {connected_network} ---"))
    output_data["distributor"]["logic"] = dfx_distributor.address

    if not is_local_network:
        # Write output to file
        with open(
            f"./scripts/deployed_distributor_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
