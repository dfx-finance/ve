#!/usr/bin/env python
from brownie import Contract, DfxUpgradeableProxy, LiquidityGaugeV4
import time

from utils.contracts import (
    dfx_distributor as _dfx_distributor,
    veboost_proxy as _veboost_proxy,
)
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
def deploy_implementation(verify_contracts=False):
    print(f"--- Deploying Liquidity Gauges (v4) contract to {connected_network} ---")
    gauge_logic = LiquidityGaugeV4.deploy(
        {"from": DEPLOY_ACCT}, publish_source=verify_contracts
    )
    return gauge_logic


# deploy gauge as proxy
def deploy_gauge(
    gauge_logic: LiquidityGaugeV4, lpt: str, label: str
) -> LiquidityGaugeV4:
    veboost_proxy = _veboost_proxy(deployed.read_addr("veBoostProxy"))
    dfx_distributor = _dfx_distributor(deployed.read_addr("dfxDistributor"))

    # deploy gauge behind proxy
    print(f"--- Deploying LiquidityGaugeV4 proxy contract to {connected_network} ---")
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        lpt,
        DEPLOY_ACCT,
        existing.read_addr("DFX"),
        existing.read_addr("veDFX"),
        veboost_proxy.address,
        dfx_distributor.address,
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        DEPLOY_PROXY_ACCT,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, f"{label}Gauge", proxy.address)
    return Contract.from_abi("LiquidityGaugeV4", proxy.address, LiquidityGaugeV4.abi)


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

    gauge_logic = deploy_implementation()
    if not is_localhost:
        print("Sleeping after deploy....")
        time.sleep(3)

    deploy_gauge(gauge_logic, "cadcUsdc")
    deploy_gauge(gauge_logic, "eurcUsdc")
    deploy_gauge(gauge_logic, "gbptUsdc")
    deploy_gauge(gauge_logic, "gyenUsdc")
    # deploy_gauge(gauge_logic, "nzdsUsdc")
    deploy_gauge(gauge_logic, "trybUsdc")
    deploy_gauge(gauge_logic, "xidrUsdc")
    deploy_gauge(gauge_logic, "xsgdUsdc")
