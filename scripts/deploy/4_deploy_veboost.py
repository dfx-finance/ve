#!/usr/bin/env python
from brownie import ZERO_ADDRESS, BoostV2
from brownie.network import gas_price
import eth_abi
import json
import time

from fork.utils.account import DEPLOY_ACCT
from utils.gas import gas_strategy, verify_gas_strategy
from utils.network import get_network_addresses, network_info


gas_price(gas_strategy)
connected_network, is_local_network = network_info()
addresses = get_network_addresses()


def main():
    print(f"--- Deploying BoostV2 contract to {connected_network} ---")
    if not is_local_network:
        verify_gas_strategy()

    output_data = {"boostV2": None}

    boostV2_params = eth_abi.encode_abi(
        ["address", "address"],
        (ZERO_ADDRESS, addresses.VEDFX),
    ).hex()

    boostV2 = BoostV2.deploy(
        ZERO_ADDRESS,
        addresses.VEDFX,
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
        publish_source=True,
    )
    output_data["BoostV2"] = boostV2.address
    output_data["BoostV2Params"] = boostV2_params

    with open(f"./scripts/deployed_boostv2_{int(time.time())}.json", "w") as output_f:
        json.dump(output_data, output_f, indent=4)
