#!/usr/bin/env python
from brownie import ChildChainReceiver

from utils.config import DEPLOY_ACCT
# from utils.ccip import ETHEREUM_CHAIN_SELECTOR
# from utils.constants_addresses import (
#     Arbitrum,
#     Ethereum,
#     ArbitrumLocalhost,
#     EthereumLocalhost,
# )
from utils.network import connected_network


# whitelist source chain and address on receiver
def whitelist_sender(receiver_addr: str, root_gauge_addr: str):
    receiver = ChildChainReceiver.at(receiver_addr)
    receiver.whitelistSourceChain(ETHEREUM_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    receiver.whitelistSender(root_gauge_addr, {"from": DEPLOY_ACCT})
    return receiver


def main():
    # Arbitrum CADC/USDC Receiver
    whitelist_sender(
        Arbitrum.CCIP_CADC_USDC_RECEIVER,
        Ethereum.ARBITRUM_CADC_USDC_ROOT_GAUGE,
    )
    # Arbitrum GYEN/USDC Receiver
    whitelist_sender(
        Arbitrum.CCIP_GYEN_USDC_RECEIVER,
        Ethereum.ARBITRUM_GYEN_USDC_ROOT_GAUGE,
    )
