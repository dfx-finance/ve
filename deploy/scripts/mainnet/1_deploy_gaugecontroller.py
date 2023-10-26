#!/usr/bin/env python
from brownie import ZERO_ADDRESS, GaugeController, VeBoostProxy
import time

from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    DEFAULT_GAUGE_TYPE_NAME,
    DEFAULT_GAUGE_TYPE_WEIGHT,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network, is_localhost

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def deploy():
    # 1. Deploy veBoostProxy
    print(f"--- Deploying VeBoostProxy contract to {connected_network} ---")
    # # (votingEscrow address, delegation address, admin address)
    # VEBOOST_PROXY_params = eth_abi.encode_abi(
    #     ["address", "address", "address"],
    #     (Ethereum.VEDFX, ZERO_ADDRESS, DEPLOY_ACCT.address),
    # ).hex()
    VEBOOST_PROXY = VeBoostProxy.deploy(
        existing.read_addr("veDFX"),
        ZERO_ADDRESS,
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
    )
    write_contract(INSTANCE_ID, "veBoostProxy", VEBOOST_PROXY.address)

    # 2. Deploy Gauge Controller
    if not is_localhost:
        time.sleep(3)
    print(f"--- Deploying Gauge Controller contract to {connected_network} ---")
    # gauge_controller_params = eth_abi.encode_abi(
    #     ["address", "address", "address"],
    #     (Ethereum.DFX, Ethereum.VEDFX, DEPLOY_ACCT.address),
    # ).hex()
    gauge_controller = GaugeController.deploy(
        existing.read_addr("DFX"),
        existing.read_addr("veDFX"),
        DEPLOY_ACCT,
        {"from": DEPLOY_ACCT},
    )
    write_contract(INSTANCE_ID, "gaugeController", gauge_controller.address)

    # 3. Configure GaugeController with defaultmtype
    if not is_localhost:
        time.sleep(3)
    print(
        f'--- Configure Gauge Controller with "{DEFAULT_GAUGE_TYPE_NAME}" type on {connected_network} ---'
    )
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME,
        DEFAULT_GAUGE_TYPE_WEIGHT,
        {"from": DEPLOY_ACCT},
    )


def main():
    print(
        (
            "Script 1 of 3:\n\n"
            "NOTE: This script expects configuration for:\n"
            "\t1. VotingEscrow (VeDFX) contract address"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)
    deploy()
