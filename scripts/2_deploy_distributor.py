#!/usr/bin/env python
import json
import time

from brownie import ZERO_ADDRESS, DfxDistributor, DfxUpgradeableProxy, accounts

from scripts import contracts
from scripts.helper import get_addresses, network_info, gas_strategy

REWARDS_RATE = 0
PREV_DISTRIBUTED_REWARDS = 0

DEPLOY_ACCT = accounts.load('hardhat')
PROXY_MULTISIG = accounts[7]
# DEPLOY_ACCT = accounts.load('deployve')
# PROXY_MULTISIG = accounts.load('deployve-proxyadmin')
GOVERNOR_MULTISIG = DEPLOY_ACCT
GUARDIAN_MULTISIG = DEPLOY_ACCT

addresses = get_addresses()
connected_network, is_local_network = network_info()

output_data = {'distributor': {'logic': None, 'proxy': None}}


def main():
    print((
        'Script 2 of 3:\n\n'
        'NOTE: This script expects configuration for:\n'
        '\t1. GaugeController address\n'
        '\t2. DFX token rewards per second\n'
        '\t3. Total amount of previously distributed rewards\n'
        '\t4. Governor and Guardian addresses'
    ))
    should_verify = not is_local_network
    should_verify = False

    gauge_controller = contracts.gauge_controller()

    print(f'--- Deploying Distributor contract to {connected_network} ---')
    dfx_distributor = DfxDistributor.deploy(
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy}, publish_source=should_verify)
    output_data['distributor']['logic'] = dfx_distributor.address

    print(
        f'--- Deploying Distributor proxy contract to {connected_network} ---')
    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        addresses.DFX,
        gauge_controller.address,
        REWARDS_RATE,
        PREV_DISTRIBUTED_REWARDS,
        # needs another multisig to deal with access control behind proxy (ideally 2)
        GOVERNOR_MULTISIG,  # governor
        GUARDIAN_MULTISIG,  # guardian
        ZERO_ADDRESS   # delegate gauge for pulling type 2 gauge rewards
    )
    dfx_upgradable_proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        PROXY_MULTISIG,
        distributor_initializer_calldata,
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy},
        publish_source=should_verify,
    )
    output_data['distributor']['proxy'] = dfx_upgradable_proxy.address

    # Write output to file
    with open(f'./scripts/deployed_distributor_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)
