#!/usr/bin/env python
from brownie import clDFX, ZERO_ADDRESS

import eth_abi
import json
import time

from fork.utils.account import DEPLOY_ACCT
from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

output_data = {"clDFX": None}


def main():
    print(f"--- Deploying clDFX contract to {connected_network} ---")

    cldfx_params = eth_abi.encode_abi(
        ["string", "string", "address", "string"],
        ("DFX", "clDFX", ZERO_ADDRESS, "1.0.0"),
    ).hex()
    cldfx = clDFX.deploy(
        "DFX",
        "clDFX",
        ZERO_ADDRESS,
        "1.0.0",
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )
    output_data["clDFX"] = cldfx.address
    output_data["clDFXParams"] = cldfx_params

    with open(f"./scripts/deployed_cldfx_{int(time.time())}.json", "w") as output_f:
        json.dump(output_data, output_f, indent=4)
