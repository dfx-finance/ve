#!/usr/bin/env python
from utils import contracts
from utils.account import DEPLOY_ACCT, impersonate
from utils.gauges import active_gauges
from utils.helper import fund_multisigs
from utils.network import get_network_addresses
from utils.gas import gas_strategy


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
    fund_multisigs(DEPLOY_ACCT)
    admin = impersonate(addresses.DFX_MULTISIG_0)

    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    # get distribution period end time
    time_total = gauge_controller.time_total()

    # get total weight for distribution period
    total_weight = gauge_controller.points_total(time_total)
    print(f"Total weight at {time_total}: {total_weight}")

    for gauge_addr in gauge_addresses:
        if gauge_addr == "0x45C38b5126eB70e8B0A2c2e9FE934625641bF063":
            print("skipping NZDS/USDC gauge (method broken?)...\n\n")
            continue
        gauge_controller.change_gauge_weight(
            gauge_addr,
            1e18,
            {"from": admin, "gas_price": gas_strategy},
        )

    gauge_controller.checkpoint({"from": admin, "gas_price": gas_strategy})
    total_weight = gauge_controller.points_total(time_total)
    print(f"Total weight at {time_total}: {total_weight}")


if __name__ == "_main__":
    main()
