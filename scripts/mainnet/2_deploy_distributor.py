#!/usr/bin/env python
import json
import time

from brownie import ZERO_ADDRESS, DfxDistributor, DfxUpgradeableProxy

from fork.utils.account import DEPLOY_ACCT
from utils import contracts
from utils.constants_addresses import Ethereum
from utils.helper import verify_deploy_address, verify_deploy_network
from utils.log import write_contract
from utils.network import network_info

REWARDS_RATE = 0
PREV_DISTRIBUTED_REWARDS = 0

connected = network_info()

output_data = {"distributor": {"logic": None, "proxy": None}}


def deploy(verify_contracts=False):
    gauge_controller = contracts.gauge_controller(Ethereum.GAUGE_CONTROLLER)

    print(f"--- Deploying Distributor contract to {connected.name} ---")
    dfx_distributor = DfxDistributor.deploy(
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    output_data["distributor"]["logic"] = dfx_distributor.address

    print(f"--- Deploying Distributor proxy contract to {connected.name} ---")
    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        Ethereum.DFX,
        gauge_controller.address,
        REWARDS_RATE,
        PREV_DISTRIBUTED_REWARDS,
        # needs another multisig to deal with access control behind proxy (ideally 2)
        Ethereum.DFX_MULTISIG_0,  # governor
        Ethereum.DFX_MULTISIG_0,  # guardian
        ZERO_ADDRESS,  # delegate gauge for pulling type 2 gauge rewards
    )
    dfx_upgradable_proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        Ethereum.DFX_MULTISIG_1,
        distributor_initializer_calldata,
        {"from": DEPLOY_ACCT},
        publish_source=verify_contracts,
    )
    output_data["distributor"]["proxy"] = dfx_upgradable_proxy.address

    write_contract("dfxDistributor", dfx_upgradable_proxy.address)
    if not connected.is_local:
        # Write output to file
        with open(
            f"./scripts/deployed_distributor_{int(time.time())}.json", "w"
        ) as output_f:
            json.dump(output_data, output_f, indent=4)


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

    verify_deploy_network(connected.name)
    verify_deploy_address(DEPLOY_ACCT)

    verify_contracts = False if connected.is_local else True
    deploy(verify_contracts)
