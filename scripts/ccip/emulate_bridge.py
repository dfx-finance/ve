#!/usr/bin/env python
from brownie import ChildChainReceiver, accounts, interface, ZERO_ADDRESS

from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

DEPLOY_ACCT = accounts.add(
    "0x0ac7fa86be251919f466d1313c31ecb341cbc09d55fcc2ffa18977619e9097fb"
)
DFX_OFT = "0xc1c76a8c5bFDE1Be034bbcD930c668726E7C1987"  # clCCIP-LnM / Polygon Mumbai
CCIP_ROUTER = "0x70499c328e1E2a3c41108bd3730F6670a44595D1"  # Router / Polygon Mumbai
CHILD_CHAIN_RECEIVER = "0xa47562EBba9f246039d5f032d0DE56a97aA2e428"
SEPOLIA_CHAIN_SELECTOR = 16015286601757825753


def main():
    # interface.IERC20(DFX_OFT).transfer(
    #     CHILD_CHAIN_RECEIVER,
    #     5e16,
    #     {"from": DEPLOY_ACCT},
    # )
    # DEPLOY_ACCT.transfer(CHILD_CHAIN_RECEIVER, 1e17)

    receiver = ChildChainReceiver.at(CHILD_CHAIN_RECEIVER)
    msg = receiver.testBuildCcipMessage(receiver, DFX_OFT, 5e16, ZERO_ADDRESS)
    print(msg)
    # print(receiver.streamer())
    # receiver.testCcipReceive(msg, {"from": DEPLOY_ACCT})

    # receiver.testNotify(DFX_OFT, 1e17, {"from": DEPLOY_ACCT})
