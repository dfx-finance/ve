#!/usr/bin/env python
from brownie import DfxUpgradeableProxy, CcipRootGauge
from brownie import network, web3

from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


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
        deployed.read_addr("dfxDistributor"),  # source chain distributor address
        deployed.read_addr("ccipSender"),  # ccip sender address
        existing.read_addr("multisig0"),
    )

    # print(DEPLOY_ACCT.balance() / 1e18)
    # print(network.web3.eth.gas_price / 1e9)
    # gas_estimate = DfxUpgradeableProxy.deploy.estimate_gas(
    #     gauge_logic.address,
    #     DEPLOY_PROXY_ACCT,
    #     gauge_initializer_calldata,
    #     {"from": DEPLOY_ACCT},
    # )

    # gas_price_gwei = (
    #     network.web3.eth.gas_price / 1e9
    # )  # Replace this with your actual gas price in Gwei

    # # Convert gas price to Wei
    # gas_price_wei = gas_price_gwei * 1e9
    # cost_wei = gas_estimate * gas_price_wei
    # cost_eth = cost_wei / 1e18

    # print(f"Gas Estimate: {gas_estimate}")
    # print(f"Gas Price (Gwei): {gas_price_gwei}")
    # print(f"Cost (Ether): {cost_eth}")

    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        existing.read_addr("multisig1"),
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

    gauge_logic = load_implementation()

    # deploy polygon root gauges
    deploy_gauge(gauge_logic, "paxg-usdc", "polygonPaxgUsdcRootGauge")
