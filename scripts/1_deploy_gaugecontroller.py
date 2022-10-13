#!/usr/bin/env python
from brownie import ZERO_ADDRESS, GaugeController, VeBoostProxy
import eth_abi
import json
import time

from scripts.helper import get_addresses, network_info, gas_strategy, DEPLOY_ACCT

DEFAULT_GAUGE_TYPE_NAME = 'DFX AMM Liquidity'
DEFAULT_TYPE_WEIGHT = 1e18

addresses = get_addresses()
connected_network, _ = network_info()

output_data = {'veBoostProxy': None, 'veBoostProxyParams': None,
               'gaugeController': None, 'gaugeControllerParams': None}


def main():
    print((
        'Script 1 of 3:\n\n'
        'NOTE: This script expects configuration for:\n'
        '\t1. VotingEscrow (VeDFX) contract address'
    ))

    print(f'--- Deploying VeBoostProxy contract to {connected_network} ---')
    # (votingEscrow address, delegation address, admin address)
    ve_boost_proxy_params = eth_abi.encode_abi(['address', 'address', 'address'],
                                               (addresses.VOTE_ESCROW, ZERO_ADDRESS, DEPLOY_ACCT.address)).hex()
    ve_boost_proxy = VeBoostProxy.deploy(addresses.VOTE_ESCROW, ZERO_ADDRESS, DEPLOY_ACCT, {
        'from': DEPLOY_ACCT, 'gas_price': gas_strategy})
    time.sleep(3)
    output_data['veBoostProxy'] = ve_boost_proxy.address
    output_data['veBoostProxyParams'] = ve_boost_proxy_params

    print(
        f'--- Deploying Gauge Controller contract to {connected_network} ---')
    gauge_controller_params = eth_abi.encode_abi(['address', 'address', 'address'],
                                                 (addresses.DFX, addresses.VOTE_ESCROW, DEPLOY_ACCT.address)).hex()
    gauge_controller = GaugeController.deploy(
        addresses.DFX, addresses.VOTE_ESCROW, DEPLOY_ACCT, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})
    time.sleep(3)
    output_data['gaugeController'] = gauge_controller.address
    output_data['gaugeControllerParams'] = gauge_controller_params

    print(
        f'--- Configure Gauge Controller with "{DEFAULT_GAUGE_TYPE_NAME}" type on {connected_network} ---')
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME, DEFAULT_TYPE_WEIGHT, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})

    with open(f'./scripts/deployed_gaugecontroller_{int(time.time())}.json', 'w') as output_f:
        json.dump(output_data, output_f, indent=4)
