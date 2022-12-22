#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import gas_strategy, get_addresses, network_info

addresses = get_addresses()
connected_network, is_local_network = network_info()


DFX_MULTISIG_ACCT = accounts.at(
    "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF", force=True
)
GAUGE_ADDRESSES = [
    ("CADC_USDC", addresses.DFX_CADC_USDC_GAUGE),
    ("EUROC_USDC", addresses.DFX_EUROC_USDC_GAUGE),
    ("GYEN_USDC", addresses.DFX_GYEN_USDC_GAUGE),
    ("NZDS_USDC", addresses.DFX_NZDS_USDC_GAUGE),
    ("TRYB_USDC", addresses.DFX_TRYB_USDC_GAUGE),
    ("XIDR_USDC", addresses.DFX_XIDR_USDC_GAUGE),
    ("XSGD_USDC", addresses.DFX_XSGD_USDC_GAUGE),
]


def accept_liqudity_gauge_v4_transfer(proxied_gauges):
    for _, gauge_addr in proxied_gauges:
        gauge = contracts.gauge(gauge_addr)
        gauge.accept_transfer_ownership(
            {"from": DFX_MULTISIG_ACCT, "gas_price": gas_strategy}
        )
        print(
            f"{gauge.name()} LiquidityGaugeV4 transfer success: {gauge.admin() == DFX_MULTISIG_ACCT}"
        )


def add_to_gauge_controller(gauge_addresses):
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    default_gauge_type = 0
    default_gauge_weight = 1e18
    for label, gauge_addr in gauge_addresses:
        print(f"--- Adding {label} LiquidityGaugeV4 to GaugeController ---")
        gauge_controller.add_gauge(
            gauge_addr,
            default_gauge_type,
            default_gauge_weight,
            {"from": DFX_MULTISIG_ACCT, "gas_price": gas_strategy},
        )


def enable_distributions():
    print("--- Enabling Gauge Distributions -------------------------")
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    if not dfx_distributor.distributionsOn():
        dfx_distributor.toggleDistributions(
            {"from": DFX_MULTISIG_ACCT, "gas_price": gas_strategy}
        )
        print(f"DFX distributions are enabled: {dfx_distributor.distributionsOn()}")
    else:
        print("DFX distribtions already enabled, skipping...")
    print("")


def main():
    # provide multisig with ether
    if is_local_network:
        accounts[0].transfer(DFX_MULTISIG_ACCT, "2 ether", gas_price=gas_strategy)

    accept_liqudity_gauge_v4_transfer(GAUGE_ADDRESSES)
    add_to_gauge_controller(GAUGE_ADDRESSES)
    enable_distributions()
