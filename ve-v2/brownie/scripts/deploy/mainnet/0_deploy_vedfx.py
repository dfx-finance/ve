#!/usr/bin/env python
from brownie import VeDFX
import eth_abi
import json
import time

from fork.utils.account import DEPLOY_ACCT
from utils.constants_addresses import Ethereum, EthereumLocalhost
from utils.helper import (
    verify_deploy_address,
    verify_deploy_network,
)
from utils.log import write_contract
from utils.network import network_info

connected = network_info()

# override addresses when running on local fork
Ethereum = EthereumLocalhost if connected.is_local else Ethereum


def deploy():
    print(f"--- Deploying veDFX contract to {connected.name} ---")
    output_data = {"veDFX": None}

    vedfx_params = eth_abi.encode_abi(
        ["address", "string", "string", "string"],
        (Ethereum.DFX, "Vote-escrowed DFX", "veDFX", "veDFX_1.0.0"),
    ).hex()
    vedfx = VeDFX.deploy(
        Ethereum.DFX,
        "Vote-escrowed DFX",
        "veDFX",
        "veDFX_1.0.0",
        {"from": DEPLOY_ACCT},
    )
    output_data["veDFX"] = vedfx.address
    output_data["veDFXParams"] = vedfx_params

    write_contract("veDFX", vedfx.address)
    if not connected.is_local:
        with open(f"./scripts/deployed_vedfx_{int(time.time())}.json", "w") as output_f:
            json.dump(output_data, output_f, indent=4)


def main():
    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)
    deploy()
