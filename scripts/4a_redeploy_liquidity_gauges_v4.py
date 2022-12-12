#!/usr/bin/env python
import time

from brownie import accounts, interface, DfxUpgradeableProxy

from scripts import contracts
from scripts.helper import get_addresses, network_info, write_log, gas_strategy

addresses = get_addresses()
connected_network, is_local_network = network_info()

DEPLOY_ACCT = accounts.load("hardhat")
DEPLOY_PROXY_ACCT = accounts[1]
DFX_MULTISIG_ACCT = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"
DFX_PROXY_MULTISIG_ACCT = "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c"
GAUGE_LOGIC_ADDRESS = "0x71c0ddBF6da72a67C29529d6f67f97C00c4751D5"
NEW_LP_ADDRESSES = [
    ("CADC_USDC", "0xF3d7AA346965656E7c65FB4135531e0C2270AF83"),
    ("EUROC_USDC", "0x477658494C3541ba272a7120176D77674a0183Ba"),
    ("GYEN_USDC", "0x63cB0F59B7E67c7d4Cb96214ca456597D85c587d"),
    ("NZDS_USDC", "0x764a5A29f982D3513e76fe07dF2034821fBdba72"),
    ("TRYB_USDC", "0xcF3c8f51DE189C8d5382713B716B133e485b99b7"),
    ("XIDR_USDC", "0x46161158b1947D9149E066d6d31AF1283b2d377C"),
    ("XSGD_USDC", "0x9A6C7aE10eB82A0d7dC3C296eCbc2E2bDC53E80B"),
]


def deploy_proxied_gauges(lp_addresses):
    # deploy gauge logic
    gauge_logic = contracts.gauge(GAUGE_LOGIC_ADDRESS)

    # deploy gauge behind proxy
    proxied_gauges = []
    output_data = {}
    for label, lp_addr in lp_addresses:
        print(f"--- Deploying LiquidityGaugeV4 proxy contract for {label} ---")
        gauge_initializer_calldata = gauge_logic.initialize.encode_input(
            lp_addr,
            DEPLOY_ACCT,
            addresses.DFX,
            addresses.VOTE_ESCROW,
            addresses.VE_BOOST_PROXY,
            addresses.DFX_DISTRIBUTOR,
        )
        dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
            gauge_logic.address,
            DEPLOY_PROXY_ACCT,
            gauge_initializer_calldata,
            {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
            publish_source=False,
        )
        proxied_gauges.append((label, dfx_upgradeable_proxy))

        # output for each gauge and create a full record at finish
        _data = {
            "logic": gauge_logic.address,
            "calldata": gauge_initializer_calldata,
            "proxy": dfx_upgradeable_proxy.address,
        }
        write_log(f"deployed_liquidity_gauges_v4_{label}", _data)
        output_data[label] = _data

        # sleep between deployments if using ethereum mainnet
        if not is_local_network:
            print("Sleeping after deploy....")
            time.sleep(3)
    write_log("deployed_liquidity_gauges_v4", output_data)
    return proxied_gauges


def transfer_all_liquidity_gauges(proxied_gauges):
    for _, p in proxied_gauges:
        gauge = contracts.gauge(p.address)
        gauge.commit_transfer_ownership(
            DFX_MULTISIG_ACCT, {"from": DEPLOY_ACCT, "gas_price": gas_strategy}
        )


def transfer_all_gauge_proxies(proxied_gauges):
    for _, p in proxied_gauges:
        upgradeable_proxy = interface.IDfxUpgradeableProxy(p.address)
        upgradeable_proxy.changeAdmin(
            DFX_PROXY_MULTISIG_ACCT,
            {"from": DEPLOY_PROXY_ACCT, "gas_price": gas_strategy},
        )
        print(
            f"{p.address} LiquidityGaugeV4 upgradeable proxy transfer success: {upgradeable_proxy.admin({'from': DFX_PROXY_MULTISIG_ACCT}) == DFX_PROXY_MULTISIG_ACCT}"
        )


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. Gauge logic\n"
            "\t2. DfxDistributor address\n"
            "\t3. GaugeController address"
        )
    )

    print(f"--- Deploying Liquidity Gauges (v4) contract to {connected_network} ---")
    new_gauges = deploy_proxied_gauges(NEW_LP_ADDRESSES)

    # initiate transfer gauges to multisig
    transfer_all_liquidity_gauges(new_gauges)
    transfer_all_gauge_proxies(new_gauges)
