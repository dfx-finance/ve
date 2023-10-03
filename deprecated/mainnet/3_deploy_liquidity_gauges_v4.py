#!/usr/bin/env python
import json
import time

from brownie import DfxUpgradeableProxy, LiquidityGaugeV4

from fork.utils.account import DEPLOY_ACCT, impersonate
from utils import contracts
from utils.gas import gas_strategy
from utils.helper import fund_multisigs, verify_gas_strategy
from utils.network import get_network_addresses, network_info

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18


output_data = {"gauges": {"amm": {}}}


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
    if not is_local_network:
        verify_gas_strategy()
    if is_local_network:
        fund_multisigs(DEPLOY_ACCT)

    should_verify = False if is_local_network else True

    veboost_proxy = contracts.veboost_proxy(addresses.VE_BOOST_PROXY)
    gauge_controller = contracts.gauge_controller(addresses.GAUGE_CONTROLLER)
    dfx_distributor = contracts.dfx_distributor(addresses.DFX_DISTRIBUTOR)

    print(f"--- Deploying Liquidity Gauges (v4) contract to {connected_network} ---")
    lp_addresses = [
        ("CADC_USDC", addresses.DFX_CADC_USDC_LP),
        ("EUROC_USDC", addresses.DFX_EUROC_USDC_LP),
        ("GYEN_USDC", addresses.DFX_GYEN_USDC_LP),
        ("NZDS_USDC", addresses.DFX_NZDS_USDC_LP),
        ("TRYB_USDC", addresses.DFX_TRYB_USDC_LP),
        ("XIDR_USDC", addresses.DFX_XIDR_USDC_LP),
        ("XSGD_USDC", addresses.DFX_XSGD_USDC_LP),
    ]

    # deploy gauge logic
    gauge = LiquidityGaugeV4.deploy({"from": DEPLOY_ACCT, "gas_price": gas_strategy})

    if not is_local_network:
        print("Sleeping after deploy....")
        time.sleep(10)

    # deploy gauge behind proxy
    for label, lp_addr in lp_addresses:
        print(
            f"--- Deploying LiquidityGaugeV4 proxy contract to {connected_network} ---"
        )
        gauge_initializer_calldata = gauge.initialize.encode_input(
            lp_addr,
            DEPLOY_ACCT,
            addresses.DFX,
            addresses.VEDFX,
            veboost_proxy.address,
            dfx_distributor.address,
        )
        dfx_upgradeable_proxy = DfxUpgradeableProxy.deploy(
            gauge.address,
            addresses.DFX_MULTISIG_1,
            gauge_initializer_calldata,
            {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
            publish_source=should_verify,
        )
        output_data["gauges"]["amm"][label] = {
            "logic": gauge.address,
            "calldata": gauge_initializer_calldata,
            "proxy": dfx_upgradeable_proxy.address,
        }
        if not is_local_network:
            # log gauge info
            with open(
                f"./scripts/deployed_liquidity_gauges_v4_{label}_{int(time.time())}.json",
                "w",
            ) as output_f:
                json.dump(output_data, output_f, indent=4)

            # grace period
            print("Sleeping after deploy....")
            time.sleep(3)

        print("--- Add gauge to GaugeController ---")
        admin = (
            impersonate(addresses.DFX_MULTISIG_0) if is_local_network else DEPLOY_ACCT
        )
        gauge_controller.add_gauge(
            dfx_upgradeable_proxy.address,
            DEFAULT_GAUGE_TYPE,
            DEFAULT_GAUGE_WEIGHT,
            {"from": admin, "gas_price": gas_strategy},
        )

    if not is_local_network:
        with open(
            f"./scripts/deployed_liquidity_gauges_v4_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
