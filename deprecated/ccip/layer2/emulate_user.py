#!/usr/bin/env python
from brownie import DfxUpgradeableProxy, RewardsOnlyGauge, Contract, interface

from utils.network import get_network_addresses, network_info
from ..utils_ccip import DEPLOY_ACCT

addresses = get_network_addresses()
connected_network, is_local_network = network_info()


def main():
    proxy = DfxUpgradeableProxy.at(addresses.DFX_ETH_BTC_GAUGE)
    starting_balance = interface.IERC20(addresses.CCIP_DFX).balanceOf(DEPLOY_ACCT)

    # change abi method to "view" to perform staticcall
    for record in RewardsOnlyGauge.abi:
        if record["name"] == "claimable_reward_write":
            record["stateMutability"] = "view"

    # load gauge interface on proxy for non-admin users
    gauge = Contract.from_abi("RewardsOnlyGauge", proxy, RewardsOnlyGauge.abi)
    available_rewards = gauge.claimable_reward_write(DEPLOY_ACCT, addresses.CCIP_DFX)
    print(f"Claimable: {available_rewards/1e18}")

    # tx = gauge.claimable_reward_write(
    #     DEPLOY_ACCT, addresses.CCIP_DFX, {"from": DEPLOY_ACCT}
    # )
    # print(f"Claimable: {tx.value/1e18}")

    # gauge.claim_rewards({"from": DEPLOY_ACCT})
    ending_balance = interface.IERC20(addresses.CCIP_DFX).balanceOf(DEPLOY_ACCT)

    print("")
    print(f"Starting: {starting_balance/1e18}")
    print(f"Ending: {ending_balance/1e18}")
    print(f"Diff: {(ending_balance-starting_balance)/1e18}")
