#!/usr/bin/env python
from brownie import ZERO_ADDRESS, DfxDistributor, DfxUpgradeableProxy

from utils.contracts import gauge_controller as _gauge_controller
from utils.config import (
    DEPLOY_ACCT,
    DEPLOY_PROXY_ACCT,
    INSTANCE_ID,
    REWARDS_RATE,
    PREV_DISTRIBUTED_REWARDS,
    VERIFY_CONTRACTS,
    verify_deploy_address,
    verify_deploy_network,
)
from utils.logger import load_inputs, load_outputs, write_contract
from utils.network import connected_network

existing = load_inputs(INSTANCE_ID)
deployed = load_outputs(INSTANCE_ID)


def deploy():
    print(f"--- Deploying Distributor contract to {connected_network} ---")
    dfx_distributor_logic = DfxDistributor.deploy(
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, "dfxDistributorLogic", dfx_distributor_logic.address)

    print(f"--- Deploying Distributor proxy contract to {connected_network} ---")
    distributor_initializer_calldata = dfx_distributor_logic.initialize.encode_input(
        existing.read_addr("DFX"),
        deployed.read_addr("gaugeController"),
        REWARDS_RATE,
        PREV_DISTRIBUTED_REWARDS,
        # needs another multisig to deal with access control behind proxy (ideally 2)
        existing.read_addr("multisig0"),  # governor
        existing.read_addr("multisig0"),  # guardian
        ZERO_ADDRESS,  # delegate gauge for pulling type 2 gauge rewards
    )
    proxy = DfxUpgradeableProxy.deploy(
        deployed.read_addr("dfxDistributorLogic"),
        DEPLOY_PROXY_ACCT,
        distributor_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=VERIFY_CONTRACTS,
    )
    write_contract(INSTANCE_ID, "dfxDistributor", proxy.address)


def main():
    print(
        (
            "Script 2 of 3:\n\n"
            "NOTE: This script expects configuration for:\n"
            "\t1. GaugeController address\n"
            "\t2. DFX token rewards per second\n"
            "\t3. Total amount of previously distributed rewards\n"
            "\t4. Governor and Guardian addresses"
        )
    )

    verify_deploy_network(connected_network)
    verify_deploy_address(DEPLOY_ACCT)
    deploy()
