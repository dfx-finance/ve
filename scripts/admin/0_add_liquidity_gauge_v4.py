#!/usr/bin/env python
import json
import time

from brownie import accounts, DfxUpgradeableProxy, LiquidityGaugeV4

from scripts import contracts
from scripts.helper import get_addresses, network_info, gas_strategy

addresses = get_addresses()
connected_network, is_local_network = network_info()

DEPLOY_ACCT = accounts[0] if is_local_network else accounts.load("deployve")
DEPLOY_PROXY_ACCT = (
    accounts[1] if is_local_network else accounts.load("deployve-proxyadmin")
)
DFX_MULTISIG_ACCT = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"
DFX_PROXY_MULTISIG_ACCT = "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c"

DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18


output_data = {"gauges": {"amm": {}}}


def main():
    should_verify = False if is_local_network else True

    veboost_proxy = contracts.veboost_proxy(addresses.VE_BOOST_PROXY)
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    label = "GBPT_USDC"
    lp_addr = addresses.DFX_GBPT_USDC_LP

    # connect to gauge logic
    gauge = LiquidityGaugeV4.at("0x71c0ddBF6da72a67C29529d6f67f97C00c4751D5")

    # deploy gauge behind proxy
    print(f"--- Deploying LiquidityGaugeV4 proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge.initialize.encode_input(
        lp_addr,
        DEPLOY_ACCT,
        addresses.DFX,
        addresses.VOTE_ESCROW,
        veboost_proxy.address,
        dfx_distributor.address,
    )
    dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
        gauge.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
        publish_source=should_verify,
    )
    output_data["gauges"]["amm"][label] = {
        "logic": gauge.address,
        "calldata": gauge_initializer_calldata,
        "proxy": dfx_upgradeable_proxy.address,
    }

    with open(
        f"./scripts/deployed_liquidity_{label}_gauge_v4_{int(time.time())}.json", "w"
    ) as output_f:
        json.dump(output_data, output_f, indent=4)
