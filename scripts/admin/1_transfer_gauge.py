#!/usr/bin/env python
from brownie import accounts, interface

from utils import contracts
from utils.gas import gas_strategy
from utils.network import get_network_addresses, network_info
from utils.account import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    DFX_MULTISIG_ACCT,
    DFX_PROXY_MULTISIG_ACCT,
)

addresses = get_network_addresses()
connected_network, is_local_network = network_info()


DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18


output_data = {"gauges": {"amm": {}}}


def transfer_liquidity_gauge(gauge_addr):
    gauge = contracts.gauge(gauge_addr)

    gauge.commit_transfer_ownership(
        DFX_MULTISIG_ACCT, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
    )


def transfer_gauge_proxy(gauge_addr):
    upgradeable_proxy = interface.IDfxUpgradeableProxy(gauge_addr)
    upgradeable_proxy.changeAdmin(
        DFX_PROXY_MULTISIG_ACCT,
        {"from": DEPLOY_PROXY_ACCT, "gas_price": gas_strategy},
    )
    print(
        f"{gauge_addr} LiquidityGaugeV4 upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': DFX_PROXY_MULTISIG_ACCT}) == DFX_PROXY_MULTISIG_ACCT}"
    )


def main():
    gauge_addr = addresses.DFX_GBPT_USDC_GAUGE

    print(f"Transfering liquidity gauge to {DFX_MULTISIG_ACCT}...")
    transfer_liquidity_gauge(gauge_addr)
    print(f"Transfering liquidity gauge proxy admin to {DFX_PROXY_MULTISIG_ACCT}...")
    transfer_gauge_proxy(gauge_addr)

    print("Complete!")
