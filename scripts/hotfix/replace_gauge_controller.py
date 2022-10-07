#!/usr/bin/env python
# 1. Deploy new GaugeController
# 2. Add all existing gauges to GaugeController
# 3. Update Distributor with new GaugeController address
# 4. Update frontend with new GaugeController address
import brownie
from brownie import accounts, GaugeController
from brownie.network import gas_price
import eth_abi
import json
import time

from scripts.helper import gas_strategy, get_addresses, network_info

DEFAULT_GAUGE_TYPE_NAME = 'DFX AMM Liquidity'
DEFAULT_TYPE_WEIGHT = 1e18
DEPLOY_ACCT = accounts.load('deployve')
DEFAULT_GAUGE_TYPE = 0
DEFAULT_GAUGE_WEIGHT = 1e18

GAUGE_ADDRESSES = [
    ('CADC_USDC',  '0x277F25705a64DDc8742B226Fc2f4E3C89D05FB28'),
    ('EURS_USDC',  '0xd41151813A14fF820C08b2E34E0198F052433CD3'),
    ('NZDS_USDC',  '0x543512F918Ad73d917197CF6Cd3Bfae0d249d1f4'),
    ('TRYB_USDC',  '0xCFF53d673bcE50F4439Faf9e4A8a4a03e521EEAF'),
    ('XSGD_USDC',  '0x156dbdD94F5385c51c3c987d633fE0696433D53B'),
]
DFX_DISTRIBUTOR_ADDRESS = '0x6d5c46C6adccAcC67D518957a6a37362A4AB6565'
GAUGE_CONTROLLER_ADDRESS = '0xcf298E99FE4c593cd56F55622e6174abC5736228'

addresses = get_addresses()
connected_network, _ = network_info()
gas_price(gas_strategy)

output_data = {'replacementGaugeController': None,
               'replacementGaugeControllerParams': None}


def main():
    dfx_distributor = brownie.interface.IDfxDistributor(
        DFX_DISTRIBUTOR_ADDRESS)
    # TOGGLE: Only required when running the script step-by-step
    gauge_controller = brownie.interface.IGaugeController(
        GAUGE_CONTROLLER_ADDRESS)

    # 1. Deploy new GaugeController
    print(
        f'--- Deploying Gauge Controller contract to {connected_network} ---')
    gauge_controller_params = eth_abi.encode_abi(['address', 'address', 'address'],
                                                 (addresses.DFX, addresses.VOTE_ESCROW, DEPLOY_ACCT.address)).hex()
    gauge_controller = GaugeController.deploy(
        addresses.DFX, addresses.VOTE_ESCROW, DEPLOY_ACCT, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})
    time.sleep(3)
    output_data['replacementGaugeController'] = gauge_controller.address
    output_data['replacementGaugeControllerParams'] = gauge_controller_params

    print(
        f'--- Configure Gauge Controller with "Liquidity" type on {connected_network} ---')
    gauge_controller.add_type(
        DEFAULT_GAUGE_TYPE_NAME, DEFAULT_TYPE_WEIGHT, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})

    # 2. Add all existing gauges to GaugeController
    for _, gauge_addr in GAUGE_ADDRESSES:
        print('--- Add gauge to GaugeController ---')
        gauge_controller.add_gauge(
            gauge_addr, DEFAULT_GAUGE_TYPE, DEFAULT_GAUGE_WEIGHT, {'from': DEPLOY_ACCT, 'gas_price': gas_strategy})

    # 3. Update Distributor with new GaugeController address
    orig_controller_addr = dfx_distributor.controller()
    dfx_distributor.setGaugeController(gauge_controller.address, {
                                       'from': DEPLOY_ACCT, 'gas_price': gas_strategy})
    time.sleep(3)
    new_controller_addr = dfx_distributor.controller()
    print(f'Old Gauge Controller: {orig_controller_addr}')
    print(f'New Gauge Controller: {new_controller_addr}')

    # with open(f'./scripts/redeployed_gaugecontroller_{int(time.time())}.json', 'w') as output_f:
    #     json.dump(output_data, output_f, indent=4)


if __name__ == '__main__':
    pass
