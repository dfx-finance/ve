#!/usr/bin/env python
from brownie import Contract, clDFX, DfxUpgradeableProxy, ZERO_ADDRESS

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import write_contract
from utils.network import connected_network


NAME = "DFX Token (L2)"
SYMBOL = "DFX"


def deploy():
    print(f"--- Deploying clDFX contract to {connected_network} ---")
    clDfx_logic = clDFX.deploy(
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )

    print(f"--- Deploying clDFX proxy contract to {connected_network} ---")
    clDfx_initializer_calldata = clDfx_logic.initialize.encode_input(
        NAME,  # token name
        SYMBOL,  # token symbol
        ZERO_ADDRESS,  # minter
        "0.0.1",  # version
    )
    proxy = DfxUpgradeableProxy.deploy(
        clDfx_logic.address,
        DEPLOY_PROXY_ACCT,
        clDfx_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    proxy = Contract.from_abi("clDFX", proxy, clDFX.abi)

    write_contract(INSTANCE_ID, "clDFXLogic", clDfx_logic.address)
    write_contract(INSTANCE_ID, "clDFX", proxy.address)


def main():
    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    deploy()
