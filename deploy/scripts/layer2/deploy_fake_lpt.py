#!/usr/bin/env python
from brownie import ERC20LP

from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import write_contract
from utils.network import connected_network

NAME = "DFX Token (L2)"
SYMBOL = "DFX"


# Creates fake LPT tokens for creating gauges without existing pools on local testnet forks
def deploy_fake_lpt(name, symbol, i=0):
    print(f"--- Deploying fake LPT contract to {connected_network} ---")
    lpt = ERC20LP.deploy(
        name, symbol, 18, 1e9, {"from": DEPLOY_ACCT}, publish_source=VERIFY_CONTRACTS
    )

    write_contract(INSTANCE_ID, f"arbitrumFakeLpt{i}", lpt.address)


def main():
    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    deploy_fake_lpt("L2 ETH/BTC LP", "dfx-eth-btc-lpt", i=0)
