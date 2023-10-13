#!/usr/bin/env python
from brownie import Contract, clDFX, ERC20LP, DfxUpgradeableProxy, ZERO_ADDRESS

import json
import time

from fork.utils.account import DEPLOY_ACCT, DEPLOY_PROXY_ACCT
from utils.helper import verify_deploy_address, verify_deploy_network
from utils.log import write_contract
from utils.network import network_info

connected = network_info()

output_data = {"clDFX": {}}

NAME = "DFX Token (L2)"
SYMBOL = "DFX"


def deploy(verify_contracts=False):
    print(f"--- Deploying clDFX contract to {connected.name} ---")
    clDfx = clDFX.deploy(
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    output_data["clDFX"]["logic"] = clDfx.address

    print(f"--- Deploying clDFX proxy contract to {connected.name} ---")
    clDfx_initializer_calldata = clDfx.initialize.encode_input(
        NAME,  # token name
        SYMBOL,  # token symbol
        ZERO_ADDRESS,  # minter
        "0.0.0",  # version
    )
    proxy = DfxUpgradeableProxy.deploy(
        clDfx.address,
        DEPLOY_PROXY_ACCT,
        clDfx_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    proxy = Contract.from_abi("clDFX", proxy, clDFX.abi)
    output_data["clDFX"]["proxy"] = proxy.address
    output_data["clDFX"]["clDFXParams"] = clDfx_initializer_calldata
    write_contract("polygonClDfx", proxy.address)


def main():
    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)

    verify_contracts = False if connected.is_local else True
    deploy(verify_contracts)

    if not connected.is_local:
        with open(f"./scripts/polygon_cldfx_{int(time.time())}.json", "w") as output_f:
            json.dump(output_data, output_f, indent=4)
