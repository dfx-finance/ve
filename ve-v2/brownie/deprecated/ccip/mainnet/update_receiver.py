#!/usr/bin/env python
from brownie import RootGaugeCcip, Contract
from utils.network import get_network_addresses

from utils.constants_addresses import Mumbai
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()


def main():
    gauge = Contract.from_abi(
        "RootGaugeCcip", addresses.MUMBAI_ETH_BTC_ROOT_GAUGE, RootGaugeCcip.abi
    )
    gauge.setDestination(Mumbai.CCIP_RECEIVER, {"from": DEPLOY_ACCT})
    print(f"Root gauge receiver (L2) updated: {Mumbai.CCIP_RECEIVER}")
