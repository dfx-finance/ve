#!/usr/bin/env python
import brownie
from brownie import ZERO_ADDRESS, DfxUpgradeableProxy, GaugeControllerUpgradeable, VeBoostProxy, accounts
from brownie.network import gas_price
import json
import time

from scripts import addresses
from scripts.helper import gas_strategy

DEFAULT_GAUGE_TYPE_NAME = 'DFX AMM Liquidity'
DEPLOYED_GAUGE_ADDRESSES = [
    ('CADC_USDC', None),
    ('EUROC_USDC', None),
    ('EURS_USDC', None),
    ('NZDS_USDC', None),
    ('TRYB_USDC', None),
    ('XIDR_USDC', None),
    ('XSGD_USDC', None),
]
DEFAULT_TYPE_WEIGHT = 1e18

gas_price(gas_strategy)

output_data = {'veBoostProxy': None,
               'gaugeController': {'logic': None, 'proxy': None}}


def main():
    print((
        'Script 1 of 3:\n\n'
        'NOTE: This script expects configuration for:\n'
        '\t1. VotingEscrow (VeDFX) contract address'
    ))

    acct = accounts.load('hardhat')
    fake_multisig = accounts[1]

    print('--- Deploying VeBoostProxy contract to Ethereum mainnet ---')
    # (votingEscrow address, delegation address, admin address)
    ve_boost_proxy = VeBoostProxy.deploy(addresses.VOTE_ESCROW, ZERO_ADDRESS, acct, {
        'from': acct, 'gas_price': gas_strategy})
    output_data['veBoostProxy'] = ve_boost_proxy.address

    print('--- Deploying Gauge Controller contract to Ethereum mainnet ---')
    gauge_controller_logic = GaugeControllerUpgradeable.deploy(
        {'from': acct, 'gas_price': gas_strategy})
    output_data['gaugeController']['logic'] = gauge_controller_logic.address

    gauge_controller_initializer_calldata = gauge_controller_logic.initialize.encode_input(
        addresses.DFX, addresses.VOTE_ESCROW, acct)
    gauge_controller_proxy = DfxUpgradeableProxy.deploy(
        gauge_controller_logic.address,
        fake_multisig,
        gauge_controller_initializer_calldata,
        {'from': acct, 'gas_price': gas_strategy},
    )
    output_data['gaugeController']['proxy'] = gauge_controller_proxy.address

    print('--- Configure Gauge Controller with "Liquidity" type ---')
    gauge_controller = brownie.interface.IGaugeController(
        gauge_controller_proxy.address)
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME, DEFAULT_TYPE_WEIGHT, {'from': acct, 'gas_price': gas_strategy})

    with open(f'./scripts/deployed_gaugecontroller_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)
