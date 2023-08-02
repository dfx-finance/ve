#!/usr/bin/env python
from brownie import accounts

from utils import contracts
from utils.gas import gas_strategy
from utils.network import get_network_addresses

HARDHAT_ACCT = accounts.load("hardhat")
DEPLOY_ACCT = accounts.load("deployve")
addresses = get_network_addresses()


def main():
    # provide multisig with ether
    HARDHAT_ACCT.transfer(DEPLOY_ACCT, "2 ether", gas_price=gas_strategy)

    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    gauge_addresses = [
        ("CADC_USDC", addresses.DFX_CADC_USDC_GAUGE),
        ("EUROC_USDC", addresses.DFX_EUROC_USDC_GAUGE),
        ("EURS_USDC", addresses.DFX_EURS_USDC_GAUGE),
        ("NZDS_USDC", addresses.DFX_NZDS_USDC_GAUGE),
        ("TRYB_USDC", addresses.DFX_TRYB_USDC_GAUGE),
        ("XIDR_USDC", addresses.DFX_XIDR_USDC_GAUGE),
        ("XSGD_USDC", addresses.DFX_XSGD_USDC_GAUGE),
    ]
    for label, gauge_addr in gauge_addresses:
        dfx_distributor.toggleGauge(
            gauge_addr, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
        )
        print(f"{label} gauge is killed: {dfx_distributor.killedGauges(gauge_addr)}")


if __name__ == "__main__":
    main()
