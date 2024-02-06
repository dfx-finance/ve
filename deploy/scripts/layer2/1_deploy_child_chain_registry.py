#!/usr/bin/env python
from brownie import ChildChainRegistry
from utils.network import connected_network

from utils.logger import write_contract
from utils.config import (
    DEPLOY_ACCT,
    INSTANCE_ID,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)


def deploy_registry():
    print(f"--- Deploying ChildChainRegistry contract to {connected_network} ---")
    registry = ChildChainRegistry.deploy(
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, "gaugeRegistry", registry.address)


def main():
    print(("NOTE: This script expects configuration for:\n" "\t1. ---\n"))
    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)

    deploy_registry()
