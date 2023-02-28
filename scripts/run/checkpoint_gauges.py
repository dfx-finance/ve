#!/usr/bin/env python
from brownie import accounts, chain
from brownie.network import gas_price

from datetime import datetime, timezone

from scripts import contracts
from scripts.helper import gas_strategy, get_addresses
from utils.constants import WEEK


addresses = get_addresses()
gas_price(gas_strategy)

DEPLOY_ACCT = accounts[0]


def main():
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    gauge_addresses = [
        addresses.DFX_CADC_USDC_GAUGE,
        addresses.DFX_EUROC_USDC_GAUGE,
        addresses.DFX_GYEN_USDC_GAUGE,
        addresses.DFX_NZDS_USDC_GAUGE,
        addresses.DFX_TRYB_USDC_GAUGE,
        addresses.DFX_XIDR_USDC_GAUGE,
        addresses.DFX_XSGD_USDC_GAUGE,
    ]

    for addr in gauge_addresses:
        tx = gauge_controller.gauge_relative_weight_write(
            addr, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
        )
        print(tx.value)


if __name__ == "__main__":
    main()
