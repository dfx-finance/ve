#!/usr/bin/env python
from brownie import accounts

from utils import contracts
from utils.account import DEPLOY_ACCT, DFX_MULTISIG_ACCT
from utils.gas import gas_strategy
from utils.network import get_network_addresses


addresses = get_network_addresses()

TOPUP_DFX_REWARDS = 4674.6575342466 * 1e18  # 1,706,250.00 / (365/7) epochs / 7 gauges


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {"from": from_account, "gas_price": gas_strategy})
    print("Sender account DFX balance:", dfx.balanceOf(from_account) / 1e18)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. DfxDistributor address\n"
        )
    )
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    dfx = contracts.load_dfx_token()

    # provide multisig with ether
    DEPLOY_ACCT.transfer(addresses.DFX_MULTISIG, "2 ether", gas_price=gas_strategy)

    # Distribute rewards to the distributor contract
    dfx.approve(
        dfx_distributor,
        1_000_000_000 * 1e18,
        {"from": DFX_MULTISIG_ACCT, "gas_price": gas_strategy},
    )
    for gauge in contracts.gauges():
        dfx_distributor.passRewardToGauge(
            gauge,
            dfx,
            TOPUP_DFX_REWARDS,
            {"from": DFX_MULTISIG_ACCT, "gas_price": gas_strategy},
        )


if __name__ == "_main__":
    main()
