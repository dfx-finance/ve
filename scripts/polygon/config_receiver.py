#!/usr/bin/env python
from brownie import ChildChainReceiver

from fork.utils.account import DEPLOY_ACCT
from utils.ccip import ETHEREUM_CHAIN_SELECTOR
from utils.constants_addresses import Polygon
from utils.network import network_info

connected = network_info()


# whitelist source chain and address on receiver
def whitelist_sender(receiver_addr: str, root_gauge_addr: str):
    receiver = ChildChainReceiver.at(receiver_addr)
    receiver.whitelistSourceChain(ETHEREUM_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    receiver.whitelistSender(root_gauge_addr, {"from": DEPLOY_ACCT})
    return receiver


def main():
    # Polygon CADC/USDC Receiver
    whitelist_sender(Polygon.CCIP_CADC_USDC_RECEIVER)
    # Polygon NGNC/USDC Receiver
    whitelist_sender(Polygon.CCIP_NGNC_USDC_RECEIVER)
    # Polygon TRYB/USDC Receiver
    whitelist_sender(Polygon.CCIP_NGNC_USDC_RECEIVER)
    # Polygon XSGD/USDC Receiver
    whitelist_sender(Polygon.CCIP_NGNC_USDC_RECEIVER)
