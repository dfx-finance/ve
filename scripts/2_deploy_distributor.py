#!/usr/bin/env python
import json
import time

from brownie import ZERO_ADDRESS, DfxDistributor, DfxUpgradeableProxy, accounts

from scripts import addresses, contracts
from scripts.helper import gas_strategy

REWARDS_RATE = 0
PREV_DISTRIBUTED_REWARDS = 0

DEPLOY_ACCT = accounts.load('hardhat')
PROXY_MULTISIG = accounts[7]
GOVERNOR_MULTISIG = DEPLOY_ACCT
GUARDIAN_MULTISIG = DEPLOY_ACCT

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

    gauge_controller = contracts.gauge_controller()

    print('--- Deploying Distributor contract to Ethereum mainnet ---')
    dfx_distributor = DfxDistributor.deploy(
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})
    output_data['distributor']['logic'] = dfx_distributor.address

    distributor_initializer_calldata = dfx_distributor.initialize.encode_input(
        addresses.DFX,
        gauge_controller.address,
        REWARDS_RATE,
        PREV_DISTRIBUTED_REWARDS,
        # needs another multisig to deal with access control behind proxy (ideally 2)
        GOVERNOR_MULTISIG,  # governor
        addresses.DFX_MULTISIG,  # guardian
        ZERO_ADDRESS   # delegate gauge for pulling type 2 gauge rewards
    )
    dfx_upgradable_proxy = DfxUpgradeableProxy.deploy(
        dfx_distributor.address,
        PROXY_MULTISIG,
        distributor_initializer_calldata,
        {'from': DEPLOY_ACCT, 'gas_price': gas_strategy},
    )
    output_data['distributor']['proxy'] = dfx_upgradable_proxy.address

    # Write output to file
    with open(f'./scripts/deployed_distributor_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)
