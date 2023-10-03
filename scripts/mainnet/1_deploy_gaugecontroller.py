#!/usr/bin/env python
from brownie import ZERO_ADDRESS, GaugeController, VeBoostProxy
import eth_abi
import json
import time

from fork.utils.account import DEPLOY_ACCT
from utils.constants_addresses import Ethereum
from utils.helper import (
    verify_deploy_address,
    verify_deploy_network,
)
from utils.log import write_contract
from utils.network import network_info

DEFAULT_GAUGE_TYPE_NAME = "DFX LP Ethereum Gauge"
DEFAULT_TYPE_WEIGHT = 1e18

connected = network_info()

output_data = {
    "veBoostProxy": None,
    "veBoostProxyParams": None,
    "gaugeController": None,
    "gaugeControllerParams": None,
}


def deploy():
    # 1. Deploy veBoostProxy
    print(f"--- Deploying VeBoostProxy contract to {connected.name} ---")
    # (votingEscrow address, delegation address, admin address)
    ve_boost_proxy_params = eth_abi.encode_abi(
        ["address", "address", "address"],
        (Ethereum.VEDFX, ZERO_ADDRESS, DEPLOY_ACCT.address),
    ).hex()
    ve_boost_proxy = VeBoostProxy.deploy(
        Ethereum.VEDFX,
        ZERO_ADDRESS,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
    )
    if not connected.is_local:
        time.sleep(3)
    output_data["veBoostProxy"] = ve_boost_proxy.address
    output_data["veBoostProxyParams"] = ve_boost_proxy_params
    write_contract("veBoostProxy", ve_boost_proxy.address)

    # 2. Deploy Gauge Controller
    print(f"--- Deploying Gauge Controller contract to {connected.name} ---")
    gauge_controller_params = eth_abi.encode_abi(
        ["address", "address", "address"],
        (Ethereum.DFX, Ethereum.VEDFX, DEPLOY_ACCT.address),
    ).hex()
    gauge_controller = GaugeController.deploy(
        Ethereum.DFX,
        Ethereum.VEDFX,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
    )
    if not connected.is_local:
        time.sleep(3)
    output_data["gaugeController"] = gauge_controller.address
    output_data["gaugeControllerParams"] = gauge_controller_params
    write_contract("gaugeController", ve_boost_proxy.address)

    # Output results
    print(
        f'--- Configure Gauge Controller with "{DEFAULT_GAUGE_TYPE_NAME}" type on {connected.name} ---'
    )
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME,
        DEFAULT_TYPE_WEIGHT,
        {"from": DEPLOY_ACCT},
    )
    if not connected.is_local:
        with open(
            f"./scripts/deployed_gaugecontroller_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)


def main():
    print(
        (
            "Script 1 of 3:\n\n"
            "NOTE: This script expects configuration for:\n"
            "\t1. VotingEscrow (VeDFX) contract address"
        )
    )

    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)
    deploy()
