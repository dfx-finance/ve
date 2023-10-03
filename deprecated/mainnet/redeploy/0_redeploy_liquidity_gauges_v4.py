#!/usr/bin/env python
import os
import time

from brownie import DfxUpgradeableProxy

from fork.utils.account import DEPLOY_ACCT, DEPLOY_PROXY_ACCT
from utils import contracts
from utils.gas import gas_strategy
from utils.helper import verify_gas_strategy
from utils.log import write_json_log
from utils.network import get_network_addresses, network_info


addresses = get_network_addresses()
connected_network, is_local_network = network_info()


LP_ADDRESSES = [
    ("CADC_USDC", addresses.DFX_CADC_USDC_LP),
    ("EUROC_USDC", addresses.DFX_EUROC_USDC_LP),
    ("GYEN_USDC", addresses.DFX_GYEN_USDC_LP),
    ("NZDS_USDC", addresses.DFX_NZDS_USDC_LP),
    ("TRYB_USDC", addresses.DFX_TRYB_USDC_LP),
    ("XIDR_USDC", addresses.DFX_XIDR_USDC_LP),
    ("XSGD_USDC", addresses.DFX_XSGD_USDC_LP),
]


def deploy_proxied_gauges(lp_addresses):
    # deploy gauge logic
    gauge_logic = contracts.gauge(addresses.GAUGE_LOGIC)

    # deploy gauge behind proxy
    proxied_gauges = []
    output_data = {}
    log_fps = []
    for label, lp_addr in lp_addresses:
        print(f"--- Deploying LiquidityGaugeV4 proxy contract for {label} ---")
        gauge_initializer_calldata = gauge_logic.initialize.encode_input(
            lp_addr,
            DEPLOY_ACCT,
            addresses.DFX,
            addresses.VEDFX,
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
        if not is_local_network:
            log_fp = write_json_log(f"deployed_liquidity_gauges_v4_{label}", _data)
            log_fps.append(log_fp)
        output_data[label] = _data

        # sleep between deployments if using ethereum mainnet
        if not is_local_network:
            print("Sleeping after deploy....")
            time.sleep(3)

    if not is_local_network:
        write_json_log("redeployed_liquidity_gauges_v4", output_data)
        for fp in log_fps:
            os.remove(fp)
    return proxied_gauges


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. Gauge logic\n"
            "\t2. DfxDistributor address\n"
        )
    )

    if not is_local_network:
        verify_gas_strategy()

    print(f"--- Deploying Liquidity Gauges (v4) contracts to {connected_network} ---")
    deploy_proxied_gauges(LP_ADDRESSES)
