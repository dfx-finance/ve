#!/usr/bin/env python
from brownie import DfxUpgradeableProxy, RootGaugeCcip
import time

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    POLYGON_CHAIN_SELECTOR,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network, is_localhost

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def deploy_implementation() -> RootGaugeCcip:
    print(f"--- Deploying Root Gauge CCIP contract to {connected_network} ---")
    gauge_logic = RootGaugeCcip.deploy(
        existing.read_addr("DFX"),  # source chain reward token
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, "rootGaugeLogic", gauge_logic.address)
    return gauge_logic


def load_implementation() -> RootGaugeCcip:
    print(f"--- Loading Root Gauge CCIP contract on {connected_network.name} ---")
    return RootGaugeCcip.at(deployed.read_addr("rootGaugeLogic"))


def deploy_gauge(
    gauge_logic: RootGaugeCcip,
    gauge_name: str,
    destinationChainId: int,
    destinationAddr: str,
    label: str,
):
    print(f"--- Deploying Root Gauge CCIP proxy contract to {connected_network} ---")
    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        gauge_name,
        DEPLOY_ACCT,  # source chain distributor address
        existing.read_addr("ccipRouter"),  # source chain ccip router address
        destinationChainId,  # target chain selector
        destinationAddr,  # child chain receiver address (l2 address)
        "0x0000000000000000000000000000000000000000",  # fee token address (zero address for native)
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
            "\t1. clDFX Mainnet address\n"
            "\t2. DfxDistributor address\n"
            "\t3. Chainlink selector for L2 chain\n"
            "\t4. CCIP receiver address on L2 chain\n"
            "\t5. Fee token address or zero address for native\n"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    gauge_logic = deploy_implementation()
    if not is_localhost:
        print("Sleeping after deploy....")
        time.sleep(3)

    # deploy polygon root gauges
    deploy_gauge(
        gauge_logic,
        "Polygon CADC/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        deployed.readAddr("ccipSender"),
        "polygonCadcUsdcRootGauge",
    )
    deploy_gauge(
        gauge_logic,
        "Polygon NGNC/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        deployed.readAddr("ccipSender"),
        "polygonNgncUsdcRootGauge",
    )
    deploy_gauge(
        gauge_logic,
        "Polygon TRYB/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        deployed.readAddr("ccipSender"),
        "polygonTrybUsdcRootGauge",
    )
    deploy_gauge(
        gauge_logic,
        "Polygon XSGD/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        deployed.readAddr("ccipSender"),
        "polygonXsgdUsdcRootGauge",
    )
