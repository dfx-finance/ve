#!/usr/bin/env python
from brownie import accounts

from utils import contracts
from utils.network import get_network_addresses
from utils.gas import gas_strategy

DEPLOY_ACCT = accounts[0]


addresses = get_network_addresses()

gauge_addresses = [
    addresses.DFX_CADC_USDC_GAUGE,
    addresses.DFX_EUROC_USDC_GAUGE,
    addresses.DFX_GYEN_USDC_GAUGE,
    addresses.DFX_NZDS_USDC_GAUGE,
    addresses.DFX_TRYB_USDC_GAUGE,
    addresses.DFX_XIDR_USDC_GAUGE,
    addresses.DFX_XSGD_USDC_GAUGE,
]


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. DfxDistributor address\n"
        )
    )

    # provide multisig with ether
    DEPLOY_ACCT.transfer(addresses.DFX_MULTISIG, "5 ether", gas_price=gas_strategy)
    DFX_MULTISIG = accounts.at(address=addresses.DFX_MULTISIG, force=True)

    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    # get distribution period end time
    time_total = gauge_controller.time_total()

    # get total weight for distribution period
    total_weight = gauge_controller.points_total(time_total)
    print(f"Total weight at {time_total}: {total_weight}")

    for gauge_addr in gauge_addresses:
        gauge_controller.change_gauge_weight(
            gauge_addr,
            10e18,
            {"from": DFX_MULTISIG, "gas_price": gas_strategy},
        )

    gauge_controller.checkpoint({"from": DFX_MULTISIG, "gas_price": gas_strategy})
    total_weight = gauge_controller.points_total(time_total)
    print(f"Total weight at {time_total}: {total_weight}")


if __name__ == "_main__":
    main()
