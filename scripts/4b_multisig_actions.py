#!/usr/bin/env python
from brownie import accounts

from scripts import contracts
from scripts.helper import gas_strategy, get_addresses, network_info

addresses = get_addresses()
connected_network, is_local_network = network_info()


DFX_MULTISIG_ACCT = accounts.at(
    "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF", force=True
)
DFX_PROXY_MULTISIG_ACCT = accounts.at(
    "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c", force=True
)
NEW_GAUGE_ADDRESSES = [
    ("CADC_USDC", "0xc6B407503dE64956Ad3cF5Ab112cA4f56AA13517"),
    ("EUROC_USDC", "0x3a622DB2db50f463dF562Dc5F341545A64C580fc"),
    ("GYEN_USDC", "0x6A47346e722937B60Df7a1149168c0E76DD6520f"),
    ("NZDS_USDC", "0x7A28cf37763279F774916b85b5ef8b64AB421f79"),
    ("TRYB_USDC", "0x2BB8B93F585B43b06F3d523bf30C203d3B6d4BD4"),
    ("XIDR_USDC", "0xB7ca895F81F20e05A5eb11B05Cbaab3DAe5e23cd"),
    ("XSGD_USDC", "0xd0EC100F1252a53322051a95CF05c32f0C174354"),
]


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

    add_to_gauge_controller(NEW_GAUGE_ADDRESSES)
    enable_distributions()


if __name__ == "__main__":
    main()
