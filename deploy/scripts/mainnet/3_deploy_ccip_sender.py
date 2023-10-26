#!/usr/bin/env python
from brownie import CcipSender, DfxUpgradeableProxy

from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def deploy():
    print(f"--- Deploying CCIP Sender contract to {connected_network} ---")
    ccip_sender_logic = CcipSender.deploy(
        existing.read_addr("DFX"),
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )

    print(f"--- Deploying CCIP Sender proxy contract to {connected_network} ---")
    distributor_initializer_calldata = ccip_sender_logic.initialize.encode_input(
        existing.read_addr("ccipRouter"),
        DEPLOY_ACCT,
    )
    proxy = DfxUpgradeableProxy.deploy(
        ccip_sender_logic.address,
        DEPLOY_PROXY_ACCT,
        distributor_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )

    write_contract(INSTANCE_ID, "ccipSenderLogic", ccip_sender_logic.address)
    write_contract(INSTANCE_ID, "ccipSender", proxy.address)


def main():
    print(
        (
            "Script 3 of 3:\n\n"
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)
    deploy()
