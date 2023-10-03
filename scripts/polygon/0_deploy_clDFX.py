#!/usr/bin/env python
from brownie import clDFX, ERC20LP, ZERO_ADDRESS

import eth_abi
import json
import time

from fork.utils.account import DEPLOY_ACCT
from utils.helper import verify_deploy_address, verify_deploy_network
from utils.log import write_contract
from utils.network import network_info

connected = network_info()

output_data = {"clDFX": None}


def deploy(verify_contracts=False):
    print(f"--- Deploying clDFX contract to {connected.name} ---")

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
        publish_source=verify_contracts,
    )
    output_data["clDFX"] = cldfx.address
    output_data["clDFXParams"] = cldfx_params
    write_contract("polygonClDfx", cldfx.address)


# Creates fake LPT tokens for creating gauges without existing pools on local testnet forks
def deploy_fake_lpt(name, symbol, i=0):
    print(f"--- Deploying fake LPT contract to {connected.name} ---")
    lpt = ERC20LP.deploy(name, symbol, 18, 1e9, {"from": DEPLOY_ACCT})

    write_contract(f"polygonFakeLpt{i}", lpt.address)


def main():
    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)

    verify_contracts = False if connected.is_local else True
    deploy(verify_contracts)

    deploy_fake_lpt("DFX Fake CADC/USDC LPT", "fake-cadc-usdc")
    deploy_fake_lpt("DFX Fake NGNC/USDC LPT", "fake-ngnc-usdc", i=1)
    deploy_fake_lpt("DFX Fake TRYB/USDC LPT", "fake-tryb-usdc", i=2)
    deploy_fake_lpt("DFX Fake XSGD/USDC LPT", "fake-xsgd-usdc", i=3)

    if not connected.is_local:
        with open(f"./scripts/polygon_cldfx_{int(time.time())}.json", "w") as output_f:
            json.dump(output_data, output_f, indent=4)
