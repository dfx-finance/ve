#!/usr/bin/env python
from brownie import ChildChainReceiver, accounts, interface, ZERO_ADDRESS

from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

DFX_AMOUNT = 1e17  # rewards
ETH_AMOUNT = 4e16  # gas


def main():
    interface.IERC20(addresses.CCIP_DFX).transfer(
        addresses.CCIP_RECEIVER,
        DFX_AMOUNT,
        {"from": DEPLOY_ACCT},
    )
    DEPLOY_ACCT.transfer(addresses.CCIP_RECEIVER, ETH_AMOUNT)
