#!/usr/bin/env python
import json
import os

from brownie import ZERO_ADDRESS, GaugeController, VeBoostProxy, accounts
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
import time

import scripts.addresses as addresses

USE_LATEST_JSON = True
DEFAULT_GAUGE_TYPE_NAME = 'Liquidity'
DEPLOYED_GAUGE_ADDRESSES = [
    ('CADC_USDC', None),
    ('EURS_USDC', None),
    ('XSGD_USDC', None),
    ('NZDS_USDC', None),
    ('TRYB_USDC', None),
    ('XIDR_USDC', None),
]
# Type 0 for Ethereum stableswap pools (https://curve.readthedocs.io/dao-gauges.html#gauge-types)
DEFAULT_GAUGE_WEIGHT = 0

gas_strategy = LinearScalingStrategy('60 gwei', '150 gwei', 1.3)
gas_price(gas_strategy)


output_data = {'veBoostProxy': None, 'gaugeController': None}


def main():
    print((
        'Script 1 of 3:\n\n'
        'NOTE: This script expects configuration for:\n'
        '\t1. VotingEscrow (VeDFX) contract address'
    ))

    acct = accounts.load('anvil')

    print('--- Deploying VeBoostProxy contract to Ethereum mainnet ---')
    # (votingEscrow address, delegation address, admin address)
    ve_boost_proxy = VeBoostProxy.deploy(addresses.VOTE_ESCROW, ZERO_ADDRESS, acct, {
        'from': acct, 'gas_price': gas_strategy})
    output_data['veBoostProxy'] = ve_boost_proxy.address

    print('--- Deploying Gauge Controller contract to Ethereum mainnet ---')
    gauge_controller = GaugeController.deploy(
        addresses.DFX, addresses.VOTE_ESCROW, acct, {'from': acct, 'gas_price': gas_strategy})

    print('--- Configure Gauge Controller with "Liquidity" type ---')
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME, DEFAULT_GAUGE_WEIGHT, {'from': acct, 'gas_price': gas_strategy})

    output_data['gaugeController'] = gauge_controller.address
    with open(f'./scripts/deployed_gaugecontroller_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)
