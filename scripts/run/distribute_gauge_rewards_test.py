#!/usr/bin/env python
from brownie import accounts

from utils import contracts
from utils.account import DEPLOY_ACCT, impersonate
from utils.gauges import active_gauges
from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from utils.network import get_network_addresses

addresses = get_network_addresses()

admin = impersonate(addresses.DFX_MULTISIG_0)
TOPUP_DFX_REWARDS = 4674.6575342466 * 1e18  # 1,706,250.00 / (365/7) epochs / 7 gauges


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {"from": from_account, "gas_price": gas_strategy})
    print("Sender account DFX balance:", dfx.balanceOf(from_account) / 1e18)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. GaugeController address\n"
            "\t2. DfxDistributor address\n"
        )
    )
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)
    gauges = active_gauges(gauge_controller, dfx_distributor)

    # Distribute gauge rewards
    dfx_distributor.distributeRewardToMultipleGauges(
        gauges, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )

    # manual rewards
    dfx = contracts.load_dfx_token()

    # provide multisig with ether
    fund_multisigs(DEPLOY_ACCT)

    # Distribute rewards to the distributor contract
    dfx.approve(
        dfx_distributor,
        1_000_000_000 * 1e18,
        {"from": admin, "gas_price": gas_strategy},
    )
    for gauge in gauges:
        dfx_distributor.passRewardToGauge(
            gauge,
            dfx,
            TOPUP_DFX_REWARDS,
            {"from": admin, "gas_price": gas_strategy},
        )


if __name__ == "_main__":
    main()
