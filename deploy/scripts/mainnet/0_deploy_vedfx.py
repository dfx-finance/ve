#!/usr/bin/env python
from brownie import VeDFX

from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)


def deploy():
    print(f"--- Deploying veDFX contract to {connected_network} ---")
    # vedfx_params = eth_abi.encode_abi(
    #     ["address", "string", "string", "string"],
    #     (Ethereum.DFX, "Vote-escrowed DFX", "veDFX", "veDFX_1.0.0"),
    # ).hex()
    vedfx = VeDFX.deploy(
        existing.read_addr("DFX"),
        "Vote-escrowed DFX",
        "veDFX",
        "veDFX_1.0.0",
        {"from": DEPLOY_ACCT},
    )

    write_contract(INSTANCE_ID, "veDFX", vedfx.address)


def main():
    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    deploy()
