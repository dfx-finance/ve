#!/usr/bin/env python
from brownie import ChildChainReceiver

from fork.utils.account import DEPLOY_ACCT
from utils.ccip import ETHEREUM_CHAIN_SELECTOR
from utils.constants_addresses import (
    Ethereum,
    Polygon,
    EthereumLocalhost,
    PolygonLocalhost,
)
from utils.network import network_info

connected = network_info()
Ethereum = EthereumLocalhost if connected.is_local else Ethereum
Polygon = PolygonLocalhost if connected.is_local else Polygon


# whitelist source chain and address on receiver
def whitelist_sender(receiver_addr: str, root_gauge_addr: str):
    receiver = ChildChainReceiver.at(receiver_addr)
    receiver.whitelistSourceChain(ETHEREUM_CHAIN_SELECTOR, {"from": DEPLOY_ACCT})
    receiver.whitelistSender(root_gauge_addr, {"from": DEPLOY_ACCT})
    return receiver


def main():
    # Polygon CADC/USDC Receiver
    whitelist_sender(
        Polygon.CCIP_CADC_USDC_RECEIVER,
        Ethereum.POLYGON_CADC_USDC_ROOT_GAUGE,
    )
    # Polygon NGNC/USDC Receiver
    whitelist_sender(
        Polygon.CCIP_NGNC_USDC_RECEIVER, Ethereum.POLYGON_NGNC_USDC_ROOT_GAUGE
    )
    # Polygon TRYB/USDC Receiver
    whitelist_sender(
        Polygon.CCIP_TRYB_USDC_RECEIVER, Ethereum.POLYGON_TRYB_USDC_ROOT_GAUGE
    )
    # Polygon XSGD/USDC Receiver
    whitelist_sender(
        Polygon.CCIP_XSGD_USDC_RECEIVER, Ethereum.POLYGON_XSGD_USDC_ROOT_GAUGE
    )
