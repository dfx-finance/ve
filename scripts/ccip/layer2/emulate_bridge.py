#!/usr/bin/env python
from brownie import ChildChainReceiver, accounts, interface, ZERO_ADDRESS

from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()
connected_network, is_local_network = network_info()


def main():
    reward_amount = 5e16
    receiver = ChildChainReceiver.at(addresses.CCIP_RECEIVER)
    # msg = receiver.testBuildCcipMessage(receiver, DFX_OFT, 5e16, ZERO_ADDRESS)
    # print(msg)
    # print(receiver.streamer())
    # receiver.testCcipReceive(msg, {"from": DEPLOY_ACCT})

    receiver.testNotify(addresses.CCIP_DFX, reward_amount, {"from": DEPLOY_ACCT})
