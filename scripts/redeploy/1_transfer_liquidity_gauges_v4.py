#!/usr/bin/env python
import brownie

from utils import contracts
from utils.account import DEPLOY_ACCT, DEPLOY_PROXY_ACCT, impersonate
from utils.gas import gas_strategy
from utils.helper import fund_multisigs
from utils.network import get_network_addresses, network_info

_, is_local_network = network_info()
addresses = get_network_addresses()

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
    admin = impersonate(addresses.DFX_MULTISIG_0) if is_local_network else DEPLOY_ACCT

    for gauge in proxied_gauges:
        gauge.commit_transfer_ownership(
            addresses.DFX_MULTISIG_0, {"from": admin, "gas_price": gas_strategy}
        )


def transfer_all_gauge_proxies(proxied_gauges):
    proxy_admin = (
        impersonate(addresses.DFX_MULTISIG_1) if is_local_network else DEPLOY_PROXY_ACCT
    )

    for gauge in proxied_gauges:
        upgradeable_proxy = brownie.interface.IDfxUpgradeableProxy(gauge.address)
        upgradeable_proxy.changeAdmin(
            addresses.DFX_MULTISIG_1,
            {"from": proxy_admin, "gas_price": gas_strategy},
        )
        print(
            f"{gauge.address} LiquidityGaugeV4 upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': addresses.DFX_MULTISIG_1}) == addresses.DFX_MULTISIG_1}"
        )


def main():
    if is_local_network:
        fund_multisigs(DEPLOY_ACCT)

    new_gauges = [contracts.gauge(addr) for _, addr in GAUGE_ADDRESSES]

    # initiate transfer gauges to multisig
    transfer_all_liquidity_gauges(new_gauges)
    transfer_all_gauge_proxies(new_gauges)
