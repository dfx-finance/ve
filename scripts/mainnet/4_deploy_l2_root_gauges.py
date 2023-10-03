#!/usr/bin/env python
import json
import time

from brownie import DfxUpgradeableProxy, RootGaugeCcip

from fork.utils.account import DEPLOY_ACCT, DEPLOY_PROXY_ACCT
from utils.constants_addresses import Ethereum, Arbitrum, Polygon
from utils.helper import verify_deploy_address, verify_deploy_network
from utils.log import write_contract
from utils.network import network_info
from utils.ccip import ARBITRUM_CHAIN_SELECTOR, POLYGON_CHAIN_SELECTOR


DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18

connected = network_info()

output_data = {"gauges": {"rootGauge": {}}}


def deploy_implementation(verify_contracts=False) -> RootGaugeCcip:
    print(f"--- Deploying Root Gauge CCIP contract to {connected.name} ---")
    gauge_logic = RootGaugeCcip.deploy(
        Ethereum.DFX,  # source chain reward token
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )

    output_data["gauges"]["rootGauge"]["logic"] = gauge_logic.address
    return gauge_logic


def deploy_gauge(
    gauge_logic: RootGaugeCcip,
    gauge_name: str,
    destinationChainId: int,
    destinationAddr: str,
    label: str,
    verify_contracts=False,
):
    print(f"--- Deploying Root Gauge CCIP proxy contract to {connected.name} ---")
    # deploy gauge proxy and initialize
    gauge_initializer_calldata = gauge_logic.initialize.encode_input(
        gauge_name,
        DEPLOY_ACCT,  # source chain distributor address
        Ethereum.CCIP_ROUTER,  # source chain ccip router address
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
        publish_source=verify_contracts,
    )

    write_contract(label, proxy.address)
    output_data["gauges"]["rootGauge"][label] = {
        "calldata": gauge_initializer_calldata,
        "proxy": proxy.address,
    }


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

    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)

    verify_contracts = False if connected.is_local else True
    gauge_logic = deploy_implementation(verify_contracts)
    if not connected.is_local:
        print("Sleeping after deploy....")
        time.sleep(3)

    # deploy arbitrum root gauges
    deploy_gauge(
        gauge_logic,
        "Arbitrum CADC/USDC Root Gauge",
        ARBITRUM_CHAIN_SELECTOR,
        Arbitrum.CCIP_CADC_USDC_RECEIVER,
        "arbitrumCadcUsdcRootGauge",
        verify_contracts,
    )
    deploy_gauge(
        gauge_logic,
        "Arbitrum GYEN/USDC Root Gauge",
        ARBITRUM_CHAIN_SELECTOR,
        Arbitrum.CCIP_GYEN_USDC_RECEIVER,
        "arbitrumGyenUsdcRootGauge",
        verify_contracts,
    )

    # deploy polygon root gauges
    deploy_gauge(
        gauge_logic,
        "Polygon CADC/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        Polygon.CCIP_CADC_USDC_RECEIVER,
        "polygonCadcUsdcRootGauge",
        verify_contracts,
    )
    deploy_gauge(
        gauge_logic,
        "Polygon NGNC/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        Polygon.CCIP_NGNC_USDC_RECEIVER,
        "polygonNgncUsdcRootGauge",
        verify_contracts,
    )
    deploy_gauge(
        gauge_logic,
        "Polygon TRYB/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        Polygon.CCIP_TRYB_USDC_RECEIVER,
        "polygonTrybUsdcRootGauge",
        verify_contracts,
    )
    deploy_gauge(
        gauge_logic,
        "Polygon XSGD/USDC Root Gauge",
        POLYGON_CHAIN_SELECTOR,
        Polygon.CCIP_XSGD_USDC_RECEIVER,
        "polygonXsgdUsdcRootGauge",
        verify_contracts,
    )

    # output log
    if not connected.is_local:
        with open(
            f"./scripts/deployed_root_gauges_ccip_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
