#!/usr/bin/env python
from brownie import ChildChainReceiver, Contract, interface, web3

from utils.network import get_network_addresses
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()

OLD_RECEIVER = "0xa47562EBba9f246039d5f032d0DE56a97aA2e428"


# Send ccDFX and contract-owned ETH to owner
def recover_assets():
    receiver = Contract.from_abi(
        "ChildChainReceiver", OLD_RECEIVER, ChildChainReceiver.abi
    )
    # transfer ccDFX
    dfx_bal = interface.IERC20(addresses.CCIP_DFX).balanceOf(receiver)
    receiver.emergencyWithdraw(
        DEPLOY_ACCT, addresses.CCIP_DFX, dfx_bal, {"from": DEPLOY_ACCT}
    )
    # transfer ETH
    eth_bal = web3.eth.get_balance(receiver.address)
    receiver.emergencyWithdrawNative(DEPLOY_ACCT, eth_bal, {"from": DEPLOY_ACCT})


def main():
    recover_assets()
