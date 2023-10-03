#!/usr/bin/env python
from brownie import ChildChainReceiver

from utils.constants_addresses import Sepolia
from utils.network import get_network_addresses
from ..utils_ccip import DEPLOY_ACCT, SEPOLIA_CHAIN_SELECTOR

addresses = get_network_addresses()


def load():
    receiver = ChildChainReceiver.at(addresses.CCIP_RECEIVER)
    return receiver


def main():
    receiver = load()

    # whitelist source chain and address on receiver
    receiver.whitelistSourceChain(SEPOLIA_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    receiver.whitelistSender(Sepolia.MUMBAI_ETH_BTC_ROOT_GAUGE, {"from": DEPLOY_ACCT})
