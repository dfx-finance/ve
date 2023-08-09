#!/usr/bin/env python
from brownie import ZERO_ADDRESS, GaugeController, VeBoostProxy
import eth_abi
import json
import time

from fork.utils.account import DEPLOY_ACCT
from utils.gas import gas_strategy, verify_gas_strategy
from utils.network import get_network_addresses, network_info

DEFAULT_GAUGE_TYPE_NAME = "DFX AMM Liquidity"
DEFAULT_TYPE_WEIGHT = 1e18

addresses = get_network_addresses()
connected_network, is_local_network = network_info()

output_data = {
    "veBoostProxy": None,
    "veBoostProxyParams": None,
    "gaugeController": None,
    "gaugeControllerParams": None,
}


def main():
    print(
        (
            "Script 1 of 3:\n\n"
            "NOTE: This script expects configuration for:\n"
            "\t1. VotingEscrow (VeDFX) contract address"
        )
    )
    if not is_local_network:
        verify_gas_strategy()

    # 1. Deploy veBoostProxy
    print(f"--- Deploying VeBoostProxy contract to {connected_network} ---")
    # (votingEscrow address, delegation address, admin address)
    ve_boost_proxy_params = eth_abi.encode_abi(
        ["address", "address", "address"],
        (addresses.VEDFX, ZERO_ADDRESS, DEPLOY_ACCT.address),
    ).hex()
    ve_boost_proxy = VeBoostProxy.deploy(
        addresses.VEDFX,
        ZERO_ADDRESS,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
    )
    if not is_local_network:
        time.sleep(3)
    output_data["veBoostProxy"] = ve_boost_proxy.address
    output_data["veBoostProxyParams"] = ve_boost_proxy_params

    # 2. Deploy Gauge Controller
    print(f"--- Deploying Gauge Controller contract to {connected_network} ---")
    gauge_controller_params = eth_abi.encode_abi(
        ["address", "address", "address"],
        (addresses.DFX, addresses.VEDFX, DEPLOY_ACCT.address),
    ).hex()
    gauge_controller = GaugeController.deploy(
        addresses.DFX,
        addresses.VEDFX,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
    )
    if not is_local_network:
        time.sleep(3)
    output_data["gaugeController"] = gauge_controller.address
    output_data["gaugeControllerParams"] = gauge_controller_params

    # Output results
    print(
        f'--- Configure Gauge Controller with "{DEFAULT_GAUGE_TYPE_NAME}" type on {connected_network} ---'
    )
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME,
        DEFAULT_TYPE_WEIGHT,
        {"from": DEPLOY_ACCT, "gas_price": gas_strategy},
    )
    if not is_local_network:
        with open(
            f"./scripts/deployed_gaugecontroller_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)
