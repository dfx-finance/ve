#!/usr/bin/env python
from brownie import Contract, DfxUpgradeableProxy, LiquidityGaugeV4
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


# deploy gauge logic
def deploy_implementation():
    print(
        f"--- Deploying LiquidityGaugeV4 implementation contract to {connected_network} ---"
    )
    gauge_logic = LiquidityGaugeV4.deploy({"from": DEPLOY_ACCT})
    write_contract(INSTANCE_ID, "liquidityGaugeV4Logic", gauge_logic.address)
    return gauge_logic


def load_implementation():
    print(
        f"--- Loading LiquidityGaugeV4 implementation contract on {connected_network} ---"
    )
    gauge_logic = LiquidityGaugeV4.at(deployed.read_addr("liquidityGaugeV4Logic"))
    return gauge_logic


# deploy gauge as proxy
def deploy_gauge(gauge_logic: LiquidityGaugeV4, label: str) -> LiquidityGaugeV4:
    # deploy gauge behind proxy
    print(f"--- Deploying LiquidityGaugeV4 proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        existing.read_addr(f"{label}Lpt"),
        existing.read_addr("multisig0"),
        existing.read_addr("DFX"),
        existing.read_addr("veDFX"),
        deployed.read_addr("veBoostProxy"),
        deployed.read_addr("dfxDistributor"),
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        # publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, f"{label}Gauge", proxy.address)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. VeBoostProxy address\n"
            "\t2. DfxDistributor address\n"
            "\t3. GaugeController address"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    # gauge_logic = deploy_implementation()
    # if not is_localhost:
    #     print("Sleeping after deploy....")
    #     time.sleep(3)
    gauge_logic = load_implementation()

    deploy_gauge(gauge_logic, "cadcUsdc")
    deploy_gauge(gauge_logic, "eurcUsdc")
    deploy_gauge(gauge_logic, "gbptUsdc")
    deploy_gauge(gauge_logic, "gyenUsdc")
    deploy_gauge(gauge_logic, "nzdsUsdc")
    deploy_gauge(gauge_logic, "trybUsdc")
    deploy_gauge(gauge_logic, "xidrUsdc")
    deploy_gauge(gauge_logic, "xsgdUsdc")
