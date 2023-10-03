#!/usr/bin/env python
import json
import time

from brownie import Contract, DfxUpgradeableProxy, LiquidityGaugeV4

from fork.utils.account import DEPLOY_ACCT, impersonate
from utils import contracts
from utils.constants_addresses import Ethereum, EthereumLocalhost
from utils.helper import verify_deploy_address, verify_deploy_network
from utils.log import write_contract
from utils.network import network_info

connected = network_info()
# override addresses when running on local fork
Ethereum = EthereumLocalhost if connected.is_local else Ethereum

DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18

output_data = {"gauges": {"amm": {}}}


# deploy gauge logic
def deploy_implementation(verify_contracts=False):
    print(f"--- Deploying Liquidity Gauges (v4) contract to {connected.name} ---")
    gauge_logic = LiquidityGaugeV4.deploy(
        {"from": DEPLOY_ACCT}, publish_source=verify_contracts
    )
    return gauge_logic


# deploy gauge as proxy
def deploy_gauge(
    gauge_logic: LiquidityGaugeV4, lpt: str, label: str, verify_contracts=False
) -> LiquidityGaugeV4:
    veboost_proxy = contracts.veboost_proxy(Ethereum.VEBOOST_PROXY)
    dfx_distributor = contracts.dfx_distributor(Ethereum.DFX_DISTRIBUTOR)

    # deploy gauge behind proxy
    print(f"--- Deploying LiquidityGaugeV4 proxy contract to {connected.name} ---")
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        lpt,
        DEPLOY_ACCT,
        Ethereum.DFX,
        Ethereum.VEDFX,
        veboost_proxy.address,
        dfx_distributor.address,
    )
    proxy = DfxUpgradeableProxy.deploy(
        gauge_logic.address,
        Ethereum.DFX_MULTISIG_1,
        gauge_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    output_data["gauges"]["amm"][label] = {
        "logic": gauge_logic.address,
        "calldata": gauge_initializer_calldata,
        "proxy": proxy.address,
    }
    write_contract(f"{label}Gauge", proxy.address)
    return Contract.from_abi("LiquidityGaugeV4", proxy.address, LiquidityGaugeV4.abi)


def add_to_gauge_controller(gauge: LiquidityGaugeV4):
    gauge_controller = contracts.gauge_controller(Ethereum.GAUGE_CONTROLLER)

    print("--- Add gauge to GaugeController ---")
    admin = impersonate(Ethereum.DFX_MULTISIG_0) if connected.is_local else DEPLOY_ACCT
    gauge_controller.add_gauge(
        gauge.address,
        DEFAULT_GAUGE_TYPE,
        DEFAULT_GAUGE_WEIGHT,
        {"from": admin},
    )


def main():
    print(
        (
            "Script 3 of 3:\n\n"
            "NOTE: This script expects configuration for:\n"
            "\t1. VeBoostProxy address\n"
            "\t2. DfxDistributor address\n"
            "\t3. GaugeController address"
        )
    )

    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)

    verify_contracts = False if connected.is_local else True
    gauge_logic = deploy_implementation(verify_contracts)
    if not connected.is_local:
        print("Sleeping after deploy....")
        time.sleep(3)

    deploy_gauge(gauge_logic, Ethereum.DFX_CADC_USDC_LP, "cadcUsdc", verify_contracts)
    deploy_gauge(gauge_logic, Ethereum.DFX_EURC_USDC_LP, "eurcUsdc", verify_contracts)
    deploy_gauge(gauge_logic, Ethereum.DFX_GBPT_USDC_LP, "gbptUsdc", verify_contracts)
    deploy_gauge(gauge_logic, Ethereum.DFX_GYEN_USDC_LP, "gyenUsdc", verify_contracts)
    deploy_gauge(gauge_logic, Ethereum.DFX_NZDS_USDC_LP, "nzdsUsdc", verify_contracts)
    deploy_gauge(gauge_logic, Ethereum.DFX_TRYB_USDC_LP, "trybUsdc", verify_contracts)
    deploy_gauge(gauge_logic, Ethereum.DFX_XIDR_USDC_LP, "xidrUsdc", verify_contracts)
    deploy_gauge(gauge_logic, Ethereum.DFX_XSGD_USDC_LP, "xsgdUsdc", verify_contracts)

    if not connected.is_local:
        with open(
            f"./scripts/deployed_liquidity_gauges_v4_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
