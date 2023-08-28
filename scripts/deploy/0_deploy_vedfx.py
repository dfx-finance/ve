#!/usr/bin/env python
from brownie import VeDFX
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
    print(f"--- Deploying veDFX contract to {connected_network} ---")
    if not is_local_network:
        verify_gas_strategy()

    output_data = {"veDFX": None}

    vedfx_params = eth_abi.encode_abi(
        ["address", "string", "string", "string"],
        (addresses.DFX, "Vote-escrowed DFX", "veDFX", "veDFX_1.0.0"),
    ).hex()
    vedfx = VeDFX.deploy(
        addresses.DFX,
        "Vote-escrowed DFX",
        "veDFX",
        "veDFX_1.0.0",
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
    )
    output_data["veDFX"] = vedfx.address
    output_data["veDFXParams"] = vedfx_params

    with open(f"./scripts/deployed_vedfx_{int(time.time())}.json", "w") as output_f:
        json.dump(output_data, output_f, indent=4)
