#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import get_addresses, network_info, gas_strategy

addresses = get_addresses()
connected_network, is_local_network = network_info()

DFX_MULTISIG_ACCT = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"


def main():
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)

    gauge = contracts.gauge(addresses.DFX_GBPT_USDC_GAUGE)
    gauge.accept_transfer_ownership(
        {"from": DFX_MULTISIG_ACCT, "gas_price": gas_strategy}
    )
    print(
        f"{gauge.name()} LiquidityGaugeV4 transfer success: {gauge.admin() == DFX_MULTISIG_ACCT}"
    )

    print("--- Add gauge to GaugeController ---")
    gauge_controller.add_gauge(
        addresses.DFX_GBPT_USDC_GAUGE,
        0,  # default type
        1e18,  # default weight
        {"from": DFX_MULTISIG_ACCT, "gas_price": gas_strategy},
    )