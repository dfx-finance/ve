#!/usr/bin/env python
from brownie import accounts, config, network

from .constants import LOCAL_BLOCKCHAIN_ENVIRONMENTS
from .network import network_info

connected_network, is_local_network = network_info()

# Constants
DEPLOY_ACCT = accounts[0]
DEPLOY_PROXY_ACCT = accounts[1]

if not is_local_network:
    print("Loading live wallets [deployve, deployve-proxyadmin]...")
    DEPLOY_ACCT = accounts.load("deployve")
    DEPLOY_PROXY_ACCT = accounts.load("deployve-proxyadmin")


def get_account(number=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if number:
        return accounts[number]
    if network.show_active() in config["networks"]:
        account = accounts.add(config["wallets"]["from_key"])
        return account
    return None


def impersonate(addr):
    return accounts.at(addr, force=True)
