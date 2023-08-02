#!/usr/bin/env python
from brownie import accounts, config, network

from scripts.utils.constants import LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.utils.network import network_info

connected_network, is_local_network = network_info()

# Constants
DEPLOY_ACCT = accounts[0] if is_local_network else accounts.load("deployve")
DEPLOY_PROXY_ACCT = (
    accounts[1] if is_local_network else accounts.load("deployve-proxyadmin")
)
DFX_MULTISIG_ACCT = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"
DFX_PROXY_MULTISIG_ACCT = "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c"


def get_account(number=None):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if number:
        return accounts[number]
    if network.show_active() in config["networks"]:
        account = accounts.add(config["wallets"]["from_key"])
        return account
    return None
