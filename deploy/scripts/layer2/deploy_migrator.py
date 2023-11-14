#!/usr/bin/env python
from brownie import Migrator

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
def deploy_migrator() -> Migrator:
    print(f"--- Deploying MigrationReceiver contract to {connected_network} ---")
    receiver = Migrator.deploy(
        existing.read_addr("bridgedDFX"),
        existing.read_addr("DFX"),
        {"from": DEPLOY_ACCT},
        publish_source=True,
    )
    write_contract(INSTANCE_ID, "migrator", receiver.address)


def main():
    print(
        (
            "NOTE: This script expects configuration for:\n"
            "\t1. Bridged DFX address\n"
            "\t2. CCIP DFX address\n"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    deploy_migrator()
