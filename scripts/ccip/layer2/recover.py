#!/usr/bin/env python
from brownie import (
    ChildChainReceiver,
    ChildChainStreamer,
    RewardsOnlyGauge,
    Contract,
    interface,
    web3,
)

from utils.network import get_network_addresses
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()

OLD_RECEIVER = "0x100f5bac104DE7D557fb208b19A9E5588691dBB7"
OLD_STREAMER = "0x6d8f120Eb55E0F05D31C4249c011062ec3A748e3"
OLD_GAUGE = "0x5681885eec6ade5161c51F8807350107cE2Cd905"


# Send ccDFX and contract-owned ETH to owner
def recover_assets():
    receiver = Contract.from_abi(
        "ChildChainReceiver", OLD_RECEIVER, ChildChainReceiver.abi
    )
    streamer = Contract.from_abi(
        "ChildChainStreamer", OLD_STREAMER, ChildChainStreamer.abi
    )
    gauge = Contract.from_abi("RewardsOnlyGauge", OLD_GAUGE, RewardsOnlyGauge.abi)

    # transfer ccDFX
    dfx_bal = interface.IERC20(addresses.CCIP_DFX).balanceOf(receiver)
    if dfx_bal:
        receiver.emergencyWithdraw(
            DEPLOY_ACCT, addresses.CCIP_DFX, dfx_bal, {"from": DEPLOY_ACCT}
        )

    # streamer.remove_reward(addresses.CCIP_DFX, {"from": DEPLOY_ACCT})
    # # transfer ETH
    # eth_bal = web3.eth.get_balance(receiver.address)
    # if eth_bal:
    #     receiver.emergencyWithdrawNative(DEPLOY_ACCT, eth_bal, {"from": DEPLOY_ACCT})
    # # transfer LPT
    # gauge_bal = gauge.balanceOf(DEPLOY_ACCT)
    # if gauge_bal:
    #     gauge.withdraw(gauge_bal, True, {"from": DEPLOY_ACCT})


def main():
    recover_assets()
