#!/usr/bin/env python
from brownie import MigrationReceiver

from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network


existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


# deploy childchainreceiver
def deploy_receiver() -> MigrationReceiver:
    print(f"--- Deploying MigrationReceiver contract to {connected_network} ---")
    receiver = MigrationReceiver.deploy(
        existing.read_addr("ccipRouter"),
        existing.read_addr("chainSelectorEth"),
        existing.read_addr("ccipSenderEth"),
        existing.read_addr("multisig0"),
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )
    write_contract(INSTANCE_ID, "migrationReceiver", receiver.address)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. CCIP Router address\n"
            "\t2. Reward token address\n"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    deploy_receiver()
