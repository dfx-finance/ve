#!/usr/bin/env python
from brownie import DfxUpgradeableProxy, CcipRootGauge
import time

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network, is_localhost

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def deploy_implementation() -> CcipRootGauge:
    print(f"--- Deploying Root Gauge CCIP contract to {connected_network} ---")
    gauge_logic = CcipRootGauge.deploy(
        existing.read_addr("DFX"),  # source chain reward token
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, "rootGaugeLogic", gauge_logic.address)
    return gauge_logic


def load_implementation() -> CcipRootGauge:
    print(f"--- Loading Root Gauge CCIP contract on {connected_network} ---")
    return CcipRootGauge.at(deployed.read_addr("rootGaugeLogic"))


def deploy_gauge(
    gauge_logic: CcipRootGauge,
    gauge_symbol: str,
    label: str,
):
    print(f"--- Deploying Root Gauge CCIP proxy contract to {connected_network} ---")
    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        f"Polygon {gauge_symbol.upper().replace('-', '/')}",
        gauge_symbol,
        DEPLOY_ACCT,  # source chain distributor address
        deployed.read_addr("ccipSender"),  # ccip sender address
        DEPLOY_ACCT,
    )

    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, label, proxy.address)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. DFX Mainnet address\n"
            "\t2. DfxDistributor address\n"
            "\t3. CCIP sender address\n"
        )
    )
    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    # gauge_logic = deploy_implementation()
    gauge_logic = load_implementation()
    # if not is_localhost:
    #     print("Sleeping after deploy....")
    #     time.sleep(3)

    # deploy polygon root gauges
    deploy_gauge(gauge_logic, "cadc-usdc", "polygonCadcUsdcRootGauge")
    deploy_gauge(gauge_logic, "ngnc-usdc", "polygonNgncUsdcRootGauge")
    deploy_gauge(gauge_logic, "tryb-usdc", "polygonTrybUsdcRootGauge")
    deploy_gauge(gauge_logic, "xsgd-usdc", "polygonXsgdUsdcRootGauge")
