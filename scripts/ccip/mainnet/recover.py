#!/usr/bin/env python
from brownie import RootGaugeCctp, Contract, interface, web3

from utils.network import get_network_addresses
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()

PREV_GAUGE = "0x6A7DfDA5ea407E31f753279FaEEd1546189F185E"
NEW_GAUGE = addresses.MUMBAI_ETH_BTC_ROOT_GAUGE


# Send ccDFX and contract-owned ETH to new address
def recover():
    prev_gauge = Contract.from_abi("RootGaugeCctp", PREV_GAUGE, RootGaugeCctp.abi)
    # transfer ccDFX
    dfx_bal = interface.IERC20(addresses.CCIP_DFX).balanceOf(PREV_GAUGE)
    prev_gauge.emergencyWithdraw(
        NEW_GAUGE, addresses.CCIP_DFX, dfx_bal, {"from": DEPLOY_ACCT}
    )
    # transfer ETH
    eth_bal = web3.eth.get_balance(prev_gauge.address)
    prev_gauge.emergencyWithdrawNative(NEW_GAUGE, eth_bal, {"from": DEPLOY_ACCT})


def main():
    recover()
