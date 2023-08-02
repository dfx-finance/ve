#!/usr/bin/env python
from brownie import accounts

from utils import contracts
from utils.gas import gas_strategy
from utils.network import get_network_addresses

DEPLOY_ACCT = accounts[0]


addresses = get_network_addresses()


# fetch all gauge addresses which are not flagged as a killedGauge
def active_gauges(gauge_controller, dfx_distributor):
    num_gauges = gauge_controller.n_gauges()
    all_gauge_addresses = [gauge_controller.gauges(i) for i in range(0, num_gauges)]
    gauge_addresses = []
    for addr in all_gauge_addresses:
        print(addr, dfx_distributor.killedGauges(addr))
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

    # Distribute gauge rewards
    dfx_distributor.distributeRewardToMultipleGauges(
        gauge_addresses, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )


if __name__ == "_main__":
    main()
