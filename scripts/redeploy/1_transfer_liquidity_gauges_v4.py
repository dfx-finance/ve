#!/usr/bin/env python
from brownie import accounts, interface

from scripts import contracts
from scripts.helper import gas_strategy, get_addresses, network_info

is_local_network = network_info()
addresses = get_addresses()

DEPLOY_ACCT = accounts[0] if is_local_network else accounts.load("deployve")
DEPLOY_PROXY_ACCT = (
    accounts[1] if is_local_network else accounts.load("deployve-proxyadmin")
)
DFX_MULTISIG_ACCT = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"
DFX_PROXY_MULTISIG_ACCT = "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c"

GAUGE_ADDRESSES = [
    ("CADC_USDC", addresses.DFX_CADC_USDC_GAUGE),
    ("EUROC_USDC", addresses.DFX_EUROC_USDC_GAUGE),
    ("GYEN_USDC", addresses.DFX_GYEN_USDC_GAUGE),
    ("NZDS_USDC", addresses.DFX_NZDS_USDC_GAUGE),
    ("TRYB_USDC", addresses.DFX_TRYB_USDC_GAUGE),
    ("XIDR_USDC", addresses.DFX_XIDR_USDC_GAUGE),
    ("XSGD_USDC", addresses.DFX_XSGD_USDC_GAUGE),
]


def transfer_all_liquidity_gauges(proxied_gauges):
    for gauge in proxied_gauges:
        gauge.commit_transfer_ownership(
            DFX_MULTISIG_ACCT, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
        )


def transfer_all_gauge_proxies(proxied_gauges):
    for gauge in proxied_gauges:
        upgradeable_proxy = interface.IDfxUpgradeableProxy(gauge.address)
        upgradeable_proxy.changeAdmin(
            DFX_PROXY_MULTISIG_ACCT,
            {"from": DEPLOY_PROXY_ACCT, "gas_price": gas_strategy},
        )
        print(
            f"{gauge.address} LiquidityGaugeV4 upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': DFX_PROXY_MULTISIG_ACCT}) == DFX_PROXY_MULTISIG_ACCT}"
        )


def main():
    new_gauges = [contracts.gauge(addr) for _, addr in GAUGE_ADDRESSES]

    # initiate transfer gauges to multisig
    transfer_all_liquidity_gauges(new_gauges)
    transfer_all_gauge_proxies(new_gauges)
