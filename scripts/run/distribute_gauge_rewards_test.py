#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import get_addresses, gas_strategy, load_dfx_token

addresses = get_addresses()

DEPLOY_ACCT = accounts[0]
DFX_MULTISIG = accounts.at(address=addresses.DFX_MULTISIG, force=True)
TOPUP_DFX_REWARDS = 4674.6575342466 * 1e18  # 1,706,250.00 / (365/7) epochs / 7 gauges


def send_dfx(dfx, amount, from_account, to_account):
    dfx.transfer(to_account, amount, {"from": from_account, "gas_price": gas_strategy})
    print("Sender account DFX balance:", dfx.balanceOf(from_account) / 1e18)


# fetch all gauge addresses which are not flagged as a killedGauge
def active_gauges(gauge_controller, dfx_distributor):
    num_gauges = gauge_controller.n_gauges()
    all_gauge_addresses = [gauge_controller.gauges(i) for i in range(0, num_gauges)]
    gauge_addresses = []
    for addr in all_gauge_addresses:
        if dfx_distributor.killedGauges(addr) == False:
            gauge_addresses.append(addr)
    return gauge_addresses


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
    gauge_addresses = active_gauges(gauge_controller, dfx_distributor)

    print(gauge_addresses)
    print(len(gauge_addresses))

    # Distribute gauge rewards
    dfx_distributor.distributeRewardToMultipleGauges(
        gauge_addresses, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )

    # manual rewards
    dfx = load_dfx_token()

    # provide multisig with ether
    DEPLOY_ACCT.transfer(addresses.DFX_MULTISIG, "2 ether", gas_price=gas_strategy)

    # Distribute rewards to the distributor contract
    dfx.approve(
        dfx_distributor,
        1_000_000_000 * 1e18,
        {"from": DFX_MULTISIG, "gas_price": gas_strategy},
    )
    for addr in gauge_addresses:
        gauge = contracts.gauge(addr)
        dfx_distributor.passRewardToGauge(
            gauge,
            dfx,
            TOPUP_DFX_REWARDS,
            {"from": DFX_MULTISIG, "gas_price": gas_strategy},
        )


if __name__ == "_main__":
    main()
