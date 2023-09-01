#!/usr/bin/env python
import json
import time

from brownie import DfxUpgradeableProxy, RootGaugeCctp
from brownie import  accounts, config

from utils import contracts
from utils.gas import  verify_gas_strategy
from utils.helper import fund_multisigs
from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18
DEPLOY_ACCT = accounts.add(config["wallets"]["from_key"])

output_data = {"gauges": {"amm": {}}}


def main():
    print(
        (
            "Script 3 of 3:\n\n"
            "NOTE: This script expects configuration for:\n"
            "\t1. root_gauge_cctp address\n"
            "\t2. DfxDistributor address\n"
        )
    )
    if not is_local_network:
        verify_gas_strategy()
    if is_local_network:
        fund_multisigs(DEPLOY_ACCT)


    print(f"--- Deploying Root Gauge CCTP contract to {connected_network} ---")
    fee_token = addresses.LINK

    print(fee_token)

    # deploy gauge logic

    if not is_local_network:
        print("Sleeping after deploy....")
        time.sleep(10)

    # deploy gauge behind proxy
    print(
        f"--- Deploying  Root Gauge CCTP proxy contract to {connected_network} ---"
    )


    gauge_implementation = RootGaugeCctp.deploy(
        {"from": DEPLOY_ACCT},
        publish_source=True
    )

    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_implementation.initialize.encode_input(
        "L1 ETH/BTC Root Gauge",
        fee_token,
        DEPLOY_ACCT,
        addresses.CCIP_ROUTER,  # mock ccip router address
        14767482510784806043,  # mock target chain selector
        "0x33Af579F8faFADa29d98922A825CFC0228D7ce39",  # mock destination address
        "0x0000000000000000000000000000000000000000",  # mock fee token address
        DEPLOY_ACCT,
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_implementation.address,
        DEPLOY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=True
    )


    output_data["gauges"]["amm"] = {
        "logic": gauge_implementation.address,
        "calldata": gauge_initializer_calldata,
        "proxy": proxy.address,
    }

    with open(
        f"./scripts/deployed_root_gauge_ccip_{int(time.time())}.json", "w"
    ) as output_f:
        json.dump(output_data, output_f, indent=4)
