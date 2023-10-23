#!/usr/bin/env python
from brownie import ERC20LP

import json
import time

from fork.utils.account import DEPLOY_ACCT
from utils.log import write_contract
from utils.network import network_info

connected = network_info()


# Creates fake LPT tokens for creating gauges without existing pools on local testnet forks
def deploy_fake_lpt(name, symbol, i=0):
    print(f"--- Deploying fake LPT contract to {connected.name} ---")
    lpt = ERC20LP.deploy(name, symbol, 18, 1e9, {"from": DEPLOY_ACCT})

    write_contract(f"polygonFakeLpt{i}", lpt.address)


def main():
    deploy_fake_lpt("DFX Fake CADC/USDC LPT", "fake-cadc-usdc")
    deploy_fake_lpt("DFX Fake NGNC/USDC LPT", "fake-ngnc-usdc", i=1)
    deploy_fake_lpt("DFX Fake TRYB/USDC LPT", "fake-tryb-usdc", i=2)
    deploy_fake_lpt("DFX Fake XSGD/USDC LPT", "fake-xsgd-usdc", i=3)
