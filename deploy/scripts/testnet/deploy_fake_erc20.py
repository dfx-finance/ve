#!/usr/bin/env python
from brownie import ERC20LP

from utils.config import DEPLOY_ACCT, verify_deploy_address, verify_deploy_network
from utils.network import connected_network

NAME = "Tester Token"
SYMBOL = "TEST"


# Creates fake LPT tokens for creating gauges without existing pools on local testnet forks
def deploy_fake_lpt(name, symbol):
    print(f"--- Deploying fake LPT contract to {connected_network} ---")
    token = ERC20LP.deploy(name, symbol, 18, 1e9, DEPLOY_ACCT, {"from": DEPLOY_ACCT})
    print(f"Mintable ERC20 deployed: {token.address}")


def main():
    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    deploy_fake_lpt(NAME, SYMBOL)
